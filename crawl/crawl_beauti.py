import os
import pickle
import requests
import calendar
import urllib
import jieba

from PIL import Image
from time import time
from tqdm import tqdm
from IPython import embed
from bs4 import BeautifulSoup

INDEX_LINK = 'https://www.ptt.cc'
HOME_LINK = INDEX_LINK + '/bbs/Beauty/index.html'
MONTH_DICT = dict((v,k) for k,v in enumerate(calendar.month_abbr))


def is_active_image_link(link):
	res = []
	ret = urllib.request.urlopen(link)
	if ret.status == 200:
		image = Image.open(ret)
		res.append(image)
		return True, res
	else:
		return False
	return False

def process_each_comment(raw_comment):
	URL_BEGINS = ['http', 'https']
	result = []
	raw_comment = raw_comment.replace('\n','')
	raw_comment = raw_comment.split(':', 1)
	raw_comment[1] = raw_comment[1].split()[:-3]
	for w in raw_comment[1]:
		if any(w.startswith(begins) for begins in URL_BEGINS):
			return [w]
		else:
			c = jieba.cut(w)
			for word in c:
				result.append(word)
	return result

def get_date_from_main_content(main_content):
	date = main_content.split("\n")[0].split()[-4:]
	date = date[-1] + "{0:02d}".format(MONTH_DICT[date[0]]) + date[1]
	return int(date)

def get_content_from_main_content(main_content):
	content, link, image = [], [], []
	main_content = "\n".join(main_content.split("\n")[1:]).split()
	IMG_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.ppm', '.bmp', '.pgm', '.tif']
	URL_BEGINS = ['http', 'https']
	for c in main_content:
		print(c)
		if any(c.startswith(begins) for begins in URL_BEGINS):
			if not any(c.endswith(extension) for extension in IMG_EXTENSIONS):
				c += '.jpg'
			is_active, im = is_active_image_link(c)
			if is_active:
				link.append(c)
			if im:
				image.append(im)
		else:
			content.append(c)
	return content, link, image

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

def process_comment(comment):
	res = {}
	for type_ in comment:
		res[type_] = []
		for _comment_ in comment[type_]:
			result = []
			_comment_ = _comment_.replace('\n','')
			_comment_ = _comment_.split(':', 1)
			_comment_[1] = _comment_[1].split()[:-3]
			for w in _comment_[1]:
				c = jieba.cut(w)
				for word in c:
					result.append(word)
			res[type_].append(result)
	return res

def process_each_article(title, url):
	article = {}
	article['Title'] = title
	print(title)

	res = requests.get(url)
	soup = BeautifulSoup(res.text, 'html.parser')
	main_content = soup.select('div#main-content.bbs-screen.bbs-content')[0].text.split("※ 發信站: 批踢踢實業坊(ptt.cc)")[0]

	article['Date'] = get_date_from_main_content(main_content)
	article['Content'], article['Link'], article['Image'] = get_content_from_main_content(main_content)
	article['Comment'] = get_comments_from_soup(soup)
	#article['Comment_Process'] = process_comment(article['Comment'])

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