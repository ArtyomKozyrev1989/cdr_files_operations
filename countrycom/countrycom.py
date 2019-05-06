# coding=ansi
import json
import pandas as pd
import os
import time
import subprocess
import sys
import datetime

## we changed coding_type to ansi since I use cyrillic symbols in the file ##

def get_files_names_cwd():
    files = os.listdir()
    index = 1
    files_dict = {}
    k = 0
    for i in range(len(files)):
        if files[i].endswith("xls") or files[i].endswith("xlsx"):
            files_dict[str(k)] = files[i]
            k+=1
    return files_dict


def read_prices(prices_file):
    with open(prices_file, 'r') as f:
        line = f.read()
    if line:
        prices = json.loads(line)
    else:
        return None
    return prices


def ask_date():
    print("Please provide pricelist date in the following format day.month.year")
    while True:
        date = input("Date: ").strip()
        date_list = date.split('.')
        if len(date_list) > 3 or len(date_list) > 4:
            print("Incorrect date")
        else:
            try:
                day = int(date_list[0])
                month = int(date_list[1])
                year = int(date_list[2])
                datetime.date(year, month, day)
            except Exception as ex:
                print(f"Incorrect date")
            else:
                date = '.'.join([str(day).rjust(2, '0'), str(month).rjust(2, '0'), str(year)])
                return date
            
            
def change_destinations_names(row):
    dest = {
        'АО "КантриКом"':'Countrycom', 
        'Присоединенный оператор': 'PrisoedOperator',
        'Присоединенный оператор АО "СанСим"':'SanSim',
        'Присоединенный оператор ООО " Анлим-Нет"':'UnlimNet',
        'Присоединенный оператор ООО " Премиум Связь"':'PremiumSvyaz',
        'Присоединенный оператор ООО " Сипинформ"':'SIPINFORM' }
    for i in dest.keys():
        if row['TempCarrier'] == i:
            return dest[i]
        
        
def create_prices_column(row, prices):
    for i in prices.keys():
        if row['DestinationName'] == i:
            return prices[i]
    else:
        return 'UnknownPrice'

    
def create_price_column(row, date):
    return date
     
    
def main():
    if os.path.exists('countrycom_price.json'):
        print('The following list of files in folder:')
        files_cwd = get_files_names_cwd()
        for number, name in files_cwd.items():
            print('{} : {}'.format(number, name))
        while True:
            pricelist_filename_number = input('Please choose Coubtrycom pticelist number: ').strip()
            if pricelist_filename_number in files_cwd.keys():
                pricelist_filename = files_cwd[pricelist_filename_number]
                break
            else:
                print("Incorrect Input. Try again")
        date = ask_date()
        pinger = subprocess.Popen(["python", "pinger.py"])
        prices = read_prices('countrycom_price.json')
        data = pd.read_excel(pricelist_filename)
        data.columns =  ['TempCode', 'TempRange1', 'TempRange2', 'CallsNumber', 'TempCarrier']
        data['Code'] = data.apply(lambda x: "7{}".format(x['TempCode']), axis=1)
        data['Range'] = data.apply(
            lambda x: "{}-{}".format(str(x['TempRange1']).rjust(7, '0'), str(x['TempRange2']).rjust(7, '0')), axis=1)
        data['DestinationName'] = data.apply(change_destinations_names, axis=1)
        data['Price'] = data.apply(create_prices_column, axis=1, args=(prices,),)
        data['Date'] = data.apply(create_price_column, axis=1, args=(date,),)
        columns_to_delete = ["TempCode", "TempRange1", "TempRange2", "CallsNumber", "TempCarrier"]
        for i in columns_to_delete:
            del(data[i])
        data.to_excel("rebuilt_countrycom_price_{}.xlsx".format(date), index = False)
        pinger.kill()
        print("The program was successfully finished")
        time.sleep(10)
    else:
        print('There is no countrycom_price.json in the folder. Create the file.')
        time.sleep(10)


if __name__ == '__main__':
    try:
        main()
    except Exception as ex:
        print("The following unexpected error happened {}".format(ex))
        time.sleep(10)
        sys.exit()
