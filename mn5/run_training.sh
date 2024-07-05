#!/bin/bash  
#SBATCH --qos=acc_bscls
#SBATCH --job-name="biohack_peft_train" 
#SBATCH -D .  
#SBATCH --output=slurm_logs/%j.out  
#SBATCH --error=slurm_logs/%j.err  
#SBATCH --ntasks=1
#SBATCH --gres=gpu:4
#SBATCH --nodes=1
#SBATCH --time=00-08:00:00  

# export SRUN_CPUS_PER_TASK=${SLURM_CPUS_PER_TASK}


SCRIPT_DIR="./"

cd $SCRIPT_DIR

module purge && 
module load  mkl/2024.0 nvidia-hpc-sdk/23.11-cuda11.8 openblas/0.3.27-gcc cudnn/9.0.0-cuda11 tensorrt/10.0.0-cuda11 impi/2021.11 hdf5/1.14.1-2-gcc gcc/11.4.0 python/3.11.5-gcc nccl/2.19.4 pytorch &&
cd /gpfs/projects/bsc02/sla_projects/biohack-2022/

source ./venv_311/bin/activate
 accelerate launch --config_file ./config/fsdp_config_qlora.yaml llm_inference/run_fsdp_qlora.py --config config/llama_3_70b_fsdp_qlora.yaml

# export ACCELERATE_USE_FSDP=1
# export FSDP_CPU_RAM_EFFICIENT_LOADING=1
# torchrun --nproc_per_node=4 ./llm_inference/run_fsdp_qlora.py --config config/llama_3_70b_fsdp_qlora.yaml
