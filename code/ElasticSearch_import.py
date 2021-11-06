import json
import sys, getopt

with open('reference_doc.json', 'r', encoding = 'utf8') as json_import_file:
    source_json_data = json.load(json_import_file)

json_doc = []
StopCounter = 0;
doc_id = 0;

json_file = open("reference_doc_import.json", "w", encoding = 'utf8')

for key in source_json_data:
    StopCounter += 1
    doc_id += 1
    
    ElasticSearch_Command = {}
    ElasticSearch_Command['index'] = { "_index" : "reference", "_id" : doc_id }

    json.dump(ElasticSearch_Command, json_file, ensure_ascii=False)
    json_file.write('\n')
    json.dump(key, json_file, ensure_ascii=False)
    json_file.write('\n')

    '''
    if StopCounter == 10:
        break
    '''