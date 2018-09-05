#!/usr/bin/env python3
import re
import sys
from bs4 import BeautifulSoup
from urllib import parse, request
from queue import PriorityQueue
from collections import defaultdict


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


def crawl(root, keywords):
    visited = set()
    results = []
    relevance_hash = {}
    
    def shouldvisit(address):
        return "cs.jhu.edu/~yarowsky/" in address and address not in visited
    
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
        for match in re.findall('\(\d\d\d\) \d\d\d-\d\d\d\d', str(h)):
            print('; '.join([a, 'PHONE', match]))

        for match in re.findall('\d\d\d \d\d\d-\d\d\d\d', str(h)):
            print('; '.join([a, 'PHONE', match]))

        # email_ext = [".com", ".co", ".org", ".edu", "ca"]

        for match in re.findall(r"[\w\.-]+@[\w\.-]+", str(h)):
            for m in re.findall(r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)", str(match)):
                    print('; '.join([a, 'EMAIL', m]))

        for match in re.findall(r"(([A-Z][a-z]+\s?)+), ([A-Z]{2}) (\d{5})", str(h)):
            add = match[1] + ", " + match[2] + " " + match[3]
            print('; '.join([a, 'ADDRESS', add]))

        # m_phone = re.search(r"[\+\(]?[1-9][0-9 .\-\(\)]{8,}[0-9]", str(h))
        # m_email = re.search(r"[\w\.-]+@[\w\.-]+", str(h))
        # m_address = re.search(r"(([A-Z][a-z]+\s?)+), ([A-Z]{2}) (\d{5})", str(h))
        #
        # if m_phone and 'Phone' in str(h):
        #     print(m_phone.group(), a)
        #
        # if m_email and 'Email' in str(h):
        #     print(m_email.group(), a)
        #
        # if m_address:
        #     print(m_address.group(), a)

        return None

    queue = PriorityQueue()
    queue.put((1, root))
    
    while not queue.empty():
        priority, address = queue.get()
        # if priority > 2:
        #     break

        try:
            r = request.urlopen(address)
            if r.status == 200:
                visited.add(address)

                if wanted(r):
                    results.append(address)
                
                html = r.read()
                extract(address, html)

                for link, title in get_links(address, html):
                    if shouldvisit(link) and link != address:
                        rel = priority + (1 - relevance(link, title, keywords))
                        # rel = priority + 1
                        print(link, "  --  ", title, " -- link and title")
                        queue.put((rel, link))
        except Exception as e:
            print(e, address)
    
    return visited, results


def main():
    menu = \
        "================================================================\n" \
        "                 Welcome to the 600.466 Web Robots              \n" \
        "================================================================\n" \
        "                                                                \n" \
        "OPTIONS:                                                        \n" \
        "  1 = Extract not self-referencing & non-local links (Part 1)   \n" \
        "  2 = Web Crawler robot_base (Part 2)                           \n" \
        "  3 = Quit                                                      \n" \
        "                                                                \n" \
        "================================================================\n"

    part1 = \
        "*************************************************************\n"\
        "            Not Self-referencing & Non-local Links           \n"\
        "*************************************************************\n"\

    part2 = \
        "*************************************************************\n"\
        "                         Web Crawler                         \n"\
        "*************************************************************\n"\

    while True:
        sys.stderr.write(menu)
        option = input("Enter Option: ")
        print("\n")
        if option == "1":
            sys.stderr.write(part1)
            print_non_local_links('https://cs.jhu.edu/~yarowsky/')
            print("\n")
        elif option == "2":
            sys.stderr.write(part2)
            keywords = ["pdf", "ppt", "slides", "yarowsky", "lecture"]
            crawl("https://cs.jhu.edu/~yarowsky/cs466.html", keywords)
            print("\n")
        elif option == "3":
            exit(0)
        else:
            sys.stderr.write("Input seems not right, try again\n")


if __name__ == "__main__": main()
