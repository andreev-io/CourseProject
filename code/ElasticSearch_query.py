#!/usr/bin/env python3

import json
from os import link
from elasticsearch import Elasticsearch
import pandas as pd
import matplotlib.pyplot as plt



# Step 1: Read StackOverflow entries file
with open('StackOverflow-entries.json', 'r', encoding = 'utf8') as json_StackOverflow_file:
    json_StackOverflow_data = json.load(json_StackOverflow_file)

# Step 2: Read plain question and reference link(s)
SO_questions = []
SO_answer_links = []
StopCounter = 0;

for key in json_StackOverflow_data:
    StopCounter += 1
        
    # Step 2-1: Normalize question (Remove special characters)
    SO_question_plain = key["question"]["plain"]
    SO_question_plain = SO_question_plain.replace('\n', ' ')

    SO_questions.append(SO_question_plain)
        
    # Step 2-2: Extract answer link(s)
    StackOverflow_answer = key["answer"]["references"]
    node_answer_link = []

    for answer_key in StackOverflow_answer:
        answer_link = answer_key["link"]
        node_answer_link.append(answer_link)
    
    SO_answer_links.append(node_answer_link)
           
    # if StopCounter == 100:
    #    break;

# Step 3: ElasticSearch and compare search links with SO answer
es = Elasticsearch('[13.82.107.120]:9200')

count = 0;
found_count = 0;
found_rank = [];
json_result_file = open("elastic_search_result.txt", "w", encoding = 'utf8')

for question in SO_questions:
    
    res = es.search(
        index="reference",
        body = {
            "size" : 200,
            "query":
                {"match":
                    {"text": question}
                }
        }
    )

    for SO_answer_url in SO_answer_links[count]:
        
        rank = 1;
        result_format = "Question {question_no}: reciprocal rank {rank}, answer link {answer_link}."
        
        for source in res["hits"]["hits"]:
            found = False
            answer_link = source["_source"]["url"]
            
            if SO_answer_url == answer_link:
                print(result_format.format (question_no=count+1, rank=rank, answer_link = SO_answer_url))
                found = True
                found_count += 1
                found_rank.append(rank)
            
            rank += 1;

        if found == False:
            print(result_format.format (question_no=count, rank="not found", answer_link = "not found"))

    count += 1;

summary_form = "{question_no} questions, {found_count} rank found ({ratio:.0%})"
summary = summary_form.format(question_no=count, found_count=found_count, ratio=found_count/count)
print(summary)

found_rank_graph = pd.Series(found_rank)
plt.hist(found_rank_graph, bins=20)
plt.title(summary)
plt.xlabel('rank')
plt.ylabel('count')
plt.show()
