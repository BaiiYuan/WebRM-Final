import json
import jieba
import pandas as pd
import numpy as np
import random
import csv
import operator
import math
import requests
import urllib
import os
import pickle
import calendar
import sys
from argparse import ArgumentParser
from collections import Counter
from bs4 import BeautifulSoup
from crawl.crawl_beauti import get_content_from_main_content
import webbrowser

parser = ArgumentParser()
parser.add_argument("-t", default='inverted_file_1500_title.json', dest = "title_inverted_file", help = "Pass in a .json file.")
parser.add_argument("-c", default='inverted_file_1500_content.json', dest = "content_inverted_file", help = "Pass in a .json file.")
parser.add_argument("-p", default='inverted_file_1500_upvote.json', dest = "push_inverted_file", help = "Pass in a .json file.")
parser.add_argument("-a", default=0.85, dest = "alpha", help = "Pass in a value [0-1]")
parser.add_argument("-b", default=0.1, dest = "beta", help = "Pass in a value < 1-alpha.")
parser.add_argument("-n", default='comment_count.json', dest = "push_cnt_file", help = "Pass in a .json file.")
#parser.add_argument("-r", "--raw_file",default='url2content.json', dest = 'raw_file',help = "Pass in a .json file.")


url_base = 'https://www.ptt.cc'

args = parser.parse_args()

# load inverted file
with open(args.title_inverted_file) as f:
	title_invert_file = json.load(f)
with open(args.content_inverted_file) as f:
	content_invert_file = json.load(f)
with open(args.push_inverted_file) as f:
	push_invert_file = json.load(f)
with open(args.push_cnt_file) as f:
        push_cnt_file = json.load(f)

alpha = args.alpha   #weight of title
beta = args.beta #weight of content
gamma = 1 - alpha - beta


#load raw data
#with open(args.raw_file) as f:
#        raw_file = json.load(f)
'''
doc_total_len = 0
doc_len_dic = dict()
for i in raw_file:
    doc_len = len(raw_file[i])
    doc_total_len += doc_len
    doc_len_dic[i] = doc_len

print ("total len: ",doc_total_len)
'''

# read query and news corpus
#querys = np.array(pd.read_csv(args.query_file)) # [(query_id, query), (query_id, query) ...]
#corpus = np.array(pd.read_csv(args.corpus_file)) # [(news_id, url), (news_id, url) ...]
#num_corpus = corpus.shape[0] # used for random sample

#doc_averge_len = doc_total_len / float(num_corpus)

#build dic of {'new_id' : 'url'}
#id_url_dic = {}
#for i in range(num_corpus):
#    id_url_dic[corpus[i][0]] = corpus[i][1]

all_docs = dict()
for word in title_invert_file:
    for doc in title_invert_file[word]['docs']:
        if doc in all_docs:
            all_docs[doc] += 1
        else:
            all_docs[doc] = 1

N = (len(all_docs))

all_docs_content = dict()
for word in content_invert_file:
    for doc in content_invert_file[word]['docs']:
        if doc in all_docs_content:
            all_docs_content[doc] += 1
        else:
            all_docs_content[doc] = 1

N_content = len(all_docs_content)


all_docs_push = dict()
for word in push_invert_file:
    for doc in push_invert_file[word]['docs']:
        if doc in all_docs_push:
            all_docs_push[doc] += 1
        else:
            all_docs_push[doc] = 1

N_push = len(all_docs_push)

print('Enter your query: ',file=sys.stderr)
querys = input()
querys = [('1',querys)]

doc_averge_len = 1



