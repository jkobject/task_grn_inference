# A dynamic benchmark for gene regulatory network (GRN) inference

The full documentation is hosted on [ReadTheDocs](https://openproblems-grn-task.readthedocs.io/en/latest/index.html). [![Documentation Status](https://readthedocs.org/projects/grn-inference-benchmarking/badge/?version=latest)](https://grn-inference-benchmarking.readthedocs.io/en/latest/?badge=latest)

<!--
This file is automatically generated from the tasks's api/*.yaml files.
Do not edit this file directly.
-->

Benchmarking GRN inference methods

Path to source:
[`src`](https://github.com/openproblems-bio/task_grn_benchmark/tree/main/src)

## README

## Installation

You need to have Docker, Java, and Viash installed. Follow [these
instructions](https://openproblems.bio/documentation/fundamentals/requirements)
to install the required dependencies.

## Download resources

``` bash
git clone git@github.com:openproblems-bio/task_grn_benchmark.git

cd task_grn_benchmark

# download resources
scripts/download_resources.sh
```

## Infer a GRN

``` bash
viash run src/methods/dummy/config.vsh.yaml -- --multiomics_rna resources/grn-benchmark/multiomics_rna.h5ad --multiomics_atac resources/grn-benchmark/multiomics_atac.h5ad --prediction output/dummy.csv
```

Similarly, run the command for other methods.

## Evaluate a GRN

``` bash
scripts/run_evaluation.sh --grn resources/grn-benchmark/grn_models/collectri.csv 
```

Similarly, run the command for other GRN models.

## Add a method

To add a method to the repository, follow the instructions in the
`scripts/add_a_method.sh` script.

## Motivation

GRNs are essential for understanding cellular identity and behavior.
They are simplified models of gene expression regulated by complex
processes involving multiple layers of control, from transcription to
post-transcriptional modifications, incorporating various regulatory
elements and non-coding RNAs. Gene transcription is controlled by a
regulatory complex that includes transcription factors (TFs),
cis-regulatory elements (CREs) like promoters and enhancers, and
essential co-factors. High-throughput datasets, covering thousands of
genes, facilitate the use of machine learning approaches to decipher
GRNs. The advent of single-cell sequencing technologies, such as
scRNA-seq, has made it possible to infer GRNs from a single experiment
due to the abundance of samples. This allows researchers to infer
condition-specific GRNs, such as for different cell types or diseases,
and study potential regulatory factors associated with these conditions.
Combining chromatin accessibility data with gene expression measurements
has led to the development of enhancer-driven GRN (eGRN) inference
pipelines, which offer significantly improved accuracy over
single-modality methods.

## Description

Here, we present a dynamic benchmark platform for GRN inference. This
platform provides curated datasets for GRN inference and evaluation,
standardized evaluation protocols and metrics, computational
infrastructure, and a dynamically updated leaderboard to track
state-of-the-art methods. It runs novel GRNs in the cloud, offers
competition scores, and stores them for future comparisons, reflecting
new developments over time.

The platform supports the integration of new datasets and protocols.
When a new feature is added, previously evaluated GRNs are re-assessed,
and the leaderboard is updated accordingly. The aim is to evaluate both
the accuracy and completeness of inferred GRNs. It is designed for both
single-modality and multi-omics GRN inference. Ultimately, it is a
community-driven platform. So far, six eGRN inference methods have been
integrated: Scenic+, CellOracle, FigR, scGLUE, GRaNIE, and ANANSE.

Due to its flexible nature, the platform can incorporate various
benchmark datasets and evaluation methods, using either prior knowledge
or feature-based approaches. In the current version, due to the absence
of standardized prior knowledge, we use a feature-based approach to
benchmark GRNs. Our evaluation utilizes standardized datasets for GRN
inference and evaluation, employing multiple regression analysis
approaches to assess both accuracy and comprehensiveness.

## Authors & contributors

| name               | roles  |
|:-------------------|:-------|
| Jalil Nourisa      | author |
| Antoine Passemiers | author |
| Robrecht Cannoodt  | author |

## API

``` mermaid
flowchart LR
  file_perturbation_h5ad("perturbation")
  comp_control_method[/"Control Method"/]
  comp_metric[/"Label"/]
  file_prediction("GRN")
  file_score("Score")
  file_prior("prior data")
  file_multiomics_rna_h5ad("multiomics rna")
  comp_method[/"Method"/]
  file_multiomics_atac_h5ad("multiomics atac")
  file_perturbation_h5ad---comp_control_method
  file_perturbation_h5ad---comp_metric
  comp_control_method-->file_prediction
  comp_metric-->file_score
  file_prediction---comp_metric
  file_prior---comp_control_method
  file_multiomics_rna_h5ad---comp_method
  comp_method-->file_prediction
  file_multiomics_atac_h5ad---comp_method
```

## File format: perturbation

Perturbation dataset for benchmarking.

Example file: `resources/grn-benchmark/perturbation_data.h5ad`

Format:

<div class="small">

    AnnData object
     obs: 'cell_type', 'sm_name', 'donor_id', 'plate_name', 'row', 'well', 'cell_count'
     layers: 'n_counts', 'pearson', 'lognorm'

</div>

Slot description:

<div class="small">

| Slot | Type | Description |
|:---|:---|:---|
| `obs["cell_type"]` | `string` | The annotated cell type of each cell based on RNA expression. |
| `obs["sm_name"]` | `string` | The primary name for the (parent) compound (in a standardized representation) as chosen by LINCS. This is provided to map the data in this experiment to the LINCS Connectivity Map data. |
| `obs["donor_id"]` | `string` | Donor id. |
| `obs["plate_name"]` | `string` | Plate name 6 levels. |
| `obs["row"]` | `string` | Row name on the plate. |
| `obs["well"]` | `string` | Well name on the plate. |
| `obs["cell_count"]` | `string` | Number of single cells pseudobulked. |
| `layers["n_counts"]` | `double` | Pseudobulked values using mean approach. |
| `layers["pearson"]` | `double` | Normalized values using pearson residuals. |
| `layers["lognorm"]` | `double` | Normalized values using shifted logarithm . |

</div>

## Component type: Control Method

Path:
[`src/control_methods`](https://github.com/openproblems-bio/openproblems-v2/tree/main/src/control_methods)

A control method.

Arguments:

<div class="small">

| Name | Type | Description |
|:---|:---|:---|
| `--perturbation_data` | `file` | Perturbation dataset for benchmarking. |
| `--layer` | `string` | Which layer of pertubation data to use to find tf-gene relationships. Default: `lognorm`. |
| `--prior_data` | `file` | Prior data used for grn benchmark. |
| `--prediction` | `file` | (*Output*) GRN prediction. |

</div>

## Component type: Label

Path:
[`src/metrics`](https://github.com/openproblems-bio/openproblems-v2/tree/main/src/metrics)

A metric to evaluate the performance of the inferred GRN

Arguments:

<div class="small">

| Name | Type | Description |
|:---|:---|:---|
| `--perturbation_data` | `file` | Perturbation dataset for benchmarking. |
| `--prediction` | `file` | GRN prediction. |
| `--score` | `file` | (*Output*) File indicating the score of a metric. |
| `--reg_type` | `string` | (*Optional*) name of regretion to use. Default: `ridge`. |
| `--subsample` | `integer` | (*Optional*) number of samples randomly drawn from perturbation data. Default: `-1`. |

</div>

## File format: GRN

GRN prediction

Example file: `resources/grn-benchmark/collectri.csv`

Format:

<div class="small">

    Tabular data
     'source', 'target', 'weight'

</div>

Slot description:

<div class="small">

| Column   | Type     | Description           |
|:---------|:---------|:----------------------|
| `source` | `string` | Source of regulation. |
| `target` | `string` | Target of regulation. |
| `weight` | `float`  | Weight of regulation. |

</div>

## File format: Score

File indicating the score of a metric.

Example file: `resources/grn-benchmark/score.csv`

Format:

<div class="small">

    Tabular data
     'accuracy', 'completeness'

</div>

Slot description:

<div class="small">

| Column         | Type     | Description                    |
|:---------------|:---------|:-------------------------------|
| `accuracy`     | `string` | (*Optional*) some explanation. |
| `completeness` | `double` | (*Optional*) some explanation. |

</div>

## File format: prior data

Prior data used for grn benchmark

Example file: `resources/grn-benchmark/prior_data.h5ad`

Format:

<div class="small">

    AnnData object
     uns: 'tf_list'

</div>

Slot description:

<div class="small">

| Slot | Type | Description |
|:---|:---|:---|
| `uns["tf_list"]` | `list` | List of known tfs obtained from https://resources.aertslab.org/cistarget. |

</div>

## File format: multiomics rna

RNA expression for multiomics data.

Example file: `resources/grn-benchmark/multiomics_rna.h5ad`

Format:

<div class="small">

    AnnData object
     obs: 'cell_type', 'donor_id'

</div>

Slot description:

<div class="small">

| Slot | Type | Description |
|:---|:---|:---|
| `obs["cell_type"]` | `string` | The annotated cell type of each cell based on RNA expression. |
| `obs["donor_id"]` | `string` | Donor id. |

</div>

## Component type: Method

Path:
[`src/methods`](https://github.com/openproblems-bio/openproblems-v2/tree/main/src/methods)

A GRN inference method

Arguments:

<div class="small">

| Name                | Type   | Description                                 |
|:--------------------|:-------|:--------------------------------------------|
| `--multiomics_rna`  | `file` | RNA expression for multiomics data.         |
| `--multiomics_atac` | `file` | (*Optional*) Peak data for multiomics data. |
| `--prediction`      | `file` | (*Output*) GRN prediction.                  |

</div>

## File format: multiomics atac

Peak data for multiomics data.

Example file: `resources/grn-benchmark/multiomics_atac.h5ad`

Format:

<div class="small">

    AnnData object
     obs: 'cell_type', 'donor_id'

</div>

Slot description:

<div class="small">

| Slot | Type | Description |
|:---|:---|:---|
| `obs["cell_type"]` | `string` | The annotated cell type of each cell based on RNA expression. |
| `obs["donor_id"]` | `string` | Donor id. |

</div>

