#The script is designed to rebuild Spyder CDR files in more readable way and save them as a separate files,
#then the new files are searched through.

# To use the program for searching phone numbers in Spyder, you should do the following:
# 1. put the script in folder with CDRs .dat files 
# 2. create file number_list.txt with phone number you would like to serach for, please note that you should print one phone number
# per line and do not add whitesapces or other symbols to numbers
# 3. Run the script
# As a result you will have in the working folder:
# old CDR .dat files, rebuilt CDR .txt files, script file spider_reader.py,  number_list.txt, found_results.txt
# If you want to start new search with new files, you'll better delete found_results.txt and rebuilt CDR .txt files


import time
import os
import re
import sys


def convert_posix_time_to_standard(t):
    return time.ctime(int(t))


def rebuild_spider_file_line(line):
    rebuilt_line=""
    for element in line.split():
        if rebuilt_line == "":
            rebuilt_line += element
        else:
            if element.startswith('15') and len(element) == 10:
                rebuilt_line = ' '.join([rebuilt_line, convert_posix_time_to_standard(element)])
            elif len(element) > 20:
                pass # do not need to have such elements in rebuilt)line
            else:
                rebuilt_line = ' '.join([rebuilt_line, element])
    return rebuilt_line


def rebuild_spider_file(file_name):
    text = ""
    with open(file_name, mode='r', errors='ignore') as f:
        text = f.read()
    text = text.replace(r'\N', ' ')
    text = text.replace('\t', ' ')
    text = text.split('\n')
    with open('rebuilt_' + file_name.replace('.dat', '.txt'), 'a') as f:
        for line in text:
            f.write(rebuild_spider_file_line(line) + "\n")
            
            
def get_dat_files_list():
    all_files_in_cwd = os.listdir()
    dat_files_list = []
    for file in all_files_in_cwd:
        if file.endswith('.dat'):
            dat_files_list.append(file)
    return dat_files_list


def get_rebuild_files_list():
    all_files_in_cwd = os.listdir()
    rebuilt_files_list = []
    for file in all_files_in_cwd:
        if file.startswith('rebuilt'):
            rebuilt_files_list.append(file)
    return rebuilt_files_list


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


def write_searh_results_to_file(file_where_match_was_found, element):
    with open("found_results.txt", 'a') as f:
        f.write("{}: {} \n".format(file_where_match_was_found, element))
        
        
def nothing_was_found(file_where_match_wasnt_found, number_to_search):
    with open(file="found_results.txt", mode='a') as f:
        f.write("NO MATCHES FOUND FOR {} IN {}\n\n".format(number_to_search, file_where_match_wasnt_found))

        
def search_for_pattern(number, file_list):
    found_ip = []
    for file in file_list:
        with open(file, 'r') as f:
            text_of_file = f.read()
        results = re.findall(pattern="X.*{}.*".format(number), string=text_of_file)
        if results:
            for element in results:
                write_searh_results_to_file(file, element)
        else:
            nothing_was_found(file, number)
          
        
def main():
    t1 = int(round(time.time() * 1000))
    dat_files = get_dat_files_list()
    if len(dat_files) == 0:
        print("There are no .dat files in the current folder.")
        print("The program will be terminated in 3 seconds")
        time.sleep(3)
        sys.exit()
    else:
        for file in dat_files:
            if not os.path.exists('rebuilt_' + file.replace('.dat', '.txt')):
                    rebuild_spider_file(file)
    numbers_to_search_list = upload_number_list()           
    rebuilt_files = get_rebuild_files_list()
    for number in numbers_to_search_list:
            search_for_pattern(number, rebuilt_files)  
    print("The program completed fine!")
    print("Take found_results.txt from the current folder")
    print("If you want to repeat search, remove found_results.txt")
    t2 = int(round(time.time() * 1000))
    print(f"Job is done within {t2 - t1} miliseconds")
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