# process each query
final_ans = []
for (query_id, query) in querys:

        # counting query term frequency
        query_cnt = Counter()
        query_words = list(jieba.cut(query))
        query_cnt.update(query_words)
        
        # calculate scores by tf-idf
        document_scores = dict() # record candidate document and its scores with title
        document_scores_content = dict() # record candidate document and its scores with content inverted file
        document_scores_push = dict()

        #parameter
        k1 = 1.2
        b = 0.75
        k3 = 100
        #N = num_corpus
        for (word, count) in query_cnt.items():
                if word in title_invert_file:
                        query_tf = count
                        idf = title_invert_file[word]['idf']
                        idf = N/idf
                        for document_count_dict in title_invert_file[word]['docs']:
                                #for doc, doc_tf in document_count_dict.items():
                                        doc = document_count_dict
                                        doc_tf = title_invert_file[word]['docs'][doc] 
                                        #dl = doc_len_dic[id_url_dic[doc]]
                                        dl = 1
                                        if doc in document_scores:
                                                #document_scores[doc] += query_tf * idf * doc_tf * idf
                                                document_scores[doc] += math.log((N-idf+0.5)/(idf+0.5))*\
                                                        (((k1+1)*doc_tf)/((k1*(1-b+b*(dl/doc_averge_len)))+doc_tf))*\
                                                        (((k3+1)*query_tf)/(k3+query_tf))
                                        else:
                                                #document_scores[doc] = query_tf * idf * doc_tf * idf
                                                document_scores[doc] = math.log((N-idf+0.5)/(idf+0.5))*\
                                                        (((k1+1)*doc_tf)/((k1*(1-b+b*(dl/doc_averge_len)))+doc_tf))*\
                                                        (((k3+1)*query_tf)/(k3+query_tf))
                if word in content_invert_file:
                        query_tf = count
                        idf = content_invert_file[word]['idf']
                        idf = N_content/idf
                        for document_count_dict in content_invert_file[word]['docs']:
                                #for doc, doc_tf in document_count_dict.items():
                                        doc = document_count_dict
                                        doc_tf = content_invert_file[word]['docs'][doc] 
                                        #dl = doc_len_dic[id_url_dic[doc]]
                                        dl = 1
                                        if doc in document_scores_content:
                                                #document_scores[doc] += query_tf * idf * doc_tf * idf
                                                document_scores_content[doc] += math.log((N_content-idf+0.5)/(idf+0.5))*\
                                                        (((k1+1)*doc_tf)/((k1*(1-b+b*(dl/doc_averge_len)))+doc_tf))*\
                                                        (((k3+1)*query_tf)/(k3+query_tf))
                                        else:
                                                #document_scores[doc] = query_tf * idf * doc_tf * idf
                                                document_scores_content[doc] = math.log((N_content-idf+0.5)/(idf+0.5))*\
                                                        (((k1+1)*doc_tf)/((k1*(1-b+b*(dl/doc_averge_len)))+doc_tf))*\
                                                        (((k3+1)*query_tf)/(k3+query_tf))
                
                if word in push_invert_file:
                        query_tf = count
                        idf = push_invert_file[word]['idf']
                        idf = N_push/idf
                        for document_count_dict in push_invert_file[word]['docs']:
                                #for doc, doc_tf in document_count_dict.items():
                                        doc = document_count_dict
                                        doc_tf = push_invert_file[word]['docs'][doc] 
                                        #dl = doc_len_dic[id_url_dic[doc]]
                                        dl = 1
                                        if doc in document_scores_push:
                                                #document_scores[doc] += query_tf * idf * doc_tf * idf
                                                document_scores_push[doc] += math.log((N_push-idf+0.5)/(idf+0.5))*\
                                                        (((k1+1)*doc_tf)/((k1*(1-b+b*(dl/doc_averge_len)))+doc_tf))*\
                                                        (((k3+1)*query_tf)/(k3+query_tf))
                                        else:
                                                #document_scores[doc] = query_tf * idf * doc_tf * idf
                                                document_scores_push[doc] = math.log((N_push-idf+0.5)/(idf+0.5))*\
                                                        (((k1+1)*doc_tf)/((k1*(1-b+b*(dl/doc_averge_len)))+doc_tf))*\
                                                        (((k3+1)*query_tf)/(k3+query_tf))
	
        for doc in document_scores:
            if doc in document_scores_content and doc in document_scores_push:
                document_scores[doc] = document_scores[doc]*alpha + document_scores_content[doc]*beta + document_scores_push[doc]*gamma
            elif doc in document_scores_content:
                document_scores[doc] = document_scores[doc]*(alpha+gamma) + document_scores_content[doc]*beta
            elif doc in document_scores_push:
                document_scores[doc] = document_scores[doc]*(alpha+beta) + document_scores_push[doc]*gamma
            #take number of upvote comment in consider
            document_scores[doc] += push_cnt_file[doc]['upvote'] * 0.1
        
        
        
        
        # sort the document score pair by the scoreinverted_file_1500_title.json
        sorted_document_scores = sorted(document_scores.items(), key=operator.itemgetter(1), reverse=True)
        #feedback
        '''
        for i in range(3):
            doc_id = sorted_document_scores[i][0]
            doc_words = list(jieba.cut(raw_file[id_url_dic[doc_id]]))
            query_cnt.update(doc_words)
        
        document_scores2 = dict()
        for (word, count) in query_cnt.items():
                if word in invert_file:
                        query_tf = count
                        idf = invert_file[word]['idf']
                        idf = N/idf
                        for document_count_dict in invert_file[word]['docs']:
                                #for doc, doc_tf in document_count_dict.items():
                                        #dl = doc_len_dic[id_url_dic[doc]]
                                        dl = 1
                                        if doc in document_scores2:
                                                #document_scores[doc] += query_tf * idf * doc_tf * idf
                                                document_scores2[doc] += math.log((N-idf+0.5)/(idf+0.5))*\
                                                        (((k1+1)*doc_tf)/((k1*(1-b+b*(dl/doc_averge_len)))+doc_tf))*\
                                                        (((k3+1)*query_tf)/(k3+query_tf))
                                        else:
                                                #document_scores[doc] = query_tf * idf * doc_tf * idf
                                                document_scores2[doc] = math.log((N-idf+0.5)/(idf+0.5))*\
                                                        (((k1+1)*doc_tf)/((k1*(1-b+b*(dl/doc_averge_len)))+doc_tf))*\
                                                        (((k3+1)*query_tf)/(k3+query_tf))
        
        alpha = 0.9
        for i in document_scores:
            if i in document_scores2:
                document_scores[i] = alpha*document_scores[i] + (1-alpha)*document_scores2[i]
        sorted_document_scores = sorted(document_scores.items(), key=operator.itemgetter(1), reverse=True)
        '''
        # record the answer of this query to final_ans
        
        final_ans.append([url_base+doc_score_tuple[0] for doc_score_tuple in sorted_document_scores[:]])
        
        
        #print (final_ans)

        print ("<!DOCTYPE html>")
        print ("<html>")
        print ("<body>")
        
        for doc in final_ans:
            url_cnt = 0
            for url in doc:
                if url_cnt > 20:
                    break
                try:
                    res = requests.get(url)
                    soup = BeautifulSoup(res.text,'html.parser')
                    main_content = soup.select('div#main-content.bbs-screen.bbs-content')[0].text.split("※ 發信站: 批踢踢實業坊(ptt.cc)")[0]
                    content,pictures = get_content_from_main_content(main_content)
                    print (url,file=sys.stderr)
                    print ('<p><a href="'+url+'">'+url+'</a></p>')
                    cnt = 1
                    for pic in pictures:
                        print ("<img src="+pic+">")
                        if cnt == 3:
                            break
                        cnt += 1
                    url_cnt += 1
                except:
                    print('page not found',file=sys.stderr)
                    pass
        print ("</body>")
        print ("</html>")


'''
        if len(sorted_document_scores) >= 300:
                final_ans.append([doc_score_tuple[0] for doc_score_tuple in sorted_document_scores[:300]])
        else: # if candidate documents less than 300, random sample some documents that are not in candidate list
                documents_set  = set([doc_score_tuple[0] for doc_score_tuple in sorted_document_scores])
                sample_pool = ['news_%06d'%news_id for news_id in range(1, num_corpus+1) if 'news_%06d'%news_id not in documents_set]
                sample_ans = random.sample(sample_pool, 300-count)
                sorted_document_scores.extend(sample_ans)
                final_ans.append([doc_score_tuple[0] for doc_score_tuple in sorted_document_scores])
	
# write answer to csv file
with open(args.output_file, 'w', newline='') as csvfile:
	writer = csv.writer(csvfile)
	head = ['Query_Index'] + ['Rank_%03d'%i for i in range(1,301)]
	writer.writerow(head)
	for query_id, ans in enumerate(final_ans, 1):
		writer.writerow(['q_%02d'%query_id]+ans)
'''
