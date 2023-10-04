import json

with open('raw.jsonl') as f:
    data = []
    for line in f:
        data.append(json.loads(line))

with open('annotations.jsonl') as f:
    done = []
    for line in f:
        done.append((json.loads(line)['id'], json.loads(line)['text']))

with open ('raw_1.jsonl', 'w') as o:
    for line in data:
        if (line['id'], line['text']) not in done:
            o.write(json.dumps(line)+'\n')

