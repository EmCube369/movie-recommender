import torch

print("=" * 70)
print("PYTORCH / CUDA CHECK")
print("=" * 70)

print("PyTorch version :", torch.__version__)
print("CUDA available  :", torch.cuda.is_available())

if torch.cuda.is_available():
    print("CUDA version    :", torch.version.cuda)
    print("GPU             :", torch.cuda.get_device_name(0))

    props = torch.cuda.get_device_properties(0)

    print(
        "GPU memory      :",
        f"{props.total_memory / (1024 ** 3):.2f} GB"
    )

    device = torch.device("cuda")
else:
    print("GPU not available to PyTorch.")
    device = torch.device("cpu")

print("Selected device :", device)