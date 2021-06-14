import os
import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from lxml import html
from sqlalchemy import create_engine
#import MySQLdb
import csv
import time
import random

#engine = create_engine("mysql+mysqldb://root:232061521161@localhost/parsing?charset=utf8mb4")
URL = 'https://career.habr.com/vacancies?divisions[]=backend&page=1&type=all'
HEADERS = {'user-agent': UserAgent().random}
HOST = 'https://career.habr.com'



def get_html(url, params=None):
    r = requests.get(url, headers=HEADERS, params=params)
    return r


def get_urls(html):
    return BeautifulSoup(html, 'html.parser')

def get_links(soup):
    vacansi_cards = soup.find_all('a', class_='vacancy-card__title-link')
    links = [HOST + card.attrs['href'] for card in vacansi_cards]
    return links

def parse_one_pages(link):
    html = get_html(link)
    if html.status_code == 200:
        soup = get_urls(html.text)
        name = soup.find('h1', class_='page-title__title').text
        class_content_section = soup.find_all('div', class_='content-section')
        salary = class_content_section[0]
        salary = salary.text.replace('Зарплата', '')
        salary = salary.replace('\n', ' ')
        requirements = class_content_section[1]
        requirements =  requirements.text.replace('Требуемые навыки', '')
        requirements = requirements.replace(' ·',',')
        specification = soup.find('div', class_='style-ugc')
        specification = specification.text
        specification = specification.replace('\n', ' ')
        note = [ name + ':::' + salary + ':::' + requirements + ':::' + specification]
        print(note)
        file_writer.writerow(note)
        #engine.execute(f"INSERT parsing.table1 (name, salary, requirements, specification) VALUES ('{name}', '{salary}', '{requirements}', '{specification}')")



def parse(url):
    html = get_html(url)
    if html.status_code == 200:
        soup = get_urls(html.text)
        links = get_links(soup)
        for link in links:
            time.sleep(random.randint(2, 7))
            parse_one_pages(link)
    else:
        print('Error')
        print(html.status_code)

with open("classmates.csv", mode="w", encoding='utf-8') as w_file:
    file_writer = csv.writer(w_file, delimiter=",", lineterminator="\n")
    for i in range(1, 75):
        parse(f'https://career.habr.com/vacancies?divisions[]=backend&divisions[]=frontend&divisions[]=apps&divisions[]=software&page={i}&type=all')


