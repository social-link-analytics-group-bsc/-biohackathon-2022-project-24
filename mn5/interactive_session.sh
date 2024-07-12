module purge && 
module load  mkl/2024.0 nvidia-hpc-sdk/23.11-cuda11.8 openblas/0.3.27-gcc cudnn/9.0.0-cuda11 tensorrt/10.0.0-cuda11 impi/2021.11 hdf5/1.14.1-2-gcc gcc/11.4.0 python/3.11.5-gcc nccl/2.19.4 pytorch  ncurses tmux &&
cd /gpfs/projects/bsc02/sla_projects/biohack-2022/

# source ./venv_311/bin/activate

# -d says not to attach to the session yet. top runs in the first
# window
tmux new-session -d 
# In the most recently created session, split the (only) window
# and run htop in the new pane
tmux split-window -h watch nvidia-smi
# Split the new pane and run perl
tmux split-pane -v htop 
tmux attach-session
