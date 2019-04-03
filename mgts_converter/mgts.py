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
    for i in range(len(files)):
        files_dict[str(i)] = files[i]
    return files_dict


def convert_phone_range_to_two_rows(line):
    line_to_lists = []
    for element in line.split('('):
        line_to_lists.append(element.split(')'))
    line_to_one_list = []
    for list_ in line_to_lists:
        line_to_one_list += list_
    return ["7" + line_to_one_list[1]+line_to_one_list[2], line_to_one_list[3]]



def read_prices(prices_file):
    with open(prices_file, 'r') as f:
        line = f.read()
    if line:
        prices = json.loads(line)
    else:
        return None
    return prices


def process_pricelist(pricelist_file, prices, date):
    pricelist = pandas.read_excel(pricelist_file)
    codes = list(pricelist[pricelist.columns[1]])
    destinations = list(pricelist[pricelist.columns[4]])
    prices_symbol = list(pricelist[pricelist.columns[5]])
    excel_lines = []
    for index in range(0, len(codes)):
        if str(codes[index]).startswith('(4'):
            if str(destinations[index]) != 'nan' and str(prices_symbol[index]) in prices.keys():
                new_dest_row = [str(destinations[index])+'_' + str(prices_symbol[index])]
                new_price_row = [prices[str(prices_symbol[index])]]
                line = convert_phone_range_to_two_rows(codes[index]) + new_dest_row  + new_price_row + [date]
                excel_lines.append(line)
    return excel_lines


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
                
                                       
def main():
    try:
        if os.path.exists('mgts_price.json'):
            print('The following list of files in folder:')
            files_cwd = get_files_names_cwd()
            for number, name in files_cwd.items():
                print('{} : {}'.format(number, name))
            while True:
                pricelist_filename_number = input('Please choose MGTS pticelist number: ').strip()
                if pricelist_filename_number in files_cwd.keys():
                    pricelist_filename = files_cwd[pricelist_filename_number]
                    break
                else:
                    print("Incorrect Input. Try again")
            date = ask_date()
            pinger = subprocess.Popen(["python", "pinger.py"])
            prices = read_prices('mgts_price.json')
            new_pricelist = process_pricelist(pricelist_filename, prices, date)
            df1 = pandas.DataFrame(new_pricelist, columns=['Code','Range','DestinationName','Price', 'Date'])
            df1.to_excel("rebuilt_mgts_price_{}.xlsx".format(date), index = False)
            pinger.kill()
            print("The program was successfully finished")
            time.sleep(10)
        else:
            print('There is no mgts_price.json in the folder. Create the file.')
            time.sleep(10)
    except Exception as ex:
        print("The following unexpected error happened {}".format(ex))
        time.sleep(10)
        sys.exit()

        
if __name__ == '__main__':
    main()
