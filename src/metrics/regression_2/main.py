from typing import Dict, List, Set, Tuple, Any, Union
import random
import json

import tqdm
import numpy as np
import lightgbm
import pandas as pd
import anndata as ad
from sklearn.preprocessing import LabelEncoder, RobustScaler, StandardScaler
from sklearn.model_selection import GroupKFold, LeaveOneGroupOut
from sklearn.linear_model import Ridge
from sklearn.metrics import r2_score, mean_squared_error
from util import verbose_print, process_links, verbose_tqdm


SEED = 0xCAFE
N_POINTS_TO_ESTIMATE_BACKGROUND = 20

def net_to_matrix(net, gene_names: np.ndarray, par: Dict[str, Any]) -> np.ndarray:
    gene_dict = {gene_name: i for i, gene_name in enumerate(gene_names)}
    if 'cell_type' in net.columns:
        verbose_print(par['verbose'], 'Taking mean of cell type specific grns', 3)
        net.drop(columns=['cell_type'], inplace=True)
        net = net.groupby(['source', 'target']).mean().reset_index()
    if par['apply_skeleton']: #apply skeleton
        print('Before filtering with skeleton:', net.shape)
        skeleton = pd.read_csv(par['skeleton'])
        skeleton['link'] = skeleton['source'].astype(str) + '_' + skeleton['target'].astype(str)
        skeleton = skeleton['link'].values.flatten()
        
        net['link'] = net['source'].astype(str) + '_' + net['target'].astype(str)
        net = net[net['link'].isin(skeleton)]
        print('After filtering with skeleton:', net.shape)
    # keep only top n links
    if net.shape[0] > par['max_n_links']:
        verbose_print(par['verbose'], f"Reducing number of links to {par['max_n_links']}", 3)
        net = process_links(net, par)
    # convert to matrix
    A = np.zeros((len(gene_names), len(gene_names)), dtype=float)
    for source, target, weight in zip(net['source'], net['target'], net['weight']):
        if (source not in gene_dict) or (target not in gene_dict):
            continue
        i = gene_dict[source]
        j = gene_dict[target]
        A[i, j] = float(weight)
    return A


def fill_zeros_in_grn(A: np.ndarray, eps: float = 1e-10) -> np.ndarray:
    A = np.copy(A)
    A[A > 0] = A[A > 0] + eps
    A[A < 0] = A[A < 0] - eps
    A[A == 0] = np.random.rand(*A[A == 0].shape) * 2 * eps - eps
    A += np.random.rand(*A.shape) * eps
    return A


def cross_validate_gene(
        reg_type: str,
        X: np.ndarray,
        groups: np.ndarray,
        grn: np.ndarray,
        j: int,
        n_features: int = 10,
        random_state: int = 0xCAFE,
        n_jobs: int = 10
) -> Dict[str, float]:
    
    results = {'r2': 0.0, 'avg-r2': 0.0}
    
    if n_features == 0:
        return results
    
    # Feature selection
    regulatory_importance = np.abs(grn[:, j])
    regulatory_importance[j] = -1
    selected_features = np.argsort(regulatory_importance)[-n_features:]
    selected_features = selected_features[regulatory_importance[selected_features] > 0]
    if len(selected_features) == 0:
        return results
    assert j not in selected_features
    X_ = X[:, selected_features]

    # Define labels
    y_ = X[:, j]

    y_pred, y_target, r2s, models = [], [], [], []
    for t, (train_index, test_index) in enumerate(LeaveOneGroupOut().split(X_, y_, groups)):

        if reg_type == 'ridge':
            model = Ridge(random_state=random_state)
        elif reg_type == 'GB':
            model = lightgbm.LGBMRegressor(verbosity=-1, n_estimators=100, n_jobs=n_jobs, random_state=random_state)
        elif reg_type == 'RF':
            model = lightgbm.LGBMRegressor(boosting_type='rf', feature_fraction=0.05, verbosity=-1, n_estimators=100, n_jobs=n_jobs, random_state=random_state)
        else:
            raise NotImplementedError(f'Unknown model "{reg_type}"')

        X_train = X_[train_index, :]
        X_test = X_[test_index, :]
        y_train = y_[train_index]
        y_test = y_[test_index]
        
        model.fit(X_train, y_train)

        y_pred.append(model.predict(X_test))
        y_target.append(y_test)
        r2s.append(r2_score(y_target[-1], y_pred[-1]))
        models.append(model)

    y_pred = np.concatenate(y_pred, axis=0)
    y_target = np.concatenate(y_target, axis=0)
    
    results['r2'] = float(np.clip(r2_score(y_target, y_pred), 0, 1))
    results['avg-r2'] = float(np.clip(np.mean(r2s), 0, 1))
    results['models'] = models
    
    return results


