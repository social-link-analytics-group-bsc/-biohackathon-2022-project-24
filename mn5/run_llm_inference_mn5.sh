#!/bin/bash  
#SBATCH --job-name="biohack_inference_LLM_model" 
#SBATCH -D .  
#SBATCH --output=slurm_logs/%j.out  
#SBATCH --error=slurm_logs/%j.err  
#SBATCH --ntasks=1
#SBATCH --gres=gpu:2
#SBATCH -cpus-per-task=16
#SBATCH --time=2-00:00:00  

export SRUN_CPUS_PER_TASK=${SLURM_CPUS_PER_TASK}

source ./marenostrum_installation/mn5_use_venv.sh 

SCRIPT_DIR="./"

cd $SCRIPT_DIR

python ./llm_inference/llm_sex_count_extraction.py
