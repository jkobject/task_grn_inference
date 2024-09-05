#!/bin/bash

# RUN_ID="run_$(date +%Y-%m-%d_%H-%M-%S)"
reg_type=${1} #GB, ridge

RUN_ID="grn_evaluation_${reg_type}"
resources_dir="s3://openproblems-data/resources/grn"
# resources_dir="./resources"
publish_dir="${resources_dir}/results/${RUN_ID}"
grn_models_folder="${resources_dir}/grn_models"

subsample=-2
max_workers=10

param_file="./params/${RUN_ID}_figr.yaml"

# grn_names=(
#     "collectri"
#     "celloracle"
#     "scenicplus"
#     "figr"
#     "granie"
#     "scglue"
# )

grn_names=(
    "figr")
# Start writing to the YAML file
cat > $param_file << HERE
param_list:
HERE

append_entry() {
  cat >> $param_file << HERE
  - id: ${reg_type}_${1}_${3}
    perturbation_data: ${resources_dir}/grn-benchmark/perturbation_data.h5ad
    reg_type: $reg_type
    method_id: $1
    subsample: $subsample
    max_workers: $max_workers
    tf_all: ${resources_dir}/prior/tf_all.csv
    layer: ${3}
    consensus: ${resources_dir}/prior/consensus-num-regulators.json
HERE

  # Conditionally append the prediction line if the second argument is "true"
  if [[ $2 == "true" ]]; then
    cat >> $param_file << HERE
    prediction: ${grn_models_folder}/$1.csv
HERE
  fi
}
layers=(scgen_pearson)
# Loop through grn_names and layers
for layer in "${layers[@]}"; do
  for grn_name in "${grn_names[@]}"; do
    append_entry "$grn_name" "true" "$layer"
  done
done

# # Append negative control
# grn_name="negative_control"
# for layer in "${layers[@]}"; do
#   append_entry "$grn_name" "false" "$layer"
# done


# # Append positive controls
# grn_name="positive_control"
# for layer in "${layers[@]}"; do
#   append_entry "$grn_name" "false" "$layer"
# done


# Append the remaining output_state and publish_dir to the YAML file
cat >> $param_file << HERE
output_state: "state.yaml"
publish_dir: "$publish_dir"
HERE

nextflow run . \
  -main-script  target/nextflow/workflows/run_grn_evaluation/main.nf \
  -profile docker \
  -with-trace \
  -c src/common/nextflow_helpers/labels_ci.config \
  -params-file ${param_file}

# ./tw-windows-x86_64.exe launch `
#     https://github.com/openproblems-bio/task_grn_benchmark.git `
#     --revision build/main `
#     --pull-latest `
#     --main-script target/nextflow/workflows/run_grn_evaluation/main.nf `
#     --workspace 53907369739130 `
#     --compute-env 6TeIFgV5OY4pJCk8I0bfOh `
#     --params-file ./params/scgen_pearson_gb_pcs.yaml `
#     --config src/common/nextflow_helpers/labels_tw.config


