# NOTE you need pandas, xlrd, openpyxl libraies
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
import datetime
import re
import openpyxl


def get_yesterday_date():
    yesterday = datetime.date.today() - datetime.timedelta(1)
    return '{}.{}.{}'.format(yesterday.year, str(yesterday.month).rjust(2,'0'), str(yesterday.day).rjust(2,'0'))


def convert_table_to_lines(table):
    result = []
    for table_line in table.index:
        line = ""
        for column_index in range(len(table.columns)-3):
            if line is not "":
                line = '*'.join([line, str(table[table.columns[column_index]][table_line])])
            else:
                line = str((table[table.columns[column_index]][table_line]))
        result.append(line)
    return result


def convert_audit_table_to_lines(table):
    result = []
    table = pd.read_excel(table)
    interested_columns = (table.Username, table.Details)
    for table_line in table.index:
        line = ""
        for column in interested_columns:
            if line is not "":
                line = '*'.join([line, str(column[table_line])])
            else:
                line = str(column[table_line])
        result.append(line)
    return result


def write_audit_search_results_to_excel(resultuser_removed, resultuser_added):
    resultuser_removed_for_excel = []
    for dataset in resultuser_removed:
        dataset = list(dataset)[0] + '*removed'
        dataset = dataset.split('*')
        resultuser_removed_for_excel.append(dataset)
    resultuser_added_for_excel = []    
    for dataset in resultuser_added:
        dataset = list(dataset)[0] + '*added'
        dataset = dataset.split('*')
        resultuser_added_for_excel.append(dataset)
    _columns=['Carrier', 'Destination', 'Product', 'User', 'Date', 'Action']   
    df1 = pd.DataFrame(resultuser_removed_for_excel + resultuser_added_for_excel, columns=_columns)
    df1.to_excel("file_difference_user.xlsx", index = False)


def compare_two_line_massives(massive1, massive2):
    result_removed = []
    result_added = []    
    for element in massive1:
        if element not in massive2:
            result_removed.append(element)
    for element in massive2:
        if element not in massive1:
            result_added.append(element)
    return result_removed, result_added


def compare_massives_write_tofile(result_removed, result_added):
    print("The following destinations was removed: \n\n")
    for i in result_removed:
        print(i)
    print("\nThe following destinations was added: \n\n")
    for i in result_added:
        print(i)
    with open("file_difference.txt", 'a') as f:
        f.write("The following destinations was removed: \n\n")
        for i in result_removed:
            f.write("{}\n".format(i))
        f.write("\nThe following destinations was added: \n\n")
        for i in result_added:
            f.write("{}\n".format(i))


def find_username_line(comp_line, audit_line):
    comp_line_list = comp_line.split('*')
    destination = comp_line_list[0]
    product = comp_line_list[2]
    mypattern = '.+{}.+{}'.format(product, destination)
    if re.search(pattern=mypattern, string=audit_line):
        return '*'.join([comp_line, audit_line.split('*')[0], get_yesterday_date()]) 
    
    
def find_epm_audit_pairs(result_removed, result_added, audit_lines):
    result_removed_with_user_full = []
    for result in result_removed:
        result_removed_with_user_local = []
        for line in audit_lines:
            userline = find_username_line(result, line)
            if userline:
                result_removed_with_user_local.append(userline)
        if not result_removed_with_user_local:
            result_removed_with_user_local.append(result + '*' + 'NoUserFound' + '*' + get_yesterday_date())
        if len(set(result_removed_with_user_local)) > 1:
            result_removed_with_user_local = []
            result_removed_with_user_local.append(result + '*' + 'SeveralUsersFound' + '*' + get_yesterday_date())
        result_removed_with_user_full.append(set(result_removed_with_user_local))
    result_added_with_user_full = []
    for result in result_added:
        result_added_with_user_local = []
        for line in audit_lines:
            userlineadd = find_username_line(result, line)
            if userlineadd:
                result_added_with_user_local.append(userlineadd)
        if not result_added_with_user_local:
            result_added_with_user_local.append(result + '*' + 'NoUserFound' + '*' + get_yesterday_date())
        if len(set(result_added_with_user_local)) > 1:
            result_added_with_user_local = []
            result_added_with_user_local.append(result + '*' + 'SeveralUsersFound' + '*' + get_yesterday_date())
        result_added_with_user_full.append(set(result_added_with_user_local))
    return result_removed_with_user_full, result_added_with_user_full


def find_epm_audit_pairs_write_tofile(resultuser_removed, resultuser_added):
    print("\nThe following destinations USERNAME was removed: \n\n")
    for elementset in resultuser_removed:
        for element in elementset:
            print(element)
    print("\nThe following destinations USERNAME was added: \n\n")
    for elementset in resultuser_added:
        for element in elementset:
            print(element)
    with open("file_difference_user.txt", 'a') as f:
        f.write("The following destinations USERNAME was removed: \n\n")
        for elementset in resultuser_removed:
            for element in elementset:
                f.write("{}\n".format(element))
        f.write("\nThe following destinations USERNAME was added: \n\n")
        for elementset in resultuser_added:
            for element in elementset:
                f.write("{}\n".format(element))


def get_epm_files_names():
    files = os.listdir()
    index = 1
    epm_files_dict = {}
    for i in range(len(files)):
        if files[i].startswith('EPM_INT_'):
            epm_files_dict[str(i)] = files[i]
    return epm_files_dict


def get_audit_file_name():
    files = os.listdir()
    for i in files:
        if i.startswith('Audit'):
            return i
    return None


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
    audit_filename = get_audit_file_name()
    epm_files_exist = show_dict_of_epm_files(epm_file_dict)
    print(audit_filename)
    if epm_files_exist and audit_filename is not None:
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
        result_removed, result_added = compare_two_line_massives(concatinated_group1, concatinated_group2)
        compare_massives_write_tofile(result_removed, result_added)
        audit_lines = convert_audit_table_to_lines(audit_filename)
        resultuser_removed, resultuser_added = find_epm_audit_pairs(result_removed, result_added, audit_lines) 
        find_epm_audit_pairs_write_tofile(resultuser_removed, resultuser_added)
        write_audit_search_results_to_excel(resultuser_removed, resultuser_added)
    elif epm_files_exist and audit_filename is None:
        print("There is no audit file in the current folder")
    elif not epm_files_exist and audit_filename is not None:
        print("There are no EPM files in the current folder")
    else:
        print("There is no audit file in the current folder")
        print("There are no EPM files in the current folder")
        
        
if __name__ == '__main__':
    try:
        main()
    except Exception as ex:
        print("The following unexpected error happened {}".format(ex))
    finally:
        print("The program is finihed and will be terminated in 20 seconds")
        time.sleep(20)
        sys.exit(0) 
