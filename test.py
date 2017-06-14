import xlrd
import os
import subprocess

book = xlrd.open_workbook("mbed-components.xls")
worksheet = book.sheet_by_name("Components")
base_url = "https://developer.mbed.org"

num_cols = worksheet.ncols
num_rows = worksheet.nrows
count = 0
FNULL = open(os.devnull, 'w')
for row in range(1, num_rows):
    mbed_lib = worksheet.cell(row, 3).value
    hello_world = worksheet.cell(row, 2).value
    if worksheet.cell(row, 2) == xlrd.XL_CELL_EMPTY:
        continue
    prg_name = hello_world.rsplit('/', 3)[-2]
    clone_url = "hg clone " + base_url + hello_world
    rm_mbed = "del /f " + '.\\' + prg_name + '.\\' + "mbed.*"
    rm_mbed_dash = "del /f " + '.\\' + prg_name + '.\\' + "mbed-*.*"
    copy_mbed = "xcopy " + '.\\' + "mbed " + '.\\' + prg_name + " /s /e /h"
    prg_dir = '.\\' + prg_name
    compiling = "mbed compile -t ARM -m K64F"
    rm_dir = "del /s /q /f .\\" + prg_name + ".\\mbed-os.\\*.*"
    rm_hg = "del rmdir /s /q hg"
    mbed_deploy = "mbed deploy"

    # If contents of cell = false, then begin subprocess calls
    if not mbed_lib: #os.system(clone_url)
        clone_output = ""

        log = open("log.txt", "a")
        errors = open("errors.txt", "a")

        print "Cloning " + prg_name + "..."
        try:
            clone_output = subprocess.check_output(clone_url, shell=True, stderr=errors)
        except:
            print clone_output

        print "Removing old mbed file..."
        subprocess.check_output(rm_mbed, shell=True, stderr=errors)
        #subprocess.check_output(rm_mbed_dash, shell=True, stderr=errors)

        print "Copying mbed-os..."
        subprocess.check_output(copy_mbed, shell=True, stderr=errors)

        print "Entering " + prg_name + " directory..."
        os.chdir(prg_dir)

        compile_errors = open("errors.txt", "a")
        compile_log = open("log.txt", "a")

        # mbed config root .
        print "Running mbed deploy..."
        subprocess.check_output(mbed_deploy, shell=True, stderr=compile_errors)

        print "Compiling " + prg_name + "..."
        subprocess.call(compiling, shell=True, stdout=compile_log, stderr=compile_errors)

        os.chdir("C:\Users\jenplu01\PycharmProjects\mbed-web-crawler")

        print "Removing mbed-os..."
        subprocess.check_output(rm_dir, shell=True, stderr=compile_log)

        count += 1
        if count >= 2:
            break