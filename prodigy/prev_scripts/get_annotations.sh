#!/bin/bash

source /home/destrada/tools/prodigy/venv/bin/activate
folder=final_annotations
file=$folder/final_annotations_16_07_2024.jsonl
touch $file

# I messed up and ran "prodigy drop bhg_0_1".
# I had previously saved the data in the following file, which I will add.
# annotations_0_1_new.jsonl (now fed into Annotator0) only contains the 78 that had not been annotated.
cat $folder/final_annotations_0_1.jsonl >> $file

# Save all annotations in file
for n in {0..3}; do
	prodigy db_out bhg_${n}_1 >> $file  
	prodigy db_out bhg_${n}_2 >> $file  
done

echo "annotations saved in $file."
echo "file contains $(cat $file | wc -l) annotations"
