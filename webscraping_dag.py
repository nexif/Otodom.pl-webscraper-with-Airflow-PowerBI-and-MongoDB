from airflow import DAG
from airflow.exceptions import AirflowException
from airflow.operators.python_operator import PythonOperator
from airflow.hooks.base import BaseHook
from datetime import datetime
from pymongo import MongoClient
from typing import OrderedDict
from bs4 import BeautifulSoup
import requests
import pymongo
from pymongo import MongoClient
from collections import OrderedDict
import time
from datetime import date

conn_id = 'mongodb_conn'

districts_set = {'aleksandrow': 'Aleksandrów',
    'bemowo': 'Bemowo',
    'bialoleka': 'Białołęka',
    'bielany': 'Bielany',
    'centrum': 'Centrum',
    'metro-wilanowska': 'Metro Wilanowska',
    'mokotow': 'Mokotów',
    'ochota': 'Ochota',
    'praga-polnoc': 'Praga Północ',
    'praga-poludnie': 'Praga Południe',
    'rembertow': 'Rembertów',
    'srodmiescie': 'Śródmieście',
    'targowek': 'Targówek',
    'ursus': 'Ursus',
    'ursynow': 'Ursynów',
    'wawer': 'Wawer',
    'wilanow': 'Wilanów',
    'wesola': 'Wesoła',
    'wlochy': 'Włochy',
    'wola': 'Wola',
    'zoliborz': 'Żoliborz'}
districts = OrderedDict(sorted(districts_set.items()))

def is_successful_HTTP_response(resp):
    try: assert resp.status_code == 200
    except AssertionError as err: raise Exception(f'Assertion Error: Received response code:', resp.status_code)


def test_mongodb_connection():
    mongo_conn = BaseHook.get_connection(conn_id)
    try:
        client = MongoClient("mongodb+srv://{}:{}@cluster0.k1skitd.mongodb.net/?retryWrites=true&w=majority".format(mongo_conn.login, mongo_conn.password), 
                                serverSelectionTimeoutMS=300)
        print(client.server_info())
    except pymongo.errors.ServerSelectionTimeoutError as e:
        raise AirflowException(f'MongoDB connection error: {e}')

def run_webscraping():
    mongo_conn = BaseHook.get_connection(conn_id)
    client = MongoClient("mongodb+srv://{}:{}@cluster0.k1skitd.mongodb.net/?retryWrites=true&w=majority".format(mongo_conn.login, mongo_conn.password))
    db = client.test
    mongo = db.mieszkania # wybieramy kolekcję
    today = str(date.today()) # '2022-06-07'
    all_houses = []

    # Pobranie danych i transformacja
    for curr_district in districts:
        print('\nDzielnica:', districts[curr_district])
        page_no = 1

        while True:
            url = 'https://www.otodom.pl/pl/oferty/wynajem/mieszkanie/warszawa/{}?page={}'.format(curr_district, page_no)
            resp = requests.get(url)
            is_successful_HTTP_response(resp)
            source_code = resp.text

            soup = BeautifulSoup(source_code, 'html.parser')
            all_listings = soup.find_all("div", {"data-cy": "search.listing"})

            if len(all_listings) < 2:
                break

            all_listings = all_listings[1].find_all('li')
            listings_on_page = 0

            for item in all_listings:
                if item.find('a') is None: continue 

                house = OrderedDict()
                
                url = 'https://www.otodom.pl' + item.find('a')['href']
                house['id'] = url.split('-')[-1]
                house['name'] = item.find('a').find('article').find('div').find('h3')['title']
                house['url'] = url

                details = item.find_all('div')[1].find_all('span')
                if '€' in details[0].text:
                    house['price'] = float(details[0].text.replace('€', 'zł').replace(u'\xa0', u'').replace(u'\xc2', u'').replace(',', '.').split('zł')[0])
                    house['price'] = house['price']*4.5 # konwersja euro na zł
                else:
                    house['price'] = float(details[0].text.replace(u'\xa0', u'').replace(u'\xc2', u'').replace(',', '.').split('zł')[0])
                
                house['rooms'] = int(details[1].text.replace('+', '').replace(u'\xa0', u'').replace(u'\xc2', u'').split('pok')[0]) # raz pojawiło się "10+ pokoi"
                house['area'] = float(details[2].text.replace(u'\xa0', u'').replace(u'\xc2', u'').replace(',', '.').split('m')[0]) 
                house['address'] = item.find('a').find('article').find('p').find('span').text
                house['district'] = districts[curr_district]
                house['date_added'] = today
                house['date_ended'] = ''
                house['active'] = True

                all_houses.append(house)
                listings_on_page += 1

            print('Strona:', page_no, '| Wczytano:', listings_on_page, ' ofert')
            page_no += 1
            time.sleep(3)


    # Dodawanie ogłoszeń do bazy
    for house in all_houses:
        mongo.replace_one({'id': house['id']}, house, upsert=True) # Wstawia, jeśli dokument nie istnieje; pomija, jeśli istnieje

    # Oznaczanie nieaktywnych ogłoszeń poprzez flagę acitve = False
    inactive_count = 0
    active_ids = set(house['id'] for house in all_houses)

    for document in mongo.find({'active': True}):
        if document['id'] not in active_ids:
            mongo.update_one({'_id': document['_id']}, {'$set': {'active': False, 'date_ended': today}})
            inactive_count += 1

    if inactive_count > 0: print(inactive_count, 'ogłoszeń przestało być aktywnych')
    print('Obecnie w bazie mamy:', mongo.count_documents({}), 'ofert\nZ czego aktywnych jest:', mongo.count_documents({'active': True}))




with DAG(dag_id="otodom_webscraping_dag",
         start_date=datetime(2022, 6, 7),
         schedule_interval="@hourly",
         catchup=False) as dag:

    verify_mongodb_connection = PythonOperator(
        task_id='mongodb_connection',
        python_callable=test_mongodb_connection
    )
    webscraping = PythonOperator(
        task_id="run_webscraping",
        python_callable=run_webscraping
    )

verify_mongodb_connection >> webscraping
