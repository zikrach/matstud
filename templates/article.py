#/usr/bin/python
# -*- coding: utf-8 -*-
"""Class for article content"""

from parse import MatStud

class Article(object):

    def __init__(self, **kwargs):
        if "number" in kwargs:
            self.number = kwargs["number"]
        if "volume" in kwargs:
            self.volume = kwargs["volume"]
        if "url" in kwargs:
            self.url = kwargs["url"]


    def get_article_content(self):
        for url in MatStud.get_content_volume(self.volume, self.number):
            print(url)
        #article = site.get_volume_link(40, 1)[:-9] + url[3]
        #print(article)
        #html_article = urlopen(article).read()
        #html = bs4.BeautifulSoup(html_article, "lxml")
        #title = url[1].replace('\n',' ')
        #authors = str(url[0]).split(',')
        #keywords = html.keyword.string.split(';')
        #abstract = html.abstract.string.replace('\n',' ')
        #text_url = article[:-4] + 'pdf'
        #print(title, authors, keywords, abstract, text_url)

if __name__ == "__main__":
    for volume in range(35, 410):
        for number in [1, 2]:
            text = Article(volume=39, number=1,
                   url="http://matstud.org.ua/texts/2013/40_1/16-22.html")
    text.get_article_content()