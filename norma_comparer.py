# NOTE: you need pandas and xlrd

# To use the program do the following
# 1. Name uploaded from Norma database file norma
# 2. Write phonenumber you gonna searching in number_list.txt files, ! one phonenumber per line
# 3. Pur CDRs files, norma file, number_list.txt file and the script in one folder
# 4. Run the script file
# 5. The results will be in console window and in found_results.txt file


import re
import os
import time
import sys
import pandas
import ipaddress


def improve_view_n(string_to_improve):
    string_to_improve = string_to_improve.split(',')
    improved_string = ""
    for i in string_to_improve:
        if i != "":
            improved_string = improved_string + i + "  "
    return improved_string


def upload_number_list():
    numbers = []
    try:
        with open(file="number_list.txt", mode="r") as f:
            for i in f:
                numbers.append(i.strip("\\\n"))
    except FileNotFoundError:
        print("number_list.txt file does not exist or corrupted.\n\n")
        print("The program will be terminated in 5 seconds")
        time.sleep(5)
        sys.exit()
    return numbers


def search_for_pattern(number):
    found_ip = []
    our_files = ('x.py', "found_results.txt", "number_list.txt", 'norma.xls')
    list_files = os.listdir()
    for file_name in list_files:
        if file_name not in our_files:
        #if file_name.startswith("MSK"):
            with open(file=file_name, mode='r') as f:
                text_of_file = f.read()
                results = re.findall(pattern=f",,,,,.*{number}.*,", string=text_of_file)
                if results:
                    for element in results:
                        write_searh_results_to_file(file_name, element)
                        element = improve_view_n(element).split()
                        for subeleement in element:
                            try:
                                ipaddress.IPv4Address(subeleement)
                            except ipaddress.AddressValueError:
                                pass
                            else:
                                found_ip.append(subeleement)
                else:
                    nothing_was_found(file_name, number)
    return found_ip


def write_searh_results_to_file(file_where_match_was_found, element):
    with open(file="found_results.txt", mode='a') as f:
        f.write(f"{file_where_match_was_found}: {improve_view_n(element)} \n")


def nothing_was_found(file_where_match_wasnt_found, number_to_search):
    with open(file="found_results.txt", mode='a') as f:
        f.write(f"NO MATCHES FOUND FOR {number_to_search} IN {file_where_match_wasnt_found}\n\n")


def check_if_ip_in_norma(ip, trunk_names):
    line_which_contains_ip = []
    for line in trunk_names:
        if ip in line:
            line_which_contains_ip.append(line)
    if line_which_contains_ip == []:
        line_which_contains_ip.append(f"Norma does not contain information about {ip}")
    return line_which_contains_ip


def main():
    found_ip_lists = []
    found_ip_list = []
    if "norma.xls" not in os.listdir():
        print("norma.xls file was not found in the current directory")
        print("The program will be terminated")
        sys.exit()
        time.sleep(3)
    normafile = pandas.read_excel('norma.xls', skiprows=2, header=None)
    trunk_names = normafile[2]
    numbers_to_search_list = upload_number_list()
    for i in numbers_to_search_list:
        found_ip_lists.append(search_for_pattern(i))
    for i in found_ip_lists:
        found_ip_list += i
    print(set(found_ip_list))
    time.sleep(4)
    for ip in set(found_ip_list):
        print(f"{check_if_ip_in_norma(ip, trunk_names)}\n")
    print("The program completed fine!")
    print("Take found_results.txt from the current folder")
    print("If you want to repeat search, remove found_results.txt")
    time.sleep(90)
    print("Bye!")
    time.sleep(1)


if __name__ == '__main__':
    try:
        main()
    except Exception as ex:
        print("The following error happened:")
        print(ex)
        time.sleep(20)
