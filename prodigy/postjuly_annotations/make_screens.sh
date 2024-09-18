#!/bin/bash
# Create 12 screens for the July annotation instructions: 8 screens for reannotators & 3 screens for group annotators.
# Use "make_annotations*.sh" to create the json files

session='session_name'

# Source the config file w/ sensitive data (won't be uploaded to git)
PRODIGY_VENV_PATH=''
BASE_PORT=''
source ../sensible_config.sh

# Labels for Prodigy
LABELS="sample,n_male,n_female,perc_male,perc_female,sample_p,n_male_p,n_female_p,perc_male_p,perc_female_p"
VIEW_ID="ner_manual"


# Create a screen that contains one window for each prodigy session


# Reannotators
screen -dmS $session
for n in {1..8}; do
    annotator=Reannotator$n
    annotations=reannotate_$n.jsonl
    port=${BASE_PORT}5$n
    db=bhg_reannotate_$n
    command="source $PRODIGY_VENV_PATH; PRODIGY_ALLOWED_SESSIONS=$annotator PRODIGY_PORT=$port prodigy mark $db $annotations --label $LABELS --view-id $VIEW_ID"
    screen -S $session -X screen $n
    screen -S $session -p $n -X stuff "${command}\n"
done

# Group annotators (3 people w/ same dataset), to check the reliability of the annotations
for n in {9..11}; do
    annotator=reliability_$((n-8))
    annotations=group_annotation.jsonl
    nn=$((50+n))
    port=${BASE_PORT}$nn
    db=bhg_reliability_$((n-8))
    command="source $PRODIGY_VENV_PATH; PRODIGY_ALLOWED_SESSIONS=$annotator PRODIGY_PORT=$port prodigy mark $db $annotations --label $LABELS --view-id $VIEW_ID"
    screen -S $session -X screen $n
    screen -S $session -p $n -X stuff "${command}\n"
done



# Reannotators
screen -dmS $session
for ((n = 1; n <= REANNOTATOR_COUNT; n++)); do
    annotator=Reannotator$n
    annotations=${ANNOTATIONS_PREFIX}${n}.jsonl
    port=$(($BASE_PORT + $n))
    db=${DB_PREFIX}${n}
    command="source $PRODIGY_VENV_PATH; PRODIGY_ALLOWED_SESSIONS=$annotator PRODIGY_PORT=$port prodigy mark $db $annotations --label $LABELS --view-id $VIEW_ID"
    screen -S $session -X screen $n
    screen -S $session -p $n -X stuff "${command}\n"
done

# Group annotators (3 people w/ same dataset), to check the reliability of the annotations
for ((n = 1; n <= RELIABILITY_GROUP_COUNT; n++)); do
    annotator=reliability_$n
    nn=$(($RELIABILITY_PORT_OFFSET + $n))
    port=80$nn
    db=${RELIABILITY_DB_PREFIX}${n}
    command="source $PRODIGY_VENV_PATH; PRODIGY_ALLOWED_SESSIONS=$annotator PRODIGY_PORT=$port prodigy mark $db $RELIABILITY_ANNOTATIONS --label $LABELS --view-id $VIEW_ID"
    screen -S $session -X screen $(($n + $REANNOTATOR_COUNT))
    screen -S $session -p $(($n + $REANNOTATOR_COUNT)) -X stuff "${command}\n"
done
