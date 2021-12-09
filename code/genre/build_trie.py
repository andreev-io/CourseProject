from genre.trie import Trie
import pickle
import json


def convert_link(link):
    link = link.replace("https://docs.python.org/3/", "")
    link = link.replace("/", " page ")
    link = link.replace(".html#", " section ")
    link = link.replace(".html", " ")
    link = link.strip()
    link = link.replace("-", " ")

    return link


with open("../reference_link.txt", "r") as f:
    links = [line.strip() for line in f.readlines()]

with open("./encoder_modified.json", "r") as f:
    encodings = json.load(f)

trie = Trie()

for link in links:
    trie.add([encodings[word] for word in convert_link(link).split(" ")])

with open("python_links_trie.pkl", "wb") as f:
    pickle.dump(trie, f)
