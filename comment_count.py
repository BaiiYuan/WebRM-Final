import json
import pickle

with open('saved/DOC1500.pkl', "rb") as f:
    DOC = pickle.load(f)

total_count = dict()

for doc_id, article in DOC.items():
    count = dict()
    upvote = len(article['Comment']['Upvote'])
    downvote = len(article['Comment']['Downvote'])
    neutral = len(article['Comment']['Neutral'])
    count['upvote'] = upvote
    count['downvote'] = downvote
    count['neutral'] = neutral
    total_count[doc_id] = count

with open('comment_count.json', 'w', encoding='utf-8') as file:
    json.dump(total_count, file, ensure_ascii=False)