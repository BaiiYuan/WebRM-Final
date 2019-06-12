import argparse
from IPython import embed
from crawl.crawl_beauti import getDOC

def main(args):
    DOC = getDOC(args.nums_pages_crawling)
    embed()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Web RM Final Project")
    parser.add_argument('-n', '--nums_pages_crawling', type=int, default=1, help='Numbers of pages wwe crawling.')
    args = parser.parse_args()
    main(args)