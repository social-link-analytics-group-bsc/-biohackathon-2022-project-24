#!/bin/bash  
#SBATCH --job-name="biohack_inference_BERT_model"  
#SBATCH -D .  
#SBATCH --output=slurm_logs/%j.out  
#SBATCH --error=slurm_logs/%j.err  
#SBATCH --gres=gpu:2
#SBATCH -c 2
#SBATCH --nodes=1  
#SBATCH --time=2-00:00:00  

source ./marenostrum_installation/mn_use_venv_amd_cp39.sh 

SCRIPT_DIR="../pipeline/"

cd $SCRIPT_DIR

python inference_BERT_model.py --model ./second_model/
