#!/bin/bash
session='nuria_bhg'

# Create a screen that contains one window for each prodigy session
screen -dmS $session
for n in {0..7}; do
    if [ $n -lt 4 ]; then
        i=1
        m=$n
    else
        i=2
        m=$((n - 4))
    fi
    command="source /home/destrada/tools/prodigy/venv/bin/activate; PRODIGY_ALLOWED_SESSIONS=Annotator$n PRODIGY_PORT=805$n prodigy mark bhg_${m}_${i} annotations_0${m}_${i}.jsonl --label sample,n_male,n_female,perc_male,perc_female,sample_p,n_male_p,n_female_p,perc_male_p,perc_female_p --view-id ner_manual"
    screen -S $session -X screen $n
    screen -S $session -p $n -X stuff "${command}\n"
done


