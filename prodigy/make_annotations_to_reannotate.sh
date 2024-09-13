#!/bin/bash
# Script to get the annotations to reannotate, after the reannotation rules changed at the start of july

# Annotations before and after the new reannotation rules
folder="../final_annotations"
new_annots="$folder/final_annotations_16_07_2024.jsonl"
prev_annots="$folder/final_annotations_03_06_2024.jsonl"

# Get stats
n_prev_annots=$(cat $prev_annots | wc -l)
echo "# Annotations before new rules: $n_prev_annots"
echo "# Annotations after new rules:  $(cat $new_annots | wc -l)"

echo "We will re-annotate the $(cat $prev_annots | wc -l) previous annotations, by separating them into 8 reannotation chunks"

n_chunks=8
n_per_chunk=$((n_prev_annots / n_chunks + 1))
for ((i=1; i<=n_chunks; i++)); do
	head -n $((n_per_chunk * i)) $prev_annots | tail -$n_per_chunk > reannotate_$i.jsonl
done
n_per_last_chunk=$((n_per_chunk - n_chunks + (n_prev_annots % n_chunks)))
tail -$n_per_last_chunk $prev_annots > reannotate_$n_chunks.jsonl

