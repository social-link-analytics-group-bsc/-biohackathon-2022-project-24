#!/bin/bash
# Get 50 annotations not present in the previous annotation data for 3 people to evaluate and see if they get the same results

# I will use the middle part of the annotations_00, 01 & 02, unused:

folder="../original_annotations"
output=group_annotation.jsonl

> $output
for n in {0..2}; do
	filepath=$folder/annotations_0$n.jsonl
	head -n 140 $filepath | tail -20 >> $output
done
echo "Json file with $(cat $output | wc -l) lines saved in $output"

