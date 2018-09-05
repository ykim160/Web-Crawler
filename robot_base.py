#!/usr/bin/env python3
import re
import sys
import requests
from bs4 import BeautifulSoup
from urllib import parse, request
from queue import PriorityQueue
from collections import defaultdict


headers = {
    'User-Agent': 'Ye Chan Kim',
    'From': 'ykim160@jhu.edu'
}


def get_links(root, html):
    soup = BeautifulSoup(html, 'html.parser', from_encoding="iso-8859-1")
    for link in soup.find_all('a'):
        href = link.get('href')
        if href:
            text = link.string
            if not text:
                text = ''
            text = re.sub('\s+', ' ', text).strip()
            yield (parse.urljoin(root, link.get('href')), text)


def crawl(root, keywords, log, content):
    visited = set()
    results = []
    relevance_hash = {}

    def shouldvisit(address):
        return "cs.jhu.edu/" in address and address not in visited
    
    def wanted(req):
        return 'text/html' in req.headers['Content-Type'] or \
                'application/pdf' in req.headers['Content-Type'] or \
                'postscripts' in req.headers['Content-Type'] or \
                'text/plain' in req.headers['Content-Type']
    
    def relevance(link, title, keywords):
        # Here I am trying to collect words and make a dict-vector
        link = link.replace("http://www.cs.jhu.edu/", "")
        words_tokenized = (re.sub('[^0-9a-zA-Z]+', '/', link)).split("/")
        words_tokenized += (re.sub('[^0-9a-zA-Z]+', '/', title)).split("/")
        page_vector = defaultdict(int)
        key_vector = defaultdict(int)
        for i in words_tokenized:
            if i != "":
                page_vector[i] += 2
        
        for i in keywords:
            key_vector[i] += 2
        
        cos = 0
        
        for w in set(list(page_vector.keys()) + list(key_vector.keys())):
            cos += page_vector[w] * key_vector[w]
        
        key_norm = sum(map(lambda i : i * i, list(key_vector.values())))
        page_norm = sum(map(lambda i : i * i, list(page_vector.values())))
            
        return float(cos) / float(key_norm * page_norm)
    
    def extract(a, h):
        log_str = []
        for match in re.findall('\(\d\d\d\) \d\d\d-\d\d\d\d', str(h)):
            log_str.append("(" + '; '.join([a, 'PHONE', match]) + ")")
            # print('; '.join([a, 'PHONE', match]))

        for match in re.findall('\d\d\d \d\d\d-\d\d\d\d', str(h)):
            log_str.append("(" + '; '.join([a, 'PHONE', match]) + ")")
            # print('; '.join([a, 'PHONE', match]))

        # email_ext = [".com", ".co", ".org", ".edu", "ca"]

        for match in re.findall(r"[\w\.-]+@[\w\.-]+", str(h)):
            for m in re.findall(r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)", str(match)):
                    # print('; '.join([a, 'EMAIL', m]))
                    log_str.append("(" + '; '.join([a, 'EMAIL', m]) + ")")


        for match in re.findall(r"(([A-Z][a-z]+\s?)+), ([A-Z]{2}) (\d{5})", str(h)):
            add = match[1] + ", " + match[2] + " " + match[3]
            # print('; '.join([a, 'ADDRESS', add]))
            log_str.append("(" + '; '.join([a, 'ADDRESS', add]) + ")")

        with open(log, "a") as myfile:
            for l in log_str:
                myfile.write("[CONTENT] " + l + "\n")

        with open(content, "a") as myfile:
            for l in log_str:
                myfile.write(l + "\n")

        return None

    queue = PriorityQueue()
    queue.put((1, root))
    
    while not queue.empty():
        priority, address = queue.get()
        # if priority > 2:
        #     break

        try:
            page = requests.get(address, headers=headers)
            if page.status_code == requests.codes.ok:
                r = request.urlopen(address)
                visited.add(address)

                if wanted(r):
                    results.append(address)
                
                html = r.read()
                extract(address, html)

                for link, title in get_links(address, html):
                    if shouldvisit(link) and link != address:
                        rel = priority + (1 - relevance(link, title, keywords))
                        # rel = priority + 1
                        # print(link, "  --  ", title, " -- link and title")
                        queue.put((rel, link))
        except Exception as e:
            print(e, address)
    
    return visited, results


def main():
    if len(sys.argv) != 4:
        print("Usage: ./robot_base.py <log file> <content file> <url>")
        return
        
    keywords = ["pdf", "ppt", "slides", "yarowsky", "lecture"]
    crawl(str(sys.argv[3]), keywords, \
          str(sys.argv[1]), str(sys.argv[2]))


if __name__ == "__main__": main()

