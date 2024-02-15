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
        self.options = ["Get Keywords from Slugs",
                        "Get all URLs from Sitemaps",
                        "Get URL for Ubersuggest"]

    def get_data(self):
        print("Enter list of URLs: (Press Ctrl+d twice aftering entering all urls)\n" + divider, end="")
        self.data = stdin.read()
        print("\n" + divider + "Processing...")

    def get_choice(self):
        for i in range(len(self.options)):
            print(f"{i+1}: {self.options[i]}")
        self.choice = int(input("Enter number: "))

    def output_data(self):
        print(divider + self.output)
        pc3copy(self.output)
        if self.output_len == 1:
            print(divider + f"{self.output_len} line copied to clipboard")
        else:
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

    def get_ubersuggest_url(self):
        occurance_count = self.data.count(":") + self.data.count(":")

        for i in range(occurance_count):
            self.data = self.data.replace("/", "%2F").replace(":", "%3A")

        self.output = f"https://app.neilpatel.com/en/traffic_analyzer/overview?domain={self.data}&lang=en&locId=2840&mode=url"
        self.output_len = 1

    def run(self):
        self.__class__.get_choice(self)
        self.__class__.get_data(self)
        match self.choice:
            case 1:
                self.__class__.deslugify(self)
            case 2:
                self.__class__.get_all_urls(self)
            case 3:
                self.__class__.get_ubersuggest_url(self)
        self.__class__.output_data(self)
        if self.errors:
            self.__class__.show_errors(self)


if __name__ == '__main__':
    Tool().run()
