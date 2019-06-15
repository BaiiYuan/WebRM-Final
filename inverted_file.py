import pickle
import jieba
from collections import Counter
import argparse
import json

def main(args):

    inverted_file = dict()
    with open('saved/DOC_470.pkl', "rb") as f:
        DOC = pickle.load(f)

    # load_stop_words
    stop_words = []
    with open('stopWords.txt', 'r', encoding='UTF-8') as file:
        for data in file.readlines():
            data = data.strip()
            stop_words.append(data)


    inverted_file = dict()
    print(len(DOC))
    for doc_id, article in DOC.items():
        terms = list()


        title = list(jieba.cut(article['Title']))
        for term in title:
            if term not in stop_words and term != " ":
                terms.append(term)


        for content in article['Content']:
            content = list(jieba.cut(content))
            for term in content:
                if term not in stop_words:
                    terms.append(term)


        term_cnt = Counter()
        term_cnt.update(terms)

        for term, count in term_cnt.items():
            if term in inverted_file:
                inverted_file[term]['idf'] += 1
                inverted_file[term]['docs'][doc_id] = count
            else:
                inverted_file[term] = dict()
                inverted_file[term]['idf'] = 1
                inverted_file[term]['docs'] = dict()
                inverted_file[term]['docs'][doc_id] = count

    print(len(inverted_file))
    with open('inverted_file_470.json', 'w', encoding='utf-8') as file:
        json.dump(inverted_file, file, ensure_ascii=False)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="contruct inverted file")
    parser.add_argument('-c', '--use_comment', type=bool, default=False, help='')
    args = parser.parse_args()
    main(args)
