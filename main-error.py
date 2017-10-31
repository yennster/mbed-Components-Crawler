import xlrd
from xlutils.copy import copy
from xlwt import *
from distutils.dir_util import copy_tree
import os
import subprocess
import shutil
import stat
import glob
import time
import requests
from bs4 import BeautifulSoup

def onerror(func, path, exc_info):
    if not os.access(path, os.W_OK):
        os.chmod(path, stat.S_IWUSR)
        func(path)
    else:
        raise

def progress(count, total, status):
    percentage = round(100.0 * count / float(total), 1)
    percent = '[' + '{0}%'.format(percentage) + ']: '
    print(percent + status)

book = xlrd.open_workbook("mbed-components.xls")
workbook = copy(book)
sheet = book.sheet_by_name("Components")
worksheet = workbook.get_sheet(0)
base_url = "https://os.mbed.com"

worksheet.write(0, 8, "K64F main.cpp Errors?")
num_cols = sheet.ncols
num_rows = sheet.nrows
for row in range(1, num_rows):
    hello_world = sheet.cell(row, 2).value
    is_a_lib = sheet.cell(row, 3).value
    mbed_lib = sheet.cell(row, 4).value

    if is_a_lib:
        worksheet.write(row, 8, "-")
        continue
    if mbed_lib:
        worksheet.write(row, 8, "-")
        continue

    prg_name = hello_world.rsplit('/', 3)[-2]
    user_name = hello_world.split('/', 3)[-2]

    read_log = open("./K64F-logs/" + user_name + "-" + prg_name + "-log.txt", "r")
    errors = any('[Error] main.cpp' in line for line in read_log)
    if errors:
        worksheet.write(row, 8, True)
    else:
        worksheet.write(row, 8, False)


    workbook.save("mbed-components.xls")
    progress(row, num_rows - 1, hello_world)

workbook.save("mbed-components.xls")
