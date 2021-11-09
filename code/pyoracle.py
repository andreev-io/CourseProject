#!/usr/bin/env python3

import argparse
from stackapi import StackAPI
from bs4 import BeautifulSoup
import json
import math
from functools import reduce
from datetime import datetime, timedelta
from ratelimit import limits, sleep_and_retry
import re

tags = ["python3", "python", "python-3.x"]
accepted_urls = [
    "docs.python.org/3/whatsnew", "docs.python.org/3/tutorial",
    "docs.python.org/3/library", "docs.python.org/3/reference",
    "docs.python.org/3/using", "docs.python.org/3/howto",
    "docs.python.org/3/installing", "docs.python.org/3/distributing",
    "docs.python.org/3/extending", "docs.python.org/3/c-api",
    "docs.python.org/3/faq"
]


class API:
    def __init__(self, key):
        self.api = StackAPI('stackoverflow', key=key)
        # Max number of pages returned per request (StackAPI handles pagination
        # automatically).
        self.api.max_pages = 100
        # Max size of each page returned per request.
        self.api.page_size = 100

    # Limit to 10,000 requests per day and to 20 requests per second.
    @sleep_and_retry
    @limits(calls=10000, period=86400)
    @limits(calls=20, period=1)
    def call(self, *args, **kwargs):
        return self.api.fetch(*args, **kwargs)

    def get_questions(self, existing_question_ids, start_date, end_date):
        # Since we iterate over tags in this method, save seen_question_ids to
        # avoid fetching the same question multiple times if it has several
        # matching tags.
        seen_question_ids = set()
        entries = []
        for tag in tags:
            print(f"Getting questions for tag {tag}")
            questions = self.__get_questions_for_tag(tag, start_date, end_date)
            print(f"Num questions fetched: {len(questions)}")

            for question in questions:
                if "accepted_answer_id" in question:
                    question_id = question["question_id"]
                    accepted_answer_id = question["accepted_answer_id"]
                    body = question["body"]
                    if question_id in existing_question_ids or question_id in seen_question_ids:
                        continue

                    entry = Entry()
                    entry.set_question(question_id, body)
                    entry.set_answer_id(accepted_answer_id)
                    entries.append(entry)
                    seen_question_ids.add(question_id)

        print(f"Num unseen questions with accepted answers: {len(entries)}")
        return entries

    def get_answers(self, entries):
        # StackOverflow API allows us to match up to 100 answers at a time, so
        # let's break up entries into groups of up to 100 and leverage this
        # functionality.
        bulk_size = 100
        runs = len(entries) // bulk_size
        for i in range(runs + 1):
            lower_index, upper_index = i * bulk_size, (i + 1) * bulk_size
            if upper_index > len(entries):
                upper_index = len(entries)
            curr_run_entries = entries[lower_index:upper_index]

            answer_id_to_entry_index = {}
            for (j, entry) in enumerate(curr_run_entries):
                answer_id = entry.get_answer_id()
                answer_id_to_entry_index[answer_id] = i * bulk_size + j

            if len(answer_id_to_entry_index) == 0:
                continue

            answer_ids = list(answer_id_to_entry_index.keys())
            answers = self.__get_answers_with_ids(answer_ids)
            for answer in answers:
                try:
                    body = answer["body"]
                    answer_id = answer["answer_id"]
                    entry_index = answer_id_to_entry_index[answer_id]
                    entries[entry_index].set_answer(body)
                except Exception as e:
                    print(e)
                    continue

    def __get_questions_for_tag(self, tag, start_date, end_date):
        res = self.call('questions',
                        tagged=tag,
                        sort='votes',
                        fromdate=start_date,
                        todate=end_date,
                        filter='withbody')
        return res["items"]

    def __get_answers_with_ids(self, ids):
        res = self.call('answers', ids=ids, filter='withbody')
        return res["items"]


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
            "references": [],
        }

    def make_json_string(entries):
        return json.dumps(entries, default=lambda o: o.__dict__, indent=4)

    def set_question(self, id, raw):
        self.question["id"] = id
        self.question["raw"] = raw
        self.question["plain"] = BeautifulSoup(raw, "lxml").text

    def set_answer_id(self, id):
        self.answer["id"] = id

    def get_answer_id(self):
        return self.answer["id"]

    def set_answer(self, raw):
        self.answer["raw"] = raw
        beautified = BeautifulSoup(raw, "html5lib")
        self.answer["plain"] = beautified.text
        for a in beautified.find_all('a', href=True):
            if any(url in a["href"] for url in accepted_urls):
                if a.string is None:
                    continue

                possible_offsets = []
                for occurrence in beautified.findAll(text=a.string):
                    parent = occurrence.parent
                    if parent.sourceline == a.sourceline:
                        possible_offsets.append(parent.sourcepos)
                    else:
                        possible_offsets.append(-1)
                try:
                    true_index = get_min_index(list(map(lambda offset: offset - a.sourcepos, possible_offsets)))
                    plain_occurrences = [m.start() for m in re.finditer(re.escape(a.string), self.answer["plain"])]
                    plain_context_offset = plain_occurrences[true_index]
                    offset_correct = self.answer["plain"][plain_context_offset:plain_context_offset+len(a.string)] == a.string
                    self.answer["references"].append({
                        "link": a["href"],
                        "context": a.string,
                        "plain_context_offset": plain_context_offset
                    })

                    self.success = offset_correct
                except Exception as e:
                    continue


        return self.success

# Ignores negative values, finds the min among non-negatives.
def get_min_index(arr):
    curr_min = math.inf
    curr_min_index = -1
    for index, item in enumerate(arr):
        if item < 0:
            continue
        
        if item < curr_min:
            curr_min = item
            curr_min_index = index

    return curr_min_index


parser = argparse.ArgumentParser()
parser.add_argument('--stackoverflow-key', type=str)
parser.add_argument('--start-date', type=int)

args = parser.parse_args()
stackoverflow_key = args.stackoverflow_key
start_date = datetime.fromtimestamp(args.start_date)
api = API(stackoverflow_key)

while start_date < datetime.now():
    with open("entries.json", "r+") as f:
        end_date = start_date + timedelta(days=1)
        print(f"Running for period from {start_date} to {end_date}")

        # Read existing entries from file, build a set of existing IDs.
        existing_entries = json.load(f)
        existing_question_ids = set(
            map(lambda x: x["question"]["id"], existing_entries))

        # Fetch new entry prototypes.
        entries = api.get_questions(existing_question_ids, start_date,
                                    end_date)
        # Populate answers for new entry prototypes.
        api.get_answers(entries)

        # Only leave new entries that actually met our corpus requirements.
        new_entries = list(filter(lambda x: x.success, entries))
        entries = [vars(e) for e in new_entries] + existing_entries
        print(f"Adding {len(new_entries)} new entries")
        f.seek(0)
        f.write(Entry.make_json_string(entries))
        f.truncate()

        total_training = reduce(
            lambda a, x: a + x,
            map(lambda e: len(e["answer"]["references"]), entries)) if len(entries) > 0 else 0

        print(f"Total number of entries is now {len(entries)}")
        print(f"Total number of answers for training is {total_training}\n")

    start_date = start_date + timedelta(days=1)
