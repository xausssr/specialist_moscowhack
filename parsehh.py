import os
import requests
from bs4 import BeautifulSoup as BS
from fake_useragent import UserAgent
import csv
import time
import random

PAGE = 100
ADD = f'https://hh.ru/search/vacancy?specialization=1.221&area=1&items_on_page={PAGE}'
headers = {'user-agent': UserAgent().random}  
def ender_page():
    Request_hh = requests.get(ADD,headers=headers)
    soup_hh = BS(Request_hh.text, 'html.parser')
    paginator = soup_hh.find_all('span',{'class': "pager-item-not-in-short-range"})

    pages = []
    for page in paginator:
        pages.append(int(page.find('a').text))
    return pages[-1]
last_page = ender_page()
def extract_hh_jobs(last_page):
    jobs = [] 
    for page in range(last_page):
        result = requests.get(f'{ADD}&page={page}',headers=headers)
        soup = BS(result.text, 'html.parser')
        results = soup.find_all('div',{'class': 'vacancy-serp-item'})
        for result in results:
            jobs.append(result.find('a').get('href'))
    return jobs
jobs_link = extract_hh_jobs(last_page)
  

def parser():
    for link in range(9, len(jobs_link)):
        time.sleep(random.randint(2, 4))
        req = requests.get(jobs_link[link],headers=headers)
        req_hh = BS(req.text, 'html.parser')
        name_work = []
        name_comp = []
        opis = []
        moneys = []
        work = req_hh.find_all('div',{'class': "vacancy-title"})
        competention = req_hh.find_all('div',{'class': "bloko-tag bloko-tag_inline"})
        opis_o = req_hh.find_all('div',{'class': "g-user-content"})
        money = req_hh.find_all('span',{'class': "bloko-header-2 bloko-header-2_lite"})

        for worki in work:
            name_work.append(worki.find('h1').text)
            name_work_string = ''.join(name_work)
            for money_o in money:
                moneys.append(money_o.text)
                moneys_string = ''.join(moneys)
            for opis_a in opis_o:
                opis.append(opis_a.text)
                opis_string = ''.join(opis)
            for com in competention:
                name_comp.append(com.find('span').text)
                name_comp_string = ','.join(name_comp)
        note = [name_work_string + ':::' + moneys_string + ':::' + name_comp_string + ':::' + opis_string]
        file_writer.writerow(note)

with open ('classmates.csv', mode='w', encoding='utf-8') as w_file:
    file_writer = csv.writer(w_file, delimiter=',', lineterminator='\n')
    parser()

