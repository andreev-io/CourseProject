#!/usr/bin/env python3

import random 
import json

# manually unzip code/entries.json.zip

f = open('code/entries.json')
data = json.load(f)
print(len(data))
print(data[0])

random.shuffle(data)
print(len(data))
print(data[0])

testing = data[0:1000]
training = data[1000:]
f.close()

with open("training_entries.json", "r+") as tr:
    tr.seek(0)
    tr.write(json.dumps(training))
    tr.truncate()

with open("testing_entries.json", "r+") as te:
    te.seek(0)
    te.write(json.dumps(testing))
    te.truncate()

# rm code/entries.json
# zip testing_entries.json.zip testing_entries.json
# zip training_entries.json.zip training_entries.json
# rm testing_entries.json
# rm training_entries.json