# def learn_background_distribution(
#         reg_type: str,
#         X: np.ndarray,
#         groups: np.ndarray,
#         max_n_regulators: int,

# ) -> Dict[int, Tuple[float, float]]:

#     rng = np.random.default_rng(seed=SEED)

#     n_genes = X.shape[1]
#     random_grn = rng.random(size=(n_genes, n_genes))

#     background = {}
#     for n_features in tqdm.tqdm(range(1, max_n_regulators + 1), desc='Estimating background dist'):
#         scores = []
#         for _ in range(N_POINTS_TO_ESTIMATE_BACKGROUND):
#             j = rng.integers(low=0, high=n_genes)
#             random_grn[:, j] = rng.random(size=n_genes)

#             if n_features > 0:
#                 res = cross_validate_gene(
#                     reg_type,
#                     X,
#                     groups,
#                     random_grn,
#                     j,
#                     n_features=n_features,
#                     random_state=SEED,
#                     n_jobs=n_jobs
#                 )
#                 scores.append(res['avg-r2'])
#         background[n_features] = (np.mean(scores), max(0.001, np.std(scores)))
#     background['max'] = background[max_n_regulators]
#     return background


def cross_validate(
        reg_type: str,
        gene_names: np.ndarray,
        tf_names: Set[str],
        X: np.ndarray,
        groups: np.ndarray,
        grn: np.ndarray,
        n_features: np.ndarray,
        n_jobs: int
) -> List[Dict[str, float]]:
    n_genes = len(grn)

    grn = fill_zeros_in_grn(grn)

    # Remove interactions when first gene in pair is not in TF list
    for i, gene_name in tqdm.tqdm(enumerate(gene_names), desc=f'GRN preprocessing'):
        if gene_name not in tf_names:
            grn[i, :] = 0
    
    # Perform cross-validation for each gene
    results = []
    included_gene_names = []
    for j in tqdm.tqdm(range(n_genes), desc=f'{reg_type} CV'):
        if n_features[j] > 0:
            included_gene_names.append(gene_names[j])
            res = cross_validate_gene(reg_type, X, groups, grn, j, n_features=int(n_features[j]),n_jobs=n_jobs)
            results.append(res)
    return {
        'gene_names': list(included_gene_names),
        'results': list(results)
    }


# def dynamic_approach(
#         grn: np.ndarray,
#         X: np.ndarray,
#         groups: np.ndarray,
#         gene_names: List[str],
#         tf_names: Set[str],
#         reg_type: str
# ) -> float:

#     # Determine maximum number of input features
#     n_genes = X.shape[1]
#     max_n_regulators = min(100, int(0.5 * n_genes))

#     # Learn background distribution for each value of `n_features`:
#     # r2 scores using random genes as features.
#     background = learn_background_distribution(reg_type, X, groups, max_n_regulators)

#     # Cross-validate each gene using the inferred GRN to define select input features
#     res = cross_validate(
#         reg_type,
#         gene_names,
#         tf_names,
#         X,
#         groups,
#         grn,
#         np.clip(np.sum(grn != 0, axis=0), 0, max_n_regulators)
#     )

#     # Compute z-scores from r2 scores to take into account the fact
#     # that random network can still perform well when the number of features is large
#     scores = []
#     for j in range(n_genes):
#         if np.isnan(res['scores'][j]['avg-r2']):
#             continue
#         n_features = int(np.sum(grn[:, j] != 0))
#         if n_features in background:
#             mu, sigma = background[n_features]
#         else:
#             mu, sigma = background['max']
#         z_score = (res['scores'][j]['avg-r2'] - mu) / sigma
#         z_score = max(0, z_score)
#         scores.append(z_score)

#     return np.mean(scores)


