import pickle
from genre.trie import Trie
from genre.fairseq_model import GENRE

with open("./data/kilt_titles_trie_dict.pkl", "rb") as f:
    trie = Trie.load_from_dict(pickle.load(f))

wikipedia_model = GENRE.from_pretrained("./models/fairseq_entity_disambiguation_aidayago").eval()

python_docs_model = GENRE.from_pretrained("./models/python_docs_test").eval()

questions = [
    "How do I get started with Python programming?",
    "Is list comprehension useful?",
]

print(
    wikipedia_model.sample(
        questions,
        prefix_allowed_tokens_fn=lambda batch_id, sent: trie.get(sent.tolist()),
    )
)

print(
    python_docs_model.sample(
        questions,
        prefix_allowed_tokens_fn=lambda batch_id, sent: trie.get(sent.tolist()),
    )
)
