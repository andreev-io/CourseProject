import re
import json


def convert_link(link):
    link = link.replace("https://docs.python.org/3/", "")
    link = link.replace("/", " page ")
    link = link.replace(".html#", " section ")
    link = link.replace(".html", " ")
    link = link.strip()
    link = link.replace("-", " ")

    return link


with open("training_entries.json", "r") as f:
    entries = json.load(f)


source = []
target = []

for entry in entries:
    plaintext_answer = entry["answer"]["plain"]

    for reference in entry["answer"]["references"]:
        if not reference["link"].startswith("https://docs.python.org/3/"):
            continue

        pre_entity = plaintext_answer[: reference["plain_context_offset"]]
        post_entity = plaintext_answer[
            reference["plain_context_offset"] + len(reference["context"]) :
        ]

        entity_string = pre_entity
        entity_string = (
            pre_entity
            + "[START_ENT] "
            + reference["context"]
            + " [END_ENT]"
            + post_entity
        )

        entity_string = re.sub(r"\s+", " ", entity_string.strip())

        source.append(entity_string)
        target.append(convert_link(reference["link"]))

print(len(source))
print(len(target))

with open("python.source", "w") as f:
    f.write("\n".join(source))

with open("python.target", "w") as f:
    f.write("\n".join(target))
