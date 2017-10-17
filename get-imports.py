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

worksheet.write(0, 7, "# of Imports")
num_cols = sheet.ncols
num_rows = sheet.nrows
for row in range(439, num_rows):
    hello_world = sheet.cell(row, 2).value

    if hello_world != "":
        is_a_lib = sheet.cell(row, 3).value
        has_mbed_os_lib = sheet.cell(row, 4).value

        repo_url = base_url + hello_world
        repo_page = requests.get(repo_url)
        repo_soup = BeautifulSoup(repo_page.content, 'html.parser')

        access_denied = repo_soup.find("h1", text="Access Denied")
        if not access_denied:
            num_imports = repo_soup.find("th", text="Imports:").find_next_sibling("td").text
            remove_icon = '<i class="fa icon_imports" aria-hidden="true"></i>'
            num_imports.encode('ascii', 'replace').replace(remove_icon, '')
            num_imports = ''.join(num_imports.split())
            worksheet.write(row, 7, int(num_imports))
        else:
            worksheet.write(row, 7, "ACCESS DENIED")
    else:
        worksheet.write(row, 7, "N/A")

    workbook.save("mbed-components.xls")
    progress(row, num_rows - 1, hello_world)

workbook.save("mbed-components.xls")
