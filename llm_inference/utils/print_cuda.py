import logging
import torch
from accelerate import PartialState

logger = logging.getLogger(
    __name__
)  ## Supposed to be a global logger to work in concurrent.futures
logging.basicConfig(level=logging.INFO)

def print_state():
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
        logging.info(f"Allocated: {round(torch.cuda.memory_allocated() / 1024**3, 1)} GB")
        logging.info(f"Cached: {round(torch.cuda.memory_reserved() / 1024**3, 1)} GB")


if __name__ == "__main__":
    print_state()
    device_string = PartialState().process_index
    print(device_string)
