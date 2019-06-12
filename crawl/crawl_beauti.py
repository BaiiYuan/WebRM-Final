import os
import pickle
import requests
import calendar

from time import time
from tqdm import tqdm
from IPython import embed
from bs4 import BeautifulSoup

INDEX_LINK = 'https://www.ptt.cc'
HOME_LINK = INDEX_LINK + '/bbs/Beauty/index.html'
MONTH_DICT = dict((v,k) for k,v in enumerate(calendar.month_abbr))


def is_active_image_link(link):
    return True

def process_each_comment(raw_comment):
    comment = raw_comment
    return comment

def get_date_from_main_content(main_content):
    date = main_content.split("\n")[0].split()[-4:]
    date = date[-1] + "{0:02d}".format(MONTH_DICT[date[0]]) + date[1]
    return int(date)

def get_content_from_main_content(main_content):
    content, link = [], []
    main_content = "\n".join(main_content.split("\n")[1:]).split()
    IMG_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.ppm', '.bmp', '.pgm', '.tif']
    for c in main_content:
        print(c)
        if any(c.endswith(extension) for extension in IMG_EXTENSIONS):
            if is_active_image_link(c):
                link.append(c)
        else:
            content.append(c)
    return content, link

def get_comments_from_soup(soup):
    comments = {'Upvote':[], 'Neutral': [], 'Downvote': []}
    raw_comments = [(comment.text[0], comment.text[1:].strip()) for comment in soup.select('div.push')]
    for comment_type, raw_comment in raw_comments:
        comment = process_each_comment(raw_comment)
        if comment_type == '推':
            comments['Upvote'].append(comment)
        elif comment_type == '→':
            comments['Neutral'].append(comment)
        else:
            comments['Downvote'].append(comment)

    return comments

def process_each_article(title, url):
    article = {}
    article['Title'] = title
    print(title)

    res = requests.get(url)
    soup = BeautifulSoup(res.text, 'html.parser')
    main_content = soup.select('div#main-content.bbs-screen.bbs-content')[0].text.split("※ 發信站: 批踢踢實業坊(ptt.cc)")[0]

    article['Date'] = get_date_from_main_content(main_content)
    article['Content'], article['Link'] = get_content_from_main_content(main_content)
    article['Commment'] = get_comments_from_soup(soup)

    embed()

    return article

def do_crawling(nums_pages_crawling):
    url = HOME_LINK
    DOC = {}
    for n in tqdm(range(nums_pages_crawling)):
        print(f"Crawling Page {n+1} ...")
        res = requests.get(url)
        soup = BeautifulSoup(res.text, 'html.parser')

        results = soup.select('div.title a')
        results = [(result.text[4:].strip(), result['href']) for result in results if result.text[1:3] == '正妹']

        for title, link in results:
            DOC[link] = process_each_article(title, INDEX_LINK+link)

        nextPage = soup.select('div.btn-group-paging a')
        url = INDEX_LINK + nextPage[1]['href']

    return DOC

def getDOC(nums_pages_crawling=1):
    t1 = time()
    if os.path.exists("saved/DOC.pkl"):
        with open("DOC.pkl", "rb") as f:
            DOC = pickle.load(f)
    else:
        DOC = do_crawling(nums_pages_crawling)
        with open("saved/DOC.pkl", "wb") as f:
            pickle.dump(DOC, f)

    return DOC
    print(f"Cost Time: {t1-time()}")

if __name__ == '__main__':
    getDOC()