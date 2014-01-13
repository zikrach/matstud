#/usr/bin/python
# -*- coding: utf-8 -*-
"""module for parsing matstud archive"""

import bs4
from urllib.request import urlopen
from lxml import etree


class Error(Exception):
    """Базовый класс для всех исключений в этом модуле."""
    pass


class InputError(Error):
    """Исключение порождается при ошибках при вводе.

    Атрибуты:
        expression -- выражение на вводе, в котором обнаружена ошибка
        message -- описание ошибки
    """

    def __init__(self, expression, message):
        self.expression = expression
        self.message = message


class MatStud(object):
    """ Клас для роботи з сайтом http://matstud.org.ua"""
    def __init__(self, address):
        self.__Address = address

    def get_all_volume_link(self):
        """Функція вертає список, який містить назву номеру журналу і
        посилання на них"""
        html_archive = urlopen(self.__Address).read()
        soup = bs4.BeautifulSoup(html_archive, "lxml")
        list_volume = [arg for arg in soup.find_all('a')]
        for arg in list_volume:
            if 'V.' in arg.contents[0]:
                journal = str(arg.contents[0]).split(',')
                volume = int(journal[0][2:])
                number = 1
                if volume > 6:
                    number = int(journal[1][3:])
                yield volume, number, arg.get('href')

    def get_volume_link(self, volume, number=1):
        """Функція вертає посилання на том volume, номер number журналу"""
        if number not in [1, 2]:
            raise InputError(number, "Невірний номер журналу!")
        for vol, num, href in self.get_all_volume_link():
            if volume > 6:
                if vol == volume and num == number:
                    return href
            else:
                if volume == vol:
                    return href
        else:
            raise InputError(volume, "Невірний том журналу!")

    def get_content_volume(self, volume, number=1):
        """"Функція повертає зміст номеру журналу"""
        html_volume = urlopen(self.get_volume_link(volume, number)).read()
        soup = bs4.BeautifulSoup(html_volume)
        html_content = soup.findAll('tr')
        for arg in html_content[3:]:
            author = ""
            title = ""
            start_page = 0
            ref_article = ""
            text = bs4.BeautifulSoup(str(arg).strip('&nbsp;'))
            if text.i:
                if text.i.string == " ":
                    author = ""
                else:
                    author = text.i.string
                href = [arg for arg in text.find_all('a')]
                for arg in href:
                    title = str(href[0].contents[0]).strip('/\n')
                    start_page = href[1].contents[0]
                    ref_article = href[1].get('href')
                yield author, title, start_page, ref_article

    def get_content_volume_error(self):
        for vol, num, href in self.get_all_volume_link():
            try:
                content = list(site.get_content_volume(vol, num))
                print("T. %s,  No. %s \t OK!\t ref=%s" % (vol, num, href))
            except IndexError:
                print("Помилка при обробці журналу Т.", vol, " No.", num)
                if vol < 7:
                    yield vol
                else:
                    yield [vol, num]

    def get_article_content(self, volume, number):
        for url in self.get_content_volume(volume, number):
            article = self.get_volume_link(volume, number)[:-9] + url[3]
            text_url = article[:-4] + 'pdf'
            try:
                html_article = urlopen(article).read()
                html = bs4.BeautifulSoup(html_article)
            except Exception:
                print("Не можу відкрити адресу", article)
                html = bs4.BeautifulSoup("<html><head></head>"
                                         "<body></body></html>")
            title = url[1].replace('\n', ' ')
            if url[0]:
                authors = str(url[0]).split(',')
            else:
                authors = ""
            keywords = ""
            if html.keyword:
                if html.keyword.string:
                    keywords = html.keyword.string.split(';')
            abstract = ""
            if html.abstract:
                if html.abstract.string:
                    abstract = html.abstract.string.replace('\n', ' ')
            yield title, authors, keywords, abstract, text_url

    def get_article_content_error(self, volume_min, volume_max):
        for volume in range(volume_min, volume_max + 1):
            for number in [1, 2]:
                print("T. %s,  No. %s" % (volume, number))
                try:
                    content = list(self.get_article_content(volume, number))
                    print("OK!")
                except TypeError:
                    print("Error parsing T. %s,  No. %s" % (volume,
                                                            number))
                    yield [volume, number]
                    raise
                except InputError:
                    print("Не існуючий номер T. %s,  No. %s" % (volume,
                                                                number))

    def article_to_xml(self, volume, number):
        root = etree.Element("records")
        for (title, authors, keywords,
             abstract, text_url) in self.get_article_content(volume, number):
            record = etree.SubElement(root, "record")
            etree.SubElement(record, "title").text = title
            authors_tag = etree.SubElement(record, "authors")
            for arg in authors:
                etree.SubElement(authors_tag, "author").text = arg.lstrip()
            page_tuple = str(text_url).split('/')
            page_number = str(page_tuple[-1]).split('.')
            page_number_tuple = page_number[0].split('-')
            etree.SubElement(record, "startPage").text = page_number_tuple[0]
            etree.SubElement(record, "endPage").text = page_number_tuple[1]
            keywords_tag = etree.SubElement(record, "keywords")
            for arg in keywords:
                etree.SubElement(keywords_tag, "keyword").text = arg.lstrip()
            etree.SubElement(record, "abstract").text = abstract
            etree.SubElement(record, "fullTextUrl").text = text_url
        handle = etree.tostring(root, pretty_print=True, encoding='utf-8',
                                xml_declaration=True, with_comments=True)
        with open('xml/' + str(volume) + '_' +
                          str(number) + "-xml.xml", "a") as file:
            file.writelines(handle.decode())

    def list_volume_to_xml(self, volume_min, volume_max):
        # TODO Зробити затирання існуючих файлів
        for volume in range(volume_min, volume_max + 1):
            for number in [1, 2]:
                print("T. %s,  No. %s" % (volume, number))
                try:
                    self.article_to_xml(volume, number)
                    print("OK!")
                except TypeError:
                    print("Error parsing T. %s,  No. %s" % (volume,
                                                            number))
                    yield [volume, number]
                    raise
                except InputError:
                    print("Не існуючий номер T. %s,  No. %s" % (volume,
                                                                number))

if __name__ == "__main__":
    site_address = "http://matstud.org.ua/index.php/MatStud/issue/archive"
    site = MatStud(site_address)
    #print(list(site.get_article_content_error(36, 40)))
    #site.article_to_xml(40, 1)
    print(list(site.list_volume_to_xml(35, 40)))


