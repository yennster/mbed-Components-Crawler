import xlrd
from xlutils.copy import copy
import os
import subprocess
import shutil
import stat
import time

def onerror(func, path, exc_info):
    if not os.access(path, os.W_OK):
        os.chmod(path, stat.S_IWUSR)
        func(path)
    else:
        raise

os.chdir("C:\Repos\Components")
book = xlrd.open_workbook("mbed-components.xls")
workbook = copy(book)
sheet = book.sheet_by_name("Components")
worksheet = workbook.get_sheet(0)
base_url = "https://developer.mbed.org"

worksheet.write(0, 5, "Compiled?")
num_cols = sheet.ncols
num_rows = sheet.nrows
count = 0
for row in range(18, num_rows):
    hello_world = sheet.cell(row, 2).value
    is_a_lib = sheet.cell(row, 3).value
    mbed_lib = sheet.cell(row, 4).value

    if sheet.cell(row, 2) == xlrd.XL_CELL_EMPTY:
        continue
    if is_a_lib:
        worksheet.write(row, 5, "LIBRARY")
        continue

    mbed_users = ["users/chris", "users/simon", "users/bridadan", "users/mbed_official"]
    if not any(user in hello_world for user in mbed_users):
        continue

    #  users/chris, users/simon, users/bridadan, users/mbed_official
    prg_name = hello_world.rsplit('/', 3)[-2]
    clone_url = "hg clone " + base_url + hello_world
    rm_mbed = "del /f " + '.\\' + prg_name + '.\\' + "mbed*"
    copy_mbed = "xcopy " + '.\\' + "mbed " + '.\\' + prg_name + " /s /e /h"
    prg_dir = '.\\' + prg_name
    compiling = "mbed compile -t ARM -m K64F"
    mbed_deploy = "mbed deploy"

    # If contents of cell = false, then begin subprocess calls
    if not mbed_lib: #os.system(clone_url)
        with open(prg_name + "-log.txt", "a") as log:
            log.write("\n----------------------------------------------------\n"
                      + "Program URL: " + base_url + hello_world + "\n" +
                      "----------------------------------------------------\n")

            print "Cloning " + prg_name + "..."
            subprocess.check_output(clone_url, shell=True, stderr=log)

            print "Removing old mbed file..."
            subprocess.check_output(rm_mbed, shell=True, stderr=log)

            print "Copying mbed-os..."
            subprocess.check_output(copy_mbed, shell=True, stderr=log)

            print "Entering " + prg_name + " directory..."
            os.chdir(prg_dir)

            # mbed config root .
            print "Running mbed deploy..."
            subprocess.check_output(mbed_deploy, shell=True, stderr=log)

            print "Compiling " + prg_name + "..."
            #compile_prg = subprocess.call(compiling, shell=True, stdout=log, stderr=log)
            compile_prg = subprocess.Popen(compiling, shell=True, stdout=log, stderr=log)

            compile_prg.wait()
            time.sleep(3)
            os.chdir("C:\Repos\Components")
            print "Removing " + prg_name + "..."
            shutil.rmtree(prg_name, onerror=onerror)

        read_log = open(prg_name + "-log.txt", "r")
        errors = any('[Error]' in line for line in read_log)
        if errors:
            worksheet.write(row, 5, "NO")
        else:
            worksheet.write(row, 5, "YES")

    workbook.save("mbed-components.xls")

    count += 1
    if count >= 15:
        break

workbook.save("mbed-components.xls")