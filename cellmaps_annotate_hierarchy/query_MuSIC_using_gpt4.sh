#!/bin/bash -l
#SBATCH --output=./outfile/gpt_analysis.%A_%a.out
#SBATCH --error=./errfile/gpt_analysis.%A_%a.err
#SBATCH --job-name=llm_analysis
#SBATCH --partition="nrnb-compute" # replace with your partition name
#SBATCH --array=2-6%3 # change if run specific array task
#SBATCH --time=3:00:00
#SBATCH --mem=8G
#SBATCH --cpus-per-task=1

hostname
date
echo "My SLURM_ARRAY_TASK_ID: " $SLURM_ARRAY_TASK_ID


PARAMFILE=MuSIC_gpt_4_params.txt

PARAM=$(awk "NR==$SLURM_ARRAY_TASK_ID" $PARAMFILE)
echo $PARAM

source activate llm_eval
# run llm query
eval python query_llm_for_analysis.py $PARAM

date