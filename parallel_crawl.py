import xlwt
import requests
from bs4 import BeautifulSoup
from threading import Thread
from Queue import Queue
from sys import stderr, stdout
import time

def do_queue(Class, function, interable, num_threads) :
    q = Queue()
    threads = [Class(q, function) for each in range(num_threads)]
    for each in threads :
        each.setDaemon(True)
        each.start()
    for thing in interable :
        q.put(thing)
    q.join()

class Reader (Thread) :
    def __init__(self, queue, func) :
        Thread.__init__(self)
        self.queue = queue
        self.func = func
    def run(self) :
        while True :
            component = self.queue.get()
            self.func(component)
            self.queue.task_done()

class Crawler:
    def __init__(self):
        self.book = xlwt.Workbook(encoding="utf-8")
        self.components_url = "https://os.mbed.com/components"
        self.base_url = "https://os.mbed.com"
        self.components_page = requests.get(self.components_url)
        self.soup = BeautifulSoup(self.components_page.content, 'html.parser')
        self.component_info = []
        self.count = 0
        self.total_components = 530
        # Set up Excel self.worksheet
        self.worksheet = self.book.add_sheet("Components")
        self.worksheet.write(0, 0, "Component URL")
        self.worksheet.write(0, 1, "Hello World URL")
        self.worksheet.write(0, 2, "Type")
        self.worksheet.write(0, 3, "Mbed Version")
        self.worksheet.write(0, 4, "Tested Targets")

    # Filters that gather HTML elements based on class name and/or tag type
    @staticmethod
    def component_filter(tag):
        return (tag.name == 'a' and
            tag.parent.name == 'div' and
            'component-list-item' in tag.parent['class'])

    @staticmethod
    def item_filter(tag):
        return (tag.name == 'a' and
            tag.parent.name == 'h4' and
            'ftitle' in tag.parent['class'])

    @staticmethod
    def targets_filter(tag):
        return (tag.name == 'a' and
            tag.parent.name == 'div')

    @staticmethod
    def hello_world_filter(tag):
        return (tag.name == 'a' and
            tag.parent.name == 'td')

    def progress(self, status):
        stdout.write("{} {}/{}\r\n".format(status, self.count, self.total_components))
        stdout.flush()

    def get_components(self):
        return [link.get('href') for link in self.soup(Crawler.component_filter)]

    def get_tested_platforms(self, soup):
        for link in soup.find_all(Crawler.targets_filter):
            href = link.get('href')
            if href and 'platforms' in href:
                href = href.replace("/platforms/","")
                href = href.replace("/","")
                href = href.replace("-","_")
                yield href


    def record_info(self, item):
        # Find first instance of a program URL
        info = []
        item_url = self.base_url + item
        info.append(item_url)
        item_page = requests.get(item_url)
        item_soup = BeautifulSoup(item_page.content, 'html.parser')
        hello_world = ""

        try:
            item_table = [link.get('href') for link in item_soup.find_all(Crawler.item_filter)]
            for link in item_soup(Crawler.item_filter):
                this_link = link.get('href')
                if "https" not in this_link:
                    hello_world = this_link
                    break
        except KeyError:
            pass
        targets = [link for link in self.get_tested_platforms(item_soup)]
        targets_entry = ", ".join(targets) if targets else "NONE LISTED"
        info.append(self.base_url + hello_world)
        hello_url = self.base_url + hello_world
        hello_page = requests.get(hello_url)
        hello_soup = BeautifulSoup(hello_page.content, 'html.parser')
        mbed_os_lib = ""
        is_lib = ""
        try:
            hello_table = [link.get('href') for link in hello_soup.find_all(Crawler.hello_world_filter)]
            is_lib = "LIB" if all('main.cpp' not in link for link in hello_table) else "APP"# Returns True if "main.cpp" is not present
            mbed_os_lib = 5 if any('mbed-os.lib' in link for link in hello_table) else 2
        except KeyError:
            pass
        info.append(is_lib)
        info.append(mbed_os_lib)
        info.append(targets_entry)
        self.component_info.append(info)
        self.count += 1
        self.progress(item)

    def crawl(self, component):
        remove = "/components/cat/"
        temp_url = self.base_url + component
        temp_page = requests.get(temp_url)
        temp_soup = BeautifulSoup(temp_page.content, 'html.parser')
        temp_links = [link.get('href') for link in temp_soup(Crawler.component_filter)]
        #print temp_links
        do_queue(Reader, self.record_info, temp_links, 10)

    def write_excel_sheet(self):
        for i, info in enumerate(self.component_info):
            for j, column in enumerate(info):
                self.worksheet.write(i+1, j, column)
        self.book.save("mbed-components.xls")

    def do_crawl(self):
        do_queue(Reader, self.crawl, self.get_components(), 4)


if __name__ == "__main__":
    crawler = Crawler()
    print("Start Crawling")
    start_time = time.time()
    crawler.do_crawl()
    crawler.write_excel_sheet()
    print("--- %s seconds ---" % (time.time() - start_time))
