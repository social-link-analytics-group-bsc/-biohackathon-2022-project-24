PYTHON_VERSION=3.10
module purge && module load cmake gcc intel mkl python/$PYTHON_VERSION.2

echo 'Using Pythonv version' "$PYTHON_VERSION"

unset PYTHONPATH

echo 'Create virtual env' 
python$PYTHON_VERSION -m venv venv

echo 'activate venv'
source ./venv/bin/activate

echo 'Upgrading pip'
pip$PYTHON_VERSION install --upgrade pip
#/apps/PYTHON/$PYTHON_VERSION.2/INTEL/bin/python$PYTHON_VERSION -m pip install --upgrade pip

echo 'installing pip-tools'
pip$PYTHON_VERSION install pip-tools

echo 'Installing the requirements'

pip$PYTHON_VERSION install -r ../requirements.txt

