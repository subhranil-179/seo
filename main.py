from bs4 import BeautifulSoup
from pyperclip3 import copy as pc3copy
import requests
from sys import stdin
from tabulate import tabulate

divider = "+----------------------------------------------------------------------------------------------------+\n"


class Tool:
    def __init__(self):
        self.data = ""
        self.choice = ""
        self.output = ""
        self.error_headers = ""
        self.errors = []
        self.output_len = 0

    def get_data(self):
        print("Enter list of URLs: (Press Ctrl+d twice aftering entering all urls)\n" + divider, end="")
        self.data = stdin.read()
        print("\n" + divider + "Processing...")

    def get_choice(self):
        print("1: Get Keywords from Slugs\n2: Get all URLs from Sitemaps")
        self.choice = int(input("Enter number: "))

    def output_data(self):
        print(divider + self.output)
        pc3copy(self.output)
        print(divider + f"{self.output_len} lines copied to clipboard")

    def show_errors(self):
        print(divider, tabulate(self.errors, headers=self.error_headers))

    def to_bulk(self):
        """
        Converts user input to list and removes empty items
        """
        self.data = [url for url in self.data.split("\n")]
        self.data = list(filter(None, self.data))

    def deslugify(self):
        """
        Extracts Keyword/s from slug
        """
        self.__class__.to_bulk(self)
        ex_url = self.data[0]
        first_occurence = ex_url.find("/", 7)

        print("")
        for i in range(len(self.data)):
            self.data[i] = str(self.data[i])[first_occurence:].lstrip("/").rstrip("/").replace("-", " ")

        for url in self.data:
            self.output += url+"\n"

        self.output = self.output.rstrip("\n")
        self.output_len = len(self.data)

    def get_all_urls(self):
        """
        Fetches all urls from sitemaps
        """
        self.__class__.to_bulk(self)
        bulk_urls = list()
        for url in self.data:
            res = requests.get(str(url))
            if not res.ok:
                self.errors.append([url, 0, res.status_code])
            else:
                soup = BeautifulSoup(res.text, features="xml")
                urls = soup.find_all(lambda tag: tag.name == 'loc' and tag.prefix == '' or None)
                urls = list(map(lambda url: url.text, urls))
                bulk_urls += urls
                self.errors.append([url, len(urls), res.status_code])
        for url in bulk_urls:
            self.output += url+"\n"

        self.output = self.output.rstrip("\n")
        self.output_len = len(bulk_urls)
        self.error_headers = ['Domain', 'Posts', 'Response']

    def run(self):
        self.__class__.get_choice(self)
        self.__class__.get_data(self)
        match self.choice:
            case 1:
                self.__class__.deslugify(self)
            case 2:
                self.__class__.get_all_urls(self)
        self.__class__.output_data(self)
        if self.errors:
            self.__class__.show_errors(self)


if __name__ == '__main__':
    Tool().run()
