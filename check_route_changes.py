# NOTE: you need pandas and xlrd libraies
# The script is  used to search for route changes in EPM INT files from database
# The option was made since database web interface is the 3rd party software
# To use the program copy paste the file and EPM files in one folder
# Then run the script
# Then choose files to compare, first group of files is compared with the second group of files

import pandas as pd
import os
import copy
import time
import sys


def convert_table_to_lines(table):
    result = []
    for table_line in table.index:
        line = ""
        for column_index in range(len(table.columns)-3):
            if line is not "":
                line = '***'.join([line, str(table[table.columns[column_index]][table_line])])
            else:
                line = str((table[table.columns[column_index]][table_line]))
        result.append(line)
    return result


def compare_two_line_massives(massive1, massive2):
    result = []
    for element in massive1:
        if element not in massive2:
            result.append(element)
    for element in massive2:
        if element not in massive1:
            result.append(element)
    return result


def get_epm_files_names():
    files = os.listdir()
    index = 1
    epm_files_dict = {}
    for i in range(len(files)):
        if files[i].startswith('EPM_INT_'):
            epm_files_dict[str(i)] = files[i]
    return epm_files_dict


def show_dict_of_epm_files(epm_files_dict):
    if len(epm_files_dict) == 0:
        print("There in no EPM Files in the working folder.")
        time.sleep(5)
        return False
    else:
        print("There are the following EPM files in the working folder:")
        for key, value in epm_files_dict.items():
            print("File Number: {} File Name {}".format(str(key), value))
        return True
    
    
def check_group_input(group, epm_files_dict):
    if len(group) > 0:
        choice_list = group.split(',')
        choice_list_strip = [] 
        for element in choice_list:
            choice_list_strip.append(element.strip())
        for element in choice_list_strip:
            if element not in epm_files_dict.keys():
                return False, None
        return True, choice_list_strip
    else:
        return False, None
    
    
def concatinate_epm_files(choice_list_strip, epm_files_dict):
    result = None
    for i in range(len(choice_list_strip)):
        if result is None:
            result = convert_table_to_lines(pd.read_excel(epm_files_dict[choice_list_strip[i]]))
        else: 
            result += convert_table_to_lines(pd.read_excel(epm_files_dict[choice_list_strip[i]]))
    return result


def main():
    epm_file_dict = get_epm_files_names()
    if show_dict_of_epm_files(epm_file_dict):
        while True:
            print("Please choose numbers for first group of files. Example: 1,26,44,55")
            group1 = input("First group: ")
            correct, choice_list_strip_group1 = check_group_input(group1, epm_file_dict)
            if correct:
                break
            else:
                print("You made incorrect files input")
        concatinated_group1 = concatinate_epm_files(choice_list_strip_group1, epm_file_dict)
        while True:
            print("Please choose numbers for second group of files. Example: 1,26,44,55")
            group2 = input("Second group: ")
            correct, choice_list_strip_group2 = check_group_input(group2, epm_file_dict)
            if correct:
                break
            else:
                print("You made incorrect files input")
        concatinated_group2 = concatinate_epm_files(choice_list_strip_group2, epm_file_dict)
        file_differences = compare_two_line_massives(concatinated_group1, concatinated_group2)
        print("The following difference between files were found: ")
        for i in file_differences:
            print(i)
        with open("file_difference.txt", 'a') as f:
            for i in file_differences:
                f.write("{}\n".format(i))
    else:
        print("Incorrect use of the program, you need to put EPM files in the folder.")
    

if __name__ == '__main__':
    try:
        main()
    except Exception as ex:
        print("The following unexpected error happened {}".format(ex))
    finally:
        print("The program is finihed and will be terminated in 20 seconds")
        time.sleep(20)
        sys.exit(0) 
