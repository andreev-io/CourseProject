#!/usr/bin/env python3

import argparse
from stackapi import StackAPI
from bs4 import BeautifulSoup
import json


def make_api():
    parser = argparse.ArgumentParser()
    parser.add_argument('--stackoverflow-key', type=str)
    args = parser.parse_args()
    stackoverflow_key = args.stackoverflow_key
    
    SITE = StackAPI('stackoverflow', key=stackoverflow_key)
    # Can't be larger than 100
    SITE.page_size = 5
    SITE.max_pages = 1

    return SITE

class Entry:
    def __init__(self):
        self.success = False

        self.question = {
            "id": 0,
            "raw": "",
            "plain": "",
        }

        self.answer = {
            "id": 0,
            "raw": "",
            "plain": "",
            "reference_link": "",
            "link_context": "",
        }

    def set_question(self, id, raw):
        self.question["id"] = id
        self.question["raw"] = raw
        self.question["plain"] = BeautifulSoup(raw, "lxml").text

    def set_answer_id(self, id):
        self.answer["id"] = id

    def get_answer_id(self):
        return self.answer["id"]

    def is_answer_ok(raw):
        return "docs.python.org/3/library" in raw or "docs.python.org/3/reference" in raw or "docs.python.org/3/tutorial" in raw

    def set_answer(self, raw):
        self.answer["raw"] = raw
        beautified = BeautifulSoup(raw, "lxml")
        self.answer["plain"] = beautified.text
        for a in beautified.find_all('a', href=True):
            if "docs.python.org/3" in a["href"]:
                self.answer["reference_link"] = a["href"]
                self.answer["link_context"] = a.string

        self.success = True

def get_questions(api):
    res = api.fetch('questions', tagged='python3', sort='votes', fromdate='1627776000', filter='withbody')
    questions = res["items"]
    print(f"Num questions fetched: {len(questions)}")

    entries = []
    for question in questions:
        if "accepted_answer_id" in question:
            entry = Entry()
            entry.set_question(question["question_id"], question["body"])
            entry.set_answer_id(question["accepted_answer_id"])
            entries.append(entry)

    print(f"Num questions with accepted answers: {len(entries)}")
    return entries

def get_answers(api, entries):
    for entry in entries:
        res = api.fetch('answers', ids=[entry.get_answer_id()], filter='withbody')
        answers = res["items"]
        try:
            answer = answers[0]
            if Entry.is_answer_ok(answer["body"]):
                entry.set_answer(answer["body"])
        except:
            continue

api = make_api()
entries = get_questions(api)
get_answers(api, entries)
entries = list(filter(lambda x: x.success, entries))
jsonString = json.dumps(entries, default=lambda o: o.__dict__, indent=4)
print(jsonString)

with open("entries.json", "w") as f:
    f.write(jsonString)
