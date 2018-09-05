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


def print_non_local_links(root):
    r = request.urlopen(root)
    for l in get_links(root, r.read()):
        m_domain = re.search(r"(www.)?([a-zA-Z0-9\-\.]+\.[a-zA-Z]{2,3})(\\S*)?", str(root))
        if not m_domain:
            print("Invalid Domain")
            return
        
        domain = m_domain.group()

        if str(domain) not in str(l[0]):  ## part one change this
            print(l, root)


def main():
    if len(sys.argv) != 2:
        print("Usage: ./lwp_parser.py <url>")
        return

    url = str(sys.argv[1])
    page = requests.get(url, headers=headers)

    if page.status_code == requests.codes.ok:
        print_non_local_links(url)

if __name__ == "__main__": main()

