# !pip install sctk anndata
# !aws s3 cp s3://openproblems-bio/public/neurips-2023-competition/sc_counts.h5ad  ./resources_raw/ --no-sign-request

import anndata as ad 
import pandas as pd
import numpy as np
import sys
from scipy.sparse import csr_matrix
import scanpy as sc
## VIASH START
par = {
    'op_perturbation_raw': 'resources/datasets_raw/op_perturbation_sc_counts.h5ad',
    'op_multiome': 'resources/datasets_raw/op_multiome_sc_counts.h5ad',
    
    'op_perturbation_bulk': 'resources/grn_benchmark/evaluation_data/op_bulk.h5ad',
    'op_rna': 'resources/grn_benchmark/inference_data/op_rna.h5ad',
    'op_atac': 'resources/grn_benchmark/inference_data/op_atac.h5ad',
    'op_rna_test': 'resources_test/grn_benchmark/inference_data/op_rna.h5ad',
    'op_atac_test': 'resources_test/grn_benchmark/inference_data/op_atac.h5ad',
    'op_perturbation_bulk_test': 'resources_test/grn_benchmark/evaluation_data/op_bulk.h5ad'
}
## VIASH END

try: 
    sys.path.append(meta['resources_dir'])
except:
    meta = { 
        'util_dir': 'src/utils/',
        'helper_dir': './'
    }   
    sys.path.append(meta['util_dir'])
    sys.path.append(meta['helper_dir'])


from util import sum_by
from helper import preprocess_sc, pseudobulk_mean_func, filter_func, normalize_func, add_metadata
from helper import shorten_evaluation_data, shorten_inference_data


def pseudobulk_sum_func(sc_counts):
    # pseudobulk
    #group cell types per well
    sc_counts.obs['plate_well_cell_type'] = sc_counts.obs['plate_name'].astype('str') \
        + '_' + sc_counts.obs['well'].astype('str') \
        + '_' + sc_counts.obs['cell_type'].astype('str')
    sc_counts.obs['plate_well_cell_type'] = sc_counts.obs['plate_well_cell_type'].astype('category')
    bulk_adata = sum_by(sc_counts, 'plate_well_cell_type')
    bulk_adata.obs['cell_count'] = sc_counts.obs.groupby('plate_well_cell_type').size().values
    bulk_adata.X = np.array(bulk_adata.X.todense())

    print('ratio of missingness' , (bulk_adata.X==0).sum()/bulk_adata.X.size)
    bulk_adata.var = bulk_adata.var.reset_index()
    bulk_adata.var.set_index('index', inplace=True)

    bulk_adata.X = np.nan_to_num(bulk_adata.X, nan=0)
    return bulk_adata

def main_perturbation(par):
    cell_counts_t = 10
        
    sc_counts_f = preprocess_sc(par)
    bulk_adata = pseudobulk_sum_func(sc_counts_f)
    bulk_adata = pseudobulk_mean_func(bulk_adata)
    bulk_adata = filter_func(bulk_adata, cell_counts_t)


    bulk_adata.obs = bulk_adata.obs.rename(columns={'sm_name':'perturbation'})

    bulk_adata = normalize_func(bulk_adata)

    del bulk_adata.layers['n_counts']

    bulk_adata.X = csr_matrix(bulk_adata.X)
    bulk_adata.layers['counts'] = csr_matrix(bulk_adata.layers['counts'])

    bulk_adata.obs['is_control'] = bulk_adata.obs['perturbation'].isin(['Dimethyl Sulfoxide'])
    bulk_adata.obs['is_positive_control'] = bulk_adata.obs['perturbation'].isin(['Dabrafenib', 'Belinostat'])

    bulk_adata = add_metadata(bulk_adata)
    bulk_adata.uns['normalization_id'] = 'apr'
    print('writing op_perturbation_bulk')
    print(bulk_adata)
    bulk_adata.write(par['op_perturbation_bulk'])
def main_multiome(par):
    multiomics = ad.read_h5ad(par['op_multiome'])
    multiomics.X = multiomics.layers['counts']
    del multiomics.layers
    multiomics.layers['counts'] = multiomics.X.copy()

    multiomics.var.index.name='location'
    multiomics.obs.index.name='obs_id'

    # map the cell types
    cell_types_o = multiomics.obs.cell_type.unique()
    T_cell_types = ['T regulatory cells', 'T cells CD8+', 'T cells CD4+']
    cell_type_map = {cell_type: 'T cells' if cell_type in T_cell_types else cell_type for cell_type in cell_types_o}
    multiomics.obs['cell_type'] = multiomics.obs['cell_type'].map(cell_type_map)
    # RNA
    rna = multiomics[:,multiomics.var.feature_types=='Gene Expression']
    rna.var = rna.var[['gene_ids', 'interval']]

    #------ ATAC
    atac = multiomics[:,multiomics.var.feature_types=='Peaks']
    atac.var = atac.var[[]]

    # Find common cells (observations) in both RNA and ATAC datasets
    common_obs = rna.obs_names.intersection(atac.obs_names)
    # Subset the RNA and ATAC data to keep only the common cells
    rna = rna[common_obs, :]
    atac = atac[common_obs, :]

    print(rna)
    print(atac)

    # change donor names
    unique_donors = rna.obs.donor_id.unique()
    donor_map = {donor_id: f'donor_{i}' for i, donor_id in enumerate(unique_donors)}
    rna.obs['donor_id'] = rna.obs['donor_id'].map(donor_map)
    atac.obs['donor_id'] = atac.obs['donor_id'].map(donor_map)

    # normalize rna 
    X_norm = sc.pp.normalize_total(rna, inplace=False)['X']
    rna.layers['X_norm'] = sc.pp.log1p(X_norm, copy=True)

    rna = add_metadata(rna)
    atac = add_metadata(atac)

    rna.uns['normalization_id'] = 'sla'
    atac.uns['normalization_id'] = 'sla'

    # - needed for some R packages
    annotation_peak = atac.var.reset_index().location.str.split(':', expand=True)
    atac.var['seqname'] = annotation_peak[0].values
    atac.var['ranges'] = annotation_peak[1].values
    atac.var['strand'] = '+'

    atac = atac[:, atac.var['seqname'].str.startswith('chr')]

    rna.write(par['op_rna'])
    atac.write(par['op_atac'])

def main_test_data(par):
    shorten_evaluation_data(par)
    shorten_inference_data(par)

if __name__ == '__main__':
    print('Processing perturbation data ...')
    main_perturbation(par)
    print('Processing multiome data ...')
    main_multiome(par)
    print('Processing test data ...')
    main_test_data(par)
    