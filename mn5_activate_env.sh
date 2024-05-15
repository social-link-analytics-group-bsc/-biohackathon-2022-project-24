module purge && 
module load  mkl/2024.0 nvidia-hpc-sdk/23.11-cuda11.8 openblas/0.3.27-gcc cudnn/9.0.0-cuda11 tensorrt/10.0.0-cuda11 impi/2021.11 hdf5/1.14.1-2-gcc gcc/11.4.0 python/3.11.5-gcc nccl/2.19.4






module load pytorch






# module load cuda/12.1 &&
# module load python/3.11.5 &&
# module load nvidia-hpc-sdk/23.11-cuda11.8 cudnn/9.0.0-cuda11 tensorrt/10.0.0-cuda11 openblas/0.3.27-gcc &&
# module load impi hdf5/1.14.1-2-gcc  &&
# # To load pytorch
# module load nccl/2.19.4 &&
# module unload openmpi &&
# module load impi/2021.11 hdf5/1.14.1-2-gcc 
source ./venv_311/bin/activate
