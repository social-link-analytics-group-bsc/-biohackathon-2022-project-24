#!/bin/bash
#SBATCH --job-name="Sex Bias Model"
#SBATCH --chdir=./
#SBATCH --output=./logs/sts_%j.out
#SBATCH --error=./logs/sts_%j.err
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=10
#SBATCH --time=02:00:00
#SBATCH --qos=debug

timestamp()
{
 date +"%Y-%m-%d %T"
}

PYTHON_VERSION=3.10

#echo "$(timestamp) Model purging and loading"
module purge && module load cmake gcc intel mkl python/$PYTHON_VERSION.2

echo "$(timestamp) Activate environment"

source ../venv/bin/activate

SCRIPT_DIR="./pipeline/"

cd $SCRIPT_DIR

echo "$(timestamp) Running the job"
srun python$PYTHON_VERSION get_sex_bias.py --data ./data/methods_subset_5000_1207_tokenized.csv --out ./output/model_output.json --model ./second_model/

echo "$(timestamp) Job done!"