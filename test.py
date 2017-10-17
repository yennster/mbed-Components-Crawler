import xlrd
from xlutils.copy import copy
from distutils.dir_util import copy_tree
import os
import subprocess
import shutil
import stat
import glob
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

worksheet.write(0, 5, "Compiled for K64F?")
num_cols = sheet.ncols
num_rows = sheet.nrows
for row in range(1, num_rows):
    hello_world = sheet.cell(row, 2).value
    is_a_lib = sheet.cell(row, 3).value
    mbed_lib = sheet.cell(row, 4).value
    mbed_users = ["users/chris", "users/simon", "users/bridadan", "users/mbed_official", "users/sam_grove"]

    if is_a_lib:
        worksheet.write(row, 5, "LIBRARY")
        continue
    if any(user in hello_world for user in mbed_users): # not
        continue

    prg_name = hello_world.rsplit('/', 3)[-2]
    user_name = hello_world.split('/', 3)[-2]

    # If contents of cell = false, then begin subprocess calls
    if not mbed_lib:
        with open(user_name + "-" + prg_name + "-log.txt", "a") as log:
            print "Cloning " + prg_name + "..."
            os.system("hg clone " + base_url + hello_world)

            print "Removing old mbed file..."
            [os.remove(f) for f in glob.glob(prg_name + os.path.sep + "mbed*")]

            print "Copying mbed-os..."
            copy_tree("mbed", prg_name)

            print "Entering " + prg_name + " directory..."
            os.chdir(prg_name)

            # mbed config root .
            print "Running mbed deploy..."
            os.system("mbed deploy")

            print "Compiling " + prg_name + "..."
            compile_prg = subprocess.Popen("mbed compile -t ARM -m K64F", shell=True, stdout=log, stderr=log)

            compile_prg.wait()
            time.sleep(3)
            os.chdir("C:\Repos\Components")
            print "Removing " + prg_name + "..."
            shutil.rmtree(prg_name, onerror=onerror)

            log.write("\n----------------------------------------------------\n"
                      + "Program URL: " + base_url + hello_world + "\n" +
                      "----------------------------------------------------\n")

        read_log = open(user_name + "-" + prg_name + "-log.txt", "r")
        errors = any('[Error]' in line for line in read_log)
        if errors:
            worksheet.write(row, 5, "NO")
        else:
            worksheet.write(row, 5, "YES")

    workbook.save("mbed-components.xls")

workbook.save("mbed-components.xls")
