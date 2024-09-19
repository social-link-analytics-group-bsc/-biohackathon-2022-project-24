# Get the annotations annotated in Prodigy
OUTPUT_DIR=annotated_reannotations/
mkdir -p $OUTPUT_DIR

for ((i=1; i<=8; i++)); do
    output=$OUTPUT_DIR/bhg_reannotated_$i.jsonl
    prodigy db-out bhg_reannotate_$i > $output
    num_i=$(cat reannotate_$i.jsonl | wc -l)
    num_o=$(cat $output | wc -l)
    echo Reannotator $i has reannotated $num_o/$num_i method sections
done

for ((i=1; i<=3; i++)); do
    output=annotated_reannotations/bhg_reliability_$i.jsonl
    prodigy db-out bhg_reliability_$i > $output
    num_i=$(cat group_annotation.jsonl | wc -l)
    num_o=$(cat $output | wc -l)
    echo Reliability $i has reannotated $num_o/$num_i method sections
done