def static_approach(
        grn: np.ndarray,
        n_features: np.ndarray,
        X: np.ndarray,
        groups: np.ndarray,
        gene_names: List[str],
        tf_names: Set[str],
        reg_type: str,
        n_jobs:int
) -> float:

    # Cross-validate each gene using the inferred GRN to define select input features
    res = cross_validate(reg_type, gene_names, tf_names, X, groups, grn, n_features, n_jobs=n_jobs)
    
    r2_scores = np.asarray([res['results'][j]['avg-r2'] for j in range(len(res['results']))])
    mean_r2_scores = np.mean(r2_scores)

    return mean_r2_scores


def main(par: Dict[str, Any]) -> pd.DataFrame:
    # Set global seed for reproducibility purposes
    random_state = SEED
    np.random.seed(random_state)
    random.seed(random_state)
    lightgbm.LGBMRegressor().set_params(random_state=random_state)

    verbose_print(par['verbose'], "Reading input files", 3)
    
    # Load perturbation data
    prturb_adata = ad.read_h5ad(par['evaluation_data'])
    gene_names = prturb_adata.var.index.to_numpy()
    n_genes = len(gene_names)
    
    net = ad.read_h5ad(par['prediction'])
    net = pd.DataFrame(net.uns['prediction'])
    net['weight'] = net['weight'].astype(float)
    assert net.shape[0]>0, 'No links found in the network'
    assert all(column in net.columns for column in ['source', 'target', 'weight']), 'Columns in the network should be source, target, weight'
    
    
   
    net_matrix = net_to_matrix(net, gene_names, par)

    n_cells = prturb_adata.shape[0]
    random_groups = np.random.choice(range(1, 5+1), size=n_cells, replace=True) # random sampling
    groups = LabelEncoder().fit_transform(random_groups)

    # Load and standardize perturbation data
    layer = par['layer']
    if  layer=='X':
        X = prturb_adata.X
    else:
        X = prturb_adata.layers[layer]
    
    try:
        X = X.todense().A
    except:
        pass

    X = RobustScaler().fit_transform(X)

    # Load consensus numbers of putative regulators
    with open(par['regulators_consensus'], 'r') as f:
        data = json.load(f)
    
    # - make present genes consistent across all data
    # gene_names = np.intersect1d(gene_names, np.asarray(list(data.keys()), dtype=object))


    n_features_theta_min = np.asarray([data[gene_name]['0'] for gene_name in gene_names], dtype=int)
    n_features_theta_median = np.asarray([data[gene_name]['0.5'] for gene_name in gene_names], dtype=int)
    n_features_theta_max = np.asarray([data[gene_name]['1'] for gene_name in gene_names], dtype=int)

    # Load list of putative TFs
    tf_names = np.loadtxt(par['tf_all'], dtype=str)
    if par['apply_tf']==False:
        tf_names = gene_names

    # Evaluate GRN
    verbose_print(par['verbose'], f'Compute metrics for layer: {layer}', 3)
    verbose_print(par['verbose'], f'Static approach (theta=0):', 3)
    if (n_features_theta_min!=0).any()==False:
        score_static_min = np.nan
    else:
        score_static_min = static_approach(net_matrix, n_features_theta_min, X, groups, gene_names, tf_names, par['reg_type'], n_jobs=par['num_workers'])
    verbose_print(par['verbose'], f'Static approach (theta=0.5):', 3)
    score_static_median = static_approach(net_matrix, n_features_theta_median, X, groups, gene_names, tf_names, par['reg_type'], n_jobs=par['num_workers'])
    print(f'Static approach (theta=1):', flush=True)
    score_static_max = static_approach(net_matrix, n_features_theta_max, X, groups, gene_names, tf_names, par['reg_type'], n_jobs=par['num_workers'])

    results = {
        'r2-theta-0.0': [float(score_static_min)],
        'r2-theta-0.5': [float(score_static_median)],
        'r2-theta-1.0': [float(score_static_max)],
    }

    # # Add dynamic score
    # if not par['static_only']:
    #     score_dynamic = dynamic_approach(grn, X, groups, gene_names, tf_names, par['reg_type'])
    #     score_overall = score_dynamic + score_static_min + score_static_median + score_static_max
    #     results['dynamic'] = [float(score_dynamic)]
    #     results['Overall'] = [float(score_overall)]

    # Convert results to DataFrame
    df_results = pd.DataFrame(results)

    return df_results
