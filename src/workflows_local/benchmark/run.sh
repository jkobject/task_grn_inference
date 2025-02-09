#!/bin/bash
#SBATCH --job-name=workflow_local
#SBATCH --output=logs/%j.out
#SBATCH --error=logs/%j.err
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=10
#SBATCH --time=10:00:00
#SBATCH --mem=1000GB
#SBATCH --partition=gpu
#SBATCH --gres=gpu:1
#SBATCH --mail-type=END,FAIL      
#SBATCH --mail-user=jalil.nourisa@gmail.com

set -e
source ~/miniconda3/bin/activate scprint

DATASETS=(
    "replogle"
)
# METHODS=(
#     "scprint"  "positive_control pearson_corr portia ppcor grnboost2 scenic "
# )

METHODS=(
    "scprint "
)

# - where to save the scores (all metrics, datasets, methods)
SAVE_SCORES_FILE="resources/scores/scores_scprint.csv"
# - whether to force re-run the inference if the files exists
FORCE=true
SBATCH=true
# - whether to run the consensus for reg2 (only run when to update the consensus)
RUN_CONSENSUS_FLAG=False

# ----- run methods -----
cmd="python src/workflows_local/benchmark/methods/script.py 
        --datasets ${DATASETS[@]} 
        --methods ${METHODS[@]}"

[ "$FORCE" = true ] && cmd="${cmd} --force"
[ "$SBATCH" = true ] && cmd="${cmd} --sbatch"

echo "Running: $cmd"
$cmd

if [ "$SBATCH" = false ]; then
    # ----- run metrics -----
    cmd="python src/workflows_local/benchmark/metrics/script.py 
            --datasets ${DATASETS[@]} 
            --methods ${METHODS[@]}
            --save_scores_file ${SAVE_SCORES_FILE}"

    [ "$RUN_CONSENSUS_FLAG" = true ] && cmd="${cmd} --run_consensus_flag"

    echo "Running: $cmd"
    $cmd
fi
