import xlrd
import os
import subprocess
import shutil
import time

os.chdir("C:\Repos\Components")
book = xlrd.open_workbook("mbed-components.xls")
worksheet = book.sheet_by_name("Components")
base_url = "https://developer.mbed.org"

num_cols = worksheet.ncols
num_rows = worksheet.nrows
count = 0
for row in range(1, num_rows):
    mbed_lib = worksheet.cell(row, 3).value
    hello_world = worksheet.cell(row, 2).value
    if worksheet.cell(row, 2) == xlrd.XL_CELL_EMPTY:
        continue
    prg_name = hello_world.rsplit('/', 3)[-2]
    clone_url = "hg clone " + base_url + hello_world
    rm_mbed = "del /f " + '.\\' + prg_name + '.\\' + "mbed.*"
    copy_mbed = "xcopy " + '.\\' + "mbed " + '.\\' + prg_name + " /s /e /h"
    prg_dir = '.\\' + prg_name
    compiling = "mbed compile -t ARM -m K64F"
    mbed_deploy = "mbed deploy"

    # If contents of cell = false, then begin subprocess calls
    if not mbed_lib: #os.system(clone_url)
        clone_output = ""
        log = open(prg_name + "-log.txt", "a")

        print "Cloning " + prg_name + "..."
        try:
            clone_output = subprocess.check_output(clone_url, shell=True, stderr=log)
        except:
            print clone_output

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
        compile_prg = subprocess.call(compiling, shell=True, stdout=log, stderr=log)

        time.sleep(1)
        os.chdir("C:\Repos\Components")
        print "Removing " + prg_name + "..."
        shutil.rmtree(prg_name)

        count += 1
        if count >= 10:
            break