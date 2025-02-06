# GRN Inference


<!--
This file is automatically generated from the tasks's api/*.yaml files.
Do not edit this file directly.
-->

Benchmarking GRN inference methods

Repository:
[openproblems-bio/task_grn_inference](https://github.com/openproblems-bio/task_grn_inference)

## Description

geneRNIB is a living benchmark platform for GRN inference. This platform
provides curated datasets for GRN inference and evaluation, standardized
evaluation protocols and metrics, computational infrastructure, and a
dynamically updated leaderboard to track state-of-the-art methods. It
runs novel GRNs in the cloud, offers competition scores, and stores them
for future comparisons, reflecting new developments over time.

The platform supports the integration of new inference methods, datasets
and protocols. When a new feature is added, previously evaluated GRNs
are re-assessed, and the leaderboard is updated accordingly. The aim is
to evaluate both the accuracy and completeness of inferred GRNs. It is
designed for both single-modality and multi-omics GRN inference.

In the current version, geneRNIB contains 11 inference methods including
both single and multi-omics, 8 evalation metrics, and five datasets
(OPSCA, Nakatake, Norman, Adamson, and Replogle).

See our publication for the details of methods.

## Authors & contributors

| name              | roles       |
|:------------------|:------------|
| Jalil Nourisa     | author      |
| Robrecht Cannoodt | author      |
| Antoine Passimier | contributor |
| Marco Stock       | contributor |
| Christian Arnold  | contributor |

## API

``` mermaid
flowchart TB
  file_atac_h5ad("<a href='https://github.com/openproblems-bio/task_grn_inference#file-format-chromatin-accessibility-data'>chromatin accessibility data</a>")
  comp_method[/"<a href='https://github.com/openproblems-bio/task_grn_inference#component-type-method'>method</a>"/]
  file_prediction_h5ad("<a href='https://github.com/openproblems-bio/task_grn_inference#file-format-grn-prediction'>GRN prediction</a>")
  comp_metric_regression[/"<a href='https://github.com/openproblems-bio/task_grn_inference#component-type-feature-based-metrics'>Feature-based metrics</a>"/]
  comp_metric_ws[/"<a href='https://github.com/openproblems-bio/task_grn_inference#component-type-wasserstein-distance-metric'>Wasserstein distance metric</a>"/]
  comp_metric[/"<a href='https://github.com/openproblems-bio/task_grn_inference#component-type-metrics'>metrics</a>"/]
  file_score_h5ad("<a href='https://github.com/openproblems-bio/task_grn_inference#file-format-score'>score</a>")
  file_evaluation_h5ad("<a href='https://github.com/openproblems-bio/task_grn_inference#file-format-perturbation-data'>perturbation data</a>")
  file_rna_h5ad("<a href='https://github.com/openproblems-bio/task_grn_inference#file-format-gene-expression-data'>gene expression data</a>")
  file_atac_h5ad-.-comp_method
  comp_method-.->file_prediction_h5ad
  file_prediction_h5ad---comp_metric_regression
  file_prediction_h5ad---comp_metric_ws
  file_prediction_h5ad---comp_metric
  comp_metric_regression-->file_score_h5ad
  comp_metric_ws-->file_score_h5ad
  comp_metric-->file_score_h5ad
  file_evaluation_h5ad---comp_metric_regression
  file_rna_h5ad---comp_method
```

## File format: chromatin accessibility data

Chromatin accessibility data

Example file: `resources_test/grn_benchmark/inference_datasets//op_atac.h5ad`

Format:

<div class="small">

    AnnData object
     obs: 'cell_type', 'donor_id'

</div>

Data structure:

<div class="small">

| Slot | Type | Description |
|:---|:---|:---|
| `obs["cell_type"]` | `string` | (*Optional*) The annotated cell type of each cell based on RNA expression. |
| `obs["donor_id"]` | `string` | (*Optional*) Donor id. |

</div>

## Component type: method

A GRN inference method

Arguments:

<div class="small">

| Name | Type | Description |
|:---|:---|:---|
| `--rna` | `file` | RNA expression data. |
| `--atac` | `file` | (*Optional*) Chromatin accessibility data. |
| `--prediction` | `file` | (*Optional, Output*) File indicating the inferred GRN. |
| `--tf_all` | `file` | (*Optional*) NA. Default: `resources_test/grn_benchmark/prior/tf_all.csv`. |
| `--max_n_links` | `integer` | (*Optional*) NA. Default: `50000`. |
| `--num_workers` | `integer` | (*Optional*) NA. Default: `4`. |
| `--temp_dir` | `string` | (*Optional*) NA. Default: `output/temdir`. |
| `--seed` | `integer` | (*Optional*) NA. Default: `32`. |
| `--dataset_id` | `string` | (*Optional*) NA. Default: `op`. |
| `--method_id` | `string` | (*Optional*) NA. Default: `grnboost2`. |

</div>

## File format: GRN prediction

File indicating the inferred GRN.

Example file: `resources/grn_models/op/collectri.h5ad`

Format:

<div class="small">

    AnnData object
     uns: 'dataset_id', 'method_id', 'prediction'

</div>

Data structure:

<div class="small">

| Slot | Type | Description |
|:---|:---|:---|
| `uns["dataset_id"]` | `string` | A unique identifier for the dataset. |
| `uns["method_id"]` | `string` | A unique identifier for the inference method. |
| `uns["prediction"]` | `DataFrame` | Inferred GRNs in the format of source, target, weight. |

</div>

## Component type: Feature-based metrics

Calculates regression scores

Arguments:

<div class="small">

| Name | Type | Description |
|:---|:---|:---|
| `--prediction` | `file` | File indicating the inferred GRN. |
| `--score` | `file` | (*Output*) File indicating the score of a metric. |
| `--method_id` | `string` | (*Optional*) NA. |
| `--layer` | `string` | (*Optional*) NA. Default: `X_norm`. |
| `--max_n_links` | `integer` | (*Optional*) NA. Default: `50000`. |
| `--verbose` | `integer` | (*Optional*) NA. Default: `2`. |
| `--dataset_id` | `string` | (*Optional*) NA. Default: `op`. |
| `--evaluation_data` | `file` | Perturbation dataset for benchmarking. |
| `--tf_all` | `file` | NA. |
| `--reg_type` | `string` | (*Optional*) NA. Default: `ridge`. |
| `--subsample` | `integer` | (*Optional*) NA. Default: `-1`. |
| `--num_workers` | `integer` | (*Optional*) NA. Default: `4`. |
| `--apply_tf` | `boolean` | (*Optional*) NA. Default: `TRUE`. |
| `--apply_skeleton` | `boolean` | (*Optional*) NA. Default: `FALSE`. |

</div>

## Component type: Wasserstein distance metric

Calculates Wasserstein distance for a given GRN and dataset

Arguments:

<div class="small">

| Name | Type | Description |
|:---|:---|:---|
| `--prediction` | `file` | File indicating the inferred GRN. |
| `--score` | `file` | (*Output*) File indicating the score of a metric. |
| `--method_id` | `string` | (*Optional*) NA. |
| `--layer` | `string` | (*Optional*) NA. Default: `X_norm`. |
| `--max_n_links` | `integer` | (*Optional*) NA. Default: `50000`. |
| `--verbose` | `integer` | (*Optional*) NA. Default: `2`. |
| `--dataset_id` | `string` | (*Optional*) NA. Default: `op`. |
| `--ws_consensus` | `file` | NA. |
| `--ws_distance_background` | `file` | NA. |
| `--evaluation_data_sc` | `file_evaluation_h5ad.yaml` | NA. |

</div>

## Component type: metrics

A metric to evaluate the performance of the inferred GRN

Arguments:

<div class="small">

| Name | Type | Description |
|:---|:---|:---|
| `--prediction` | `file` | File indicating the inferred GRN. |
| `--score` | `file` | (*Output*) File indicating the score of a metric. |
| `--method_id` | `string` | (*Optional*) NA. |
| `--layer` | `string` | (*Optional*) NA. Default: `X_norm`. |
| `--max_n_links` | `integer` | (*Optional*) NA. Default: `50000`. |
| `--verbose` | `integer` | (*Optional*) NA. Default: `2`. |
| `--dataset_id` | `string` | (*Optional*) NA. Default: `op`. |

</div>

## File format: score

File indicating the score of a metric.

Example file: `resources_test/scores/score.h5ad`

Format:

<div class="small">

    AnnData object
     uns: 'dataset_id', 'method_id', 'metric_ids', 'metric_values'

</div>

Data structure:

<div class="small">

| Slot | Type | Description |
|:---|:---|:---|
| `uns["dataset_id"]` | `string` | A unique identifier for the dataset. |
| `uns["method_id"]` | `string` | A unique identifier for the method. |
| `uns["metric_ids"]` | `string` | One or more unique metric identifiers. |
| `uns["metric_values"]` | `double` | The metric values obtained for the given prediction. Must be of same length as ‘metric_ids’. |

</div>

## File format: perturbation data

Perturbation dataset for benchmarking.

Example file: `resources_test/grn_benchmark/evaluation_data//op.h5ad`

Format:

<div class="small">

    AnnData object
     obs: 'cell_type', 'perturbation', 'donor_id', 'perturbation_type'
     layers: 'X_norm'

</div>

Data structure:

<div class="small">

| Slot | Type | Description |
|:---|:---|:---|
| `obs["cell_type"]` | `string` | The annotated cell type of each cell based on RNA expression. |
| `obs["perturbation"]` | `string` | Name of the column containing perturbation names. |
| `obs["donor_id"]` | `string` | (*Optional*) Donor id. |
| `obs["perturbation_type"]` | `string` | (*Optional*) Name of the column indicating perturbation type. |
| `layers["X_norm"]` | `double` | Normalized values. |

</div>

## File format: gene expression data

RNA expression data.

Example file: `resources_test/grn_benchmark/inference_datasets//op_rna.h5ad`

Format:

<div class="small">

    AnnData object
     obs: 'cell_type', 'donor_id'
     layers: 'counts', 'X_norm'

</div>

Data structure:

<div class="small">

| Slot | Type | Description |
|:---|:---|:---|
| `obs["cell_type"]` | `string` | (*Optional*) The annotated cell type of each cell based on RNA expression. |
| `obs["donor_id"]` | `string` | (*Optional*) Donor id. |
| `layers["counts"]` | `double` | (*Optional*) Counts matrix. |
| `layers["X_norm"]` | `double` | Normalized values. |

</div>

