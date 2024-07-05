import os
import logging
import torch
import yaml
from accelerate import PartialState

logger = logging.getLogger(
    __name__
)  ## Supposed to be a global logger to work in concurrent.futures
logging.basicConfig(level=logging.INFO)


def load_config(config_path):
    with open(config_path, "r") as file:
        return yaml.safe_load(file)


def setup_model_path(config_all, config_model):
    model_outdir = config_all["llm_params"]["model_outdir"]
    model_name = config_model["inference"]["model_name"]
    return os.path.join(model_outdir, model_name)


def setup_adapter_path(model_path, adapter_quantization, adapter=False):
    if adapter:
        if adapter_quantization:
            adapter_path = f"{model_path}_lora_{adapter_quantization}"
            adapter_id = f"_lora_{adapter_quantization}"
        else:
            adapter_path = f"{model_path}_lora"
            adapter_id = "_lora"
    else:
        adapter_path = None
        adapter_id = ""
    return adapter_path, adapter_id


def print_cuda_state():
    """
    Print the device information
    """
    # Check cuda
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    logging.info(f"Using device: {device}")

    # Additional Info when using cuda
    if device.type == "cuda":
        for i in range(torch.cuda.device_count()):
            logging.info(torch.cuda.get_device_properties(i))
        logging.info(torch.cuda.get_device_name())
        logging.info("Memory Usage:")
        logging.info(
            f"Allocated: {round(torch.cuda.memory_allocated() / 1024**3, 1)} GB"
        )
        logging.info(f"Cached: {round(torch.cuda.memory_reserved() / 1024**3, 1)} GB")


if __name__ == "__main__":
    print_cuda_state()
    device_string = PartialState().process_index
    print(device_string)
