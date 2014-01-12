#/usr/bin/python
# -*- coding: utf-8 -*-
"""module for parsing matstud archive"""

import bs4
from urllib.request import urlopen


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
                yield arg.contents[0], arg.get('href')

    def get_volume_link(self, volume, number=1):
        """Функція вертає посилання на том volume, номер number журналу"""
        if number not in [1, 2]:
            raise InputError(number, "Невірний номер журналу!")
        for vol, href in self.get_all_volume_link():
            if volume > 6:
                name = str(vol).split(",")
                if str(volume) in name[0] and str(number) in name[1]:
                    return href
            else:
                if str(volume) in vol:
                    return href
        else:
            raise InputError(volume, "Невірний том журналу!")

    def get_content_volume(self, volume, number=1):
        """"Функція повертає зміст номеру журналу"""
        html_volume = urlopen(self.get_volume_link(volume, number)).read()
        soup = bs4.BeautifulSoup(html_volume)
        html_content = soup.findAll('tr')
        for arg in html_content[3:]:
            text = bs4.BeautifulSoup(str(arg).strip('&nbsp;'))
            author = [arg for arg in text.findAll('i')]
            href = [arg for arg in text.find_all('a')]
            author = author[0].contents[0]
            title = href[0].contents[0]
            start_page = href[1].contents[0]
            ref_article = href[1].get('href')
            yield author, title, start_page, ref_article


if __name__ == "__main__":
    site_address = "http://matstud.org.ua/index.php/MatStud/issue/archive"
    site = MatStud(site_address)
    site_address = site.get_volume_link(32, 1)
    print(site_address)
    print(list(site.get_content_volume(32, 1)))
