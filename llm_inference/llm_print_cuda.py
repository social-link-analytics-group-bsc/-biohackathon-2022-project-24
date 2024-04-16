import torch
from accelerate import PartialState


def _print_state(device):
    """
    Print the device information
    """
    # Check cuda
    print("Using device:", device)
    print()

    # Additional Info when using cuda
    if device.type == "cuda":
        for i in range(torch.cuda.device_count()):
            print(torch.cuda.get_device_properties(i))
        # print(torch.cuda.get_device_name())
        # print("Memory Usage:")
        # print("Allocated:", round(torch.cuda.memory_allocated() / 1024**3, 1), "GB")
        # print("Cached:   ", round(torch.cuda.memory_reserved() / 1024**3, 1), "GB")


if __name__ == "__main__":
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    _print_state(device)
    device_string = PartialState().process_index
    print(device_string)
