import json
import pandas
import os
import time
import subprocess
import sys
import datetime


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
            
            
def convert_phone_range_to_two_rows_to_range(start, end):
    start = str(start)
    end = str(end)
    if start == end:
        return (start, "")
    for i in range(0, len(start)):
        if start[i] != end[i]:
            return start[0:i], "{}-{}".format(start[i:], end[i:])



def process_pricelist(pricelist_file, prices, date):
    pricelist = pandas.read_excel(pricelist_file)
    start_code = list(pricelist[pricelist.columns[0]])
    end_code = list(pricelist[pricelist.columns[1]])
    destinations = list(pricelist[pricelist.columns[2]])
    prices_symbol = list(pricelist[pricelist.columns[2]])
    excel_lines = []
    for index in range(0, len(start_code)):
        if str(start_code[index]).startswith('74'):
            if str(prices_symbol[index]) in prices.keys():
                prefix_row, range_row = convert_phone_range_to_two_rows_to_range(start_code[index], end_code[index])
                new_price_row = [prices[str(prices_symbol[index])]]
                line = [prefix_row] + [range_row] + [destinations[index]]  + new_price_row + [date]
                excel_lines.append(line)
    return excel_lines


def main():
    if os.path.exists('rostelecom_price.json'):
        print('The following list of files in folder:')
        files_cwd = get_files_names_cwd()
        for number, name in files_cwd.items():
            print('{} : {}'.format(number, name))
        while True:
            pricelist_filename_number = input('Please choose Rostelecom pticelist number: ').strip()
            if pricelist_filename_number in files_cwd.keys():
                pricelist_filename = files_cwd[pricelist_filename_number]
                break
            else:
                print("Incorrect Input. Try again")
        date = ask_date()
        #pinger = subprocess.Popen(["python", "pinger.py"])
        prices = read_prices('rostelecom_price.json')
        new_pricelist = process_pricelist(pricelist_filename, prices, date)
        df1 = pandas.DataFrame(new_pricelist, columns=['Code','Range','DestinationName','Price', 'Date'])
        df1.to_excel("rebuilt_rostelecom_price_{}.xlsx".format(date), index = False)
        #pinger.kill()
        print("The program was successfully finished")
        time.sleep(10)
    else:
        print('There is no rostelecom_price.json in the folder. Create the file.')
        time.sleep(10)

        
def main():
    try:
        if os.path.exists('rostelecom_price.json'):
            print('The following list of files in folder:')
            files_cwd = get_files_names_cwd()
            for number, name in files_cwd.items():
                print('{} : {}'.format(number, name))
            while True:
                pricelist_filename_number = input('Please choose Rostelecom pticelist number: ').strip()
                if pricelist_filename_number in files_cwd.keys():
                    pricelist_filename = files_cwd[pricelist_filename_number]
                    break
                else:
                    print("Incorrect Input. Try again")
            date = ask_date()
            pinger = subprocess.Popen(["python", "pinger.py"])
            prices = read_prices('rostelecom_price.json')
            new_pricelist = process_pricelist(pricelist_filename, prices, date)
            df1 = pandas.DataFrame(new_pricelist, columns=['Code','Range','DestinationName','Price', 'Date'])
            df1.to_excel("rebuilt_rostelecom_price_{}.xlsx".format(date), index = False)
            pinger.kill()
            print("The program was successfully finished")
            time.sleep(10)
        else:
            print('There is no rostelecom_price.json in the folder. Create the file.')
            time.sleep(10)
    except Exception as ex:
        print("The following unexpected error happened {}".format(ex))
        time.sleep(10)
        sys.exit()
            
        
if __name__ == '__main__':
    main()
