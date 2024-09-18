# Running llm inference on Marenostrum

## Preparing on the Marenostrum
### Loading Modules
```bash
module purge &&
module load  mkl/2024.0 nvidia-hpc-sdk/23.11-cuda11.8 openblas/0.3.27-gcc cudnn/9.0.0-cuda11 tensorrt/10.0.0-cuda11 impi/2021.11 hdf5/1.14.1-2-gcc gcc/11.4.0 python/3.11.5-gcc nccl/2.19.4 pytorch
module unload pytorch/2.4.0 
```
### Activate environment

```bash
python -m venv venv
source venv_test/bin/activate

pip install -U -r requirements.txt

pip install sympy --ignore-installed
```

### Downloading the model

```bash
cd llm_models/
huggingface-cli download mistralai/Mistral-7B-Instruct-v0.3 --local-dir ./mixtral_8x7b_instruct_v03 --cache-dir ./cache 
```

### Dataset preparation


## Running the script

### Evaluation
This script, llm_evaluate_models.py, is designed to evaluate a language model using various parameters such as quantization, instruct modes, and adapter support. 
The script allows for flexible evaluation by accepting a range of command-line arguments.

#### Usage
To run the evaluation script, use the following basic command:

```bash
    python llm_evaluate_models.py --model <model_name_or_path> --prompt <prompt_file_path> --training_set <training_set_path> [options]
```
##### Command-Line Arguments

Here are the available command-line arguments for running the script:

--model (required): The path to the model or the name of the model if it can be downloaded from a model hub.

--quantization (optional): Specifies the quantization level for the model, if applicable.

--instruct (optional): A flag indicating whether the model is an instruct model. Use this flag if the model supports instruction-based prompting.

--adapter (optional): A flag to indicate whether an adapter should be loaded for the model.

--adapter_quantization (optional): Specifies if the adapter is quantized. Defaults to False.

--prompt (required): The path to the prompt file that contains the input prompts for the model.

--full_eval (optional): A flag to indicate whether to run the evaluation on the entire dataset, without splitting.

--training_set (required): The path to the training dataset for evaluation.

#### Example Commands

1. Basic Usage:

```bash

python llm_evaluate_models.py --model my_model --prompt data/prompts.txt --training_set data/training_data.csv
```

1. Using Instruct Mode:

```bash

python llm_evaluate_models.py --model my_instruct_model --prompt data/prompts.txt --training_set data/training_data.csv --instruct
```

1. With Quantization and Adapter:

```bash

python llm_evaluate_models.py --model my_model --prompt data/prompts.txt --training_set data/training_data.csv --quantization 8bit --adapter --adapter_quantization 4bit
```

1. Full Dataset Evaluation:

```bash
    python llm_evaluate_models.py --model my_model --prompt data/prompts.txt --training_set data/training_data.csv --full_eval
```
