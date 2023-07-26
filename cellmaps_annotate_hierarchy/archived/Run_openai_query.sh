#!/bin/bash -l
#SBATCH --output=./outfile/Chatgpt.%A_%a.out
#SBATCH --error=./errfile/Chatgpt.%A_%a.err
#SBATCH --job-name=run_chatgpt
#SBATCH --partition="nrnb-compute"
#SBATCH --array=1
#SBATCH --time=3:00:00
#SBATCH --mem=8G
#SBATCH --cpus-per-task=1
hostname
date
echo "My SLURM_ARRAY_TASK_ID: " $SLURM_ARRAY_TASK_ID

PARAMFILE= /cellar/users/mhu/Projects/cellmaps_annotate_hierarchy/cellmaps_annotate_hierarchy/MuSIC2_Maps/051523_MuSIC2_branch1-2.params
PARAM=$(awk "NR==$SLURM_ARRAY_TASK_ID" $PARAMFILE)
echo $PARAM

source activate llm

python -u /cellar/users/mhu/Projects/cellmaps_annotate_hierarchy/cellmaps_annotate_hierarchy/openai_query.py $PARAM

date
