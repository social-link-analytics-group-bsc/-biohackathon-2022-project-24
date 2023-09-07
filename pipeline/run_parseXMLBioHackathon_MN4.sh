#!/bin/bash
#SBATCH --job-name=BH22_pipeline      # Job name
#SBATCH --mail-type=BEGIN,END,FAIL            # Mail events (NONE, BEGIN, END, FAIL, ALL)
#SBATCH --cpus-per-task=4               # Number of cores per MPI rank 
#SBATCH --nodes=1                      # Number of nodes
#SBATCH --time=10:00:00                 # Time limit hrs:min:sec
#SBATCH --output=serial_test_run_new_pipeline.log   # Standard output and error log

module load python/3.9.10
# python3 parseXMLPubMed.py -d ../retrieveMetadataPubMed/tmp_database.db -i /gpfs/projects/bsc08/shared_projects/BioHackathon2022/pubmed

python3 ./utils/parseXMLBioHackaton.py -d ../retrieveMetadataPubMed/tmp_db_2.db -i ./data/pmcid_humans_5000_290623.txt