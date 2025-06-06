#!/bin/bash
# ws_distance: only three datasets [norman, adamson, replogle]
# scprint: only two datasets [opsca, replogle, norman] -> for reologle and scprint, the inference data is different
# scenicplus, scglue,  granie, figr, celloracle on [opsca]

test=false
RUN_ID="test_run"
# - settings
run_local=true
reg_type="ridge"
num_workers=10
apply_tf_methods=true
apply_skeleton=false
# - specify inputs
dataset_ids=" op " 
metric_ids="[regression_1, regression_2, ws_distance]" 
method_ids="[pearson_corr,
            negative_control, 
            positive_control, 

            portia, 
            ppcor, 
            scenic, 
            scprint, 
            grnboost2,

            scenicplus, 
            scglue,
            granie,
            figr,
            celloracle]"


if [ "$test" = true ]; then
  resources_folder='resources_test'
else
  resources_folder='resources'
fi
echo "Resources folder: $resources_folder"
label=${RUN_ID}
echo "Run ID: $RUN_ID"

resources_dir="s3://openproblems-data/${resources_folder}/grn"


publish_dir="${resources_dir}/results/${RUN_ID}"
echo "Publish dir: $publish_dir"
grn_models_folder="${resources_dir}/grn_models/"
grn_models_folder_local="./resources/grn_models/"


params_dir="./params"
param_file="${params_dir}/${RUN_ID}.yaml"
param_local="${params_dir}/${RUN_ID}_param_local.yaml"
param_aws="s3://openproblems-data/resources/grn/results/params/${RUN_ID}_param_local.yaml"

# Print GRN names correctly
echo $param_local
echo "GRN models: ${method_ids[@]}"

# Ensure param_file is clean
> "$param_local"
> "$param_file"

if [ "$run_local" = true ]; then
  cat >> "$param_local" << HERE
param_list:
HERE
fi

append_entry() {
  local dataset="$1"
  echo "Dataset: $dataset"
  cat >> "$param_local" << HERE
  - id: ${dataset}_${reg_type}
    metric_ids: $metric_ids
    method_ids: $method_ids
    rna: ${resources_dir}/grn_benchmark/inference_data/${dataset}_rna.h5ad
    rna_all: ${resources_dir}/extended_data/${dataset}_bulk.h5ad
    evaluation_data: ${resources_dir}/grn_benchmark/evaluation_data/${dataset}_bulk.h5ad
    tf_all: ${resources_dir}/grn_benchmark/prior/tf_all.csv
    regulators_consensus: ${resources_dir}/grn_benchmark/prior/regulators_consensus_${dataset}.json
    layer: 'X_norm'
    num_workers: $num_workers
    apply_tf_methods: $apply_tf_methods
    apply_skeleton: $apply_skeleton
    skeleton: ${resources_dir}/grn_benchmark/prior/skeleton.csv
    reg_type: $reg_type

HERE

  if [[ "$dataset" == "norman" || "$dataset" == "adamson" || "$dataset" == "replogle" ]]; then
    cat >> "$param_local" << HERE
    evaluation_data_sc: ${resources_dir}/grn_benchmark/evaluation_data/${dataset}_sc.h5ad
    ws_consensus: ${resources_dir}/grn_benchmark/prior/ws_consensus_${dataset}.csv
    ws_distance_background: ${resources_dir}/grn_benchmark/prior/ws_distance_background_${dataset}.csv
HERE
  fi
  if [[ "$dataset" == "op" ]]; then
    cat >> "$param_local" << HERE
    atac: ${resources_dir}/grn_benchmark/inference_data/${dataset}_atac.h5ad
HERE
  fi
}

# Iterate over datasets 
for dataset in $dataset_ids; do
  append_entry "$dataset"
done

# Append final fields
if [ "$run_local" = true ]; then
  cat >> "$param_local" << HERE
output_state: "state.yaml"
publish_dir: "$publish_dir"
HERE
  viash ns build --parallel 
  nextflow run . \
    -main-script  target/nextflow/workflows/run_benchmark/main.nf \
    -profile docker \
    -with-trace \
    -c common/nextflow_helpers/labels_ci.config \
    -params-file ${param_local}
  
else
  cat >> "$param_file" << HERE
output_state: "state.yaml"
publish_dir: "$publish_dir"
param_list: "$param_aws"
HERE
  echo "Parameter file created: $param_file"

  aws s3 cp $param_local $param_aws

  tw launch https://github.com/openproblems-bio/task_grn_inference \
    --revision build/main \
    --pull-latest \
    --main-script target/nextflow/workflows/run_benchmark/main.nf \
    --workspace 53907369739130 \
    --compute-env 7gRyww9YNGb0c6BUBtLhDP   \
    --params-file ${param_file} \
    --config common/nextflow_helpers/labels_tw.config \
    --labels ${label}
fi
#on demand 6TJs9kM1T7ot4DbUY2huLF   
#7gRyww9YNGb0c6BUBtLhDP
