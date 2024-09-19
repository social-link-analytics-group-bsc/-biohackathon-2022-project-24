#!/bin/bash
# Separate the original annotations into 12 equally distributed groups
n=80
file=original_annotations.jsonl
for i in {1..12}; do
	head -n $((n * i)) $file | tail -$n > annotations$i.jsonl
done
