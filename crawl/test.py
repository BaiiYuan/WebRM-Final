import requests
from bs4 import BeautifulSoup
from IPython import embed

INDEX_LINK = 'https://www.ptt.cc'
HOME_LINK = INDEX_LINK + '/bbs/Beauty/index.html'

def process_each_title(title, url):
    res = requests.get(url)
    soup = BeautifulSoup(res.text, 'html.parser')
    content = soup.select('div#main-content.bbs-screen.bbs-content')[0].text.split("※ 發信站: 批踢踢實業坊(ptt.cc)")[0]
    comments = [(comment.text[0], comment.text[1:].strip()) for comment in soup.select('div.push')]

    return (title, content, comments)

def do_crawling(nums_crawling=50):
    url = HOME_LINK
    DOC = {}
    for _ in range(nums_crawling):
        res = requests.get(url)
        soup = BeautifulSoup(res.text, 'html.parser')

        results = soup.select('div.title a')
        results = [(result.text[4:].strip(), result['href']) for result in results if result.text[1:3] == '正妹']

        for title, link in results:
            DOC[link] = process_each_title(title, INDEX_LINK+link)

        nextPage = soup.select('div.btn-group-paging a')
        url = INDEX_LINK + nextPage[1]['href']

def main():
    do_crawling()

if __name__ == '__main__':
    main()