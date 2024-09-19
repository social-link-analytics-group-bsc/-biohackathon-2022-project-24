# Check if the original and final have the same method sections (I recreated the original ones so I needed to make sure)
echo "If no differences are printed apart from the filename, they are the same"
for ((i=1; i<=8; i++)); do
    orig=reannotate_$i.jsonl
    final=annotated_reannotations/bhg_reannotated_$i.jsonl
    n_orig=$(cat $orig | wc -l)
    n_final=$(cat $final | wc -l)
    threshold=30
    if [ $n_final -gt $threshold ]; then
	echo $orig
    	awk '{for(i=1; i<=15; i++) printf $i " "; print ""}' $orig | head -$threshold > a
    	awk '{for(i=1; i<=15; i++) printf $i " "; print ""}' $final | head -$threshold > b
    	diff a b
    fi
done
rm a b
