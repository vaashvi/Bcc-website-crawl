from urllib.request import urlopen
from link_finder import LinkFinder
from domain import *
from general import *
import json
from bs4 import BeautifulSoup

class Spider:

    project_name = ''
    base_url = ''
    domain_name = ''
    queue_file = ''
    crawled_file = ''
    queue = set()
    crawled = set()
    temp_set=set()

    def __init__(self, project_name, base_url, domain_name):
        Spider.project_name = project_name
        Spider.base_url = base_url
        Spider.domain_name = domain_name
        Spider.queue_file = Spider.project_name + '/queue.txt'
        Spider.crawled_file = Spider.project_name + '/crawled.txt'
        Spider.output_file=Spider.project_name+'/output_file.json'
        self.boot()
        self.crawl_page('First spider', Spider.base_url)

    # Creates directory and files for project on first run and starts the spider
    @staticmethod
    def boot():
        create_project_dir(Spider.project_name)
        create_data_files(Spider.project_name, Spider.base_url)
        Spider.queue = file_to_set(Spider.queue_file)
        Spider.crawled = file_to_set(Spider.crawled_file)

    # Updates user display, fills queue and updates files
    @staticmethod
    def crawl_page(thread_name, page_url):
        if page_url not in Spider.crawled:
            crawler_url_id=len(Spider.crawled)
            print(thread_name + ' now crawling ' + page_url)
            # if crawler_url_id < 100:
            print('Queue ' + str(len(Spider.queue)) + ' | Crawled  ' + str(crawler_url_id))
            if crawler_url_id ==0:
                Spider.add_links_to_queue(Spider.gather_links(page_url))
            if '/news/business-' in page_url:
                Spider.add_links_to_queue(Spider.gather_links(page_url))
                Spider.crawled.add(page_url)
                Spider.gather_article(page_url,crawler_url_id)

            Spider.queue.remove(page_url)
            Spider.update_files()
        


    # Converts raw response data into readable information and checks for proper html formatting
    @staticmethod
    def gather_links(page_url):
        html_string = ''
        try:
            response = urlopen(page_url)
            if 'text/html' in response.getheader('Content-Type'):
                html_bytes = response.read()
                html_string = html_bytes.decode("utf-8")
            finder = LinkFinder(Spider.base_url, page_url)
            finder.feed(html_string)
        except Exception as e:
            print(str(e))
            return set()
        return finder.page_links()

    # Saves queue data to project files
    @staticmethod
    def add_links_to_queue(links):
        for url in links:
            if (url in Spider.queue) or (url in Spider.crawled) or (url in Spider.temp_set):
                continue
            if Spider.domain_name != get_domain_name(url):
                continue
            Spider.queue.add(url)
            Spider.temp_set.add(url)

    @staticmethod
    def update_files():
        set_to_file(Spider.queue, Spider.queue_file)
        set_to_file(Spider.crawled, Spider.crawled_file)


    @staticmethod
    def gather_article(page_url,id):
        html_string = ''
        try:
            response = urlopen(page_url)
            if 'text/html' in response.getheader('Content-Type'):
                html_bytes = response.read()
                html_string = html_bytes.decode("utf-8")
                parsed_html = BeautifulSoup(html_string)
                # print(parsed_html)
                header_info=json.loads((parsed_html.head.findAll('script', attrs={"type":"application/ld+json"}))[0].text)
                gather_data={
                    'id':id,
                    'Headline':header_info['headline'],
                    'Description':header_info['description'],
                    'Url':header_info['url'],
                    'Published_Time':header_info['datePublished'],
                    'Author':header_info['author']['name']
                }
                update_json(Spider.output_file,gather_data)
                # print(gather_data)
        except Exception as e:
            print("article error "+str(e))
    
