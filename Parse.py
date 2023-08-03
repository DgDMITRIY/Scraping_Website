import codecs
import csv
import json
import re
import os

import random
from time import sleep

import requests
from bs4 import BeautifulSoup

headers = {
    "Accept": "*/*",
    "User-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 YaBrowser/23.5.4.674 Yowser/2.5 Safari/537.36"
}

for number_of_urls_in_this_segment in range(1, 12):
    urls_pages = "https://www.retail.ru/rbc/tradingnetworks/businesses/jewelry-retail/?CODE=diy-home-goods-furniture&hide_h1=Y&PAGEN_1=" + str(
        number_of_urls_in_this_segment)

    # этим мы показываем, что мы не бот, а обычный юзер (в Network в любом из методов GET копируем свой user_agent и accept)

    req = requests.get(urls_pages, headers=headers)

    # req возвращает результат работы метода get библиотеки requests, а именно принимает первым аргументом url,
    # вторым (но он не обязателен) аргументом заголовки

    src = req.text

    # сохраняем в переменную наш полученный объект и вызовем метод .text

    soup = BeautifulSoup(src, "lxml")
    name_of_segments = soup.find("div", class_="col-lg-9 col-md-8 left-colom").find("h1").text

    # сохраняем полученные данные в файл

    with open(f"pages_of_segment/{name_of_segments}_page-{number_of_urls_in_this_segment}.html", "w",
              encoding="utf-8") as file:
        file.write(src)

    with open(f"pages_of_segment/{name_of_segments}_page-{number_of_urls_in_this_segment}.html",
              encoding="utf-8") as file:
        src = file.read()

    # передаём в объект 'soup'

    all_companies = soup.find_all(class_="title")
    all_companies_hrefs = soup.find_all(class_="details")

    # создаём словарь для дальнейшего записывания данных о компаниях и выгрузки их в json-формат

    all_companies_dict = {}
    for item_companies, item_href_companies in zip(all_companies, all_companies_hrefs):
        item_companies_text = item_companies.text.strip("\n")
        item_companies_href_text = "https://www.retail.ru" + item_href_companies.get("href")
        all_companies_dict[item_companies_text] = item_companies_href_text

    # запись в json-файл

    with open(f"all_href_companies_of_{name_of_segments}_page-{number_of_urls_in_this_segment}.json", "w",
              encoding='utf-8') as file:
        json.dump(all_companies_dict, file, indent=4, ensure_ascii=False)

    # проверка данных json-файла

    with open(f"all_href_companies_of_{name_of_segments}_page-{number_of_urls_in_this_segment}.json",
              encoding='utf-8') as file:
        all_companies = json.load(file)

    # узнаём количество страниц рассматриваемого сегмента (переменная count)
    # указываем int, т.к. возвращает объект строки

    iteration_count = int(len(all_companies))
    print(f'Всего итераций {iteration_count}')
    count = 0

    table_head = ['Название компании',
                  'Телефон',
                  'E-mail',
                  'Сайт',
                  'VK',
                  'YouTube',
                  'О компании',
                  'Общая информация']

    with codecs.open('data/Рынок_России.csv', 'w', encoding='cp1251') as file:
        writer = csv.writer(file, delimiter=';')

        # принимает лишь один аргумент, поэтому делаем список или кортеж (метод .writerow())

        writer.writerow(
            [
                table_head[0],
                table_head[1],
                table_head[2],
                table_head[3],
                table_head[4],
                table_head[5],
                table_head[6],
                table_head[7]
            ]
        )

    for company_name, company_href in all_companies.items():

        rep = ["\"", "*"]
        for item in rep:
            if item in company_name:
                company_name = company_name.replace(item, '')
        req = requests.get(url=company_href, headers=headers)
        src = req.text
        # запись страниц в папку data. Счётчик count для перебора этих страниц
        with open(f"data/{company_name}.html", "w", encoding="utf-8") as file:
            file.write(src)

        with open(f"data/{company_name}.html", encoding="utf-8") as file:
            src = file.read()

        soup = BeautifulSoup(src, "lxml")

        # собираем данные о компаниях (почта, номер)
        try:
            companies_name = soup.find(class_="col-lg-9 col-md-8 left-colom").find('h1')
        except Exception:
            companies_name = ""
        if None is soup.find(class_="noShowPhone showPhone"):
            col_number = ""
        else:
            col_number = "Показать телефон"
        e_mail = soup.select("a.prop_item.email")
        if e_mail is None:
            e_mail = ""
        else:
            e_mail = BeautifulSoup("".join(map(str, soup.select("a.prop_item.email"))), "html.parser")
        try:
            web_site = BeautifulSoup(
                "".join(map(str, soup.find("div", class_="prop_item site").select('a[href^="https://"]'))),
                "html.parser")
        except Exception:
            web_site = ""
        try:
            soc_media_vk = BeautifulSoup(
                "".join(map(str, soup.find("div", {"class": "props_area"}).select('a[href^="https://vk.com/"]'))),
                "html.parser")
        except Exception:
            soc_media_vk = ""
        try:
            soc_media_you_tube = BeautifulSoup(
                "".join(
                    map(str, soup.find("div", {"class": "props_area"}).select('a[href^="https://www.youtube.com/"]'))),
                "html.parser")
        except Exception:
            soc_media_you_tube = ""
        try:
            soup.find(string=re.compile('О компании'))
            about_company = soup.find(string=re.compile('О компании')).find_next()
        except Exception:
            about_company = ""
        try:
            soup.find(string=re.compile('Общая'))
            total_info = soup.find(string=re.compile('Общая')).find_next()
        except Exception:
            total_info = ""

        data = [companies_name, col_number,
                e_mail, web_site, soc_media_vk, soc_media_you_tube,
                about_company, total_info]

        # получаем текст из них и записываем всё в список

        if type(data[0]) == str or None:
            companies_name_text = ""
        else:
            companies_name_text = data[0].text.strip()
        if data[1] == "" or type(data[1]) == str or type(data[1]) is None:
            col_number_text = ""
        else:
            col_number_text = data[1].text.strip()
        if type(data[2]) == str or None:
            e_mail_text = ""
        else:
            e_mail_text = data[2].text.strip()
        if type(data[3]) == str or None:
            web_site_text = ""
        else:
            web_site_text = data[3].text.strip()
        if type(data[4]) == str or None:
            soc_media_vk_text = ""
        else:
            soc_media_vk_text = data[4].text.strip()
        if type(data[5]) == str or None:
            soc_media_you_tube_text = ""
        else:
            soc_media_you_tube_text = data[5].text.strip()
        if data[6] == "" or type(data[6]) == str or type(data[6]) is None:
            about_company_text = ""
        else:
            about_company_text = data[6].text.strip()
        if data[7] == "" or type(data[7]) == str or type(data[7]) is None:
            total_info_text = ""
        else:
            total_info_text = data[7].text.strip()

        # дополняем наш csv-файл вытянутыми данными

        with codecs.open(f'data/Рынок_России.csv', 'a', encoding='cp1251', errors='ignore') as file:
            writer = csv.writer(file, delimiter=';')

            writer.writerow(
                [
                    companies_name_text,
                    col_number_text,
                    e_mail_text,
                    web_site_text,
                    soc_media_vk_text,
                    soc_media_you_tube_text,
                    about_company_text,
                    total_info_text
                ]
            )
        count += 1
        print(f"Итерация № {count}. Компания '{company_name}'")
        iteration_count -= 1
        os.remove(f"data/{company_name}.html")

        if iteration_count == 0:
            print(f"Работа завершена со страницей: {number_of_urls_in_this_segment}")
            print(f"Приступаем к странице №{number_of_urls_in_this_segment + 1}")
            break

        print(f"Осталось итераций: {iteration_count}")

        # делаем мелкий перерыв между итерациями

        sleep(random.randrange(2, 4))
