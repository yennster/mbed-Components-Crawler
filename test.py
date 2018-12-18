# to fix: https://os.mbed.com/components/PCA9685/ - mbed.bld in library, PR sent, might move to components
# to fix: https://os.mbed.com/components/SHT30-ARP-Analog-Humidity-Temperature-Se/ - example library points at user/private URL but
#   looks like there is a public version that is under teams/ (correct on component library link)
# to fix: https://os.mbed.com/components/SHT31-Analog-Humidity-Temperature-Sensor/ - example library points at user/private URL but
#   looks like there is a public version that is under teams/ (correct on component library link)
# to fix: https://os.mbed.com/components/10-Axis-Sensor-Data-Logger-with-microSD-/ - email to mac to fix
# to fix: https://os.mbed.com/components/MAXREFDES143-DeepCover-Embedded-Security/ - email to jimmy and james to investigate
#
# --prepare in linux, --build in windows?? symlink vs junction problem. WSL is really slow

import xlrd
from xlutils.copy import copy
from distutils.dir_util import copy_tree
import os
import subprocess
import shutil
import stat
import glob
import time

home_dir = os.getcwd()

def onerror(func, path, exc_info):
    if not os.access(path, os.W_OK):
        os.chmod(path, stat.S_IWUSR)
        func(path)
    else:
        raise

def clean():
    if os.path.exists(home_dir + '/components'):
        shutil.rmtree(home_dir + '/components')
    print 'components directory has been removed'

def prepare():
    # check for a clean system and setup if so
    if not os.path.exists(home_dir + '/components'):
        os.mkdir(home_dir + '/components')
        os.chdir(home_dir + '/components')
        os.system("mbed import mbed-os -vv")
    else:
        os.chdir(home_dir + '/components')
    
    book = xlrd.open_workbook("../mbed-components.xls")
    workbook = copy(book)
    sheet = book.sheet_by_name("Components")
    worksheet = workbook.get_sheet(0)

    worksheet.write(0, 5, "Clone and build?")
    worksheet.write(0, 6, "gcc_arm k64f")
    worksheet.write(0, 7, "armc5 k64f")
    worksheet.write(0, 8, "armc6 k64f")
    worksheet.write(0, 9, "iar k64f")
    worksheet.write(0, 10, "gcc_arm lpc1768")
    worksheet.write(0, 11, "armc5 lpc1768")
    worksheet.write(0, 12, "armc6 lpc1768")
    worksheet.write(0, 13, "iar lpc1768")

    num_rows = sheet.nrows
    for row in range(1, num_rows):
        hello_world = sheet.cell(row, 1).value
        is_a_lib = sheet.cell(row, 2).value
        prg_name = hello_world.rsplit('/', 3)[-2]
        # verify this is an application and if a duplicate, just skip becuase we've already
        #   cloned and built this once before
        if is_a_lib == "APP" and not os.path.exists(home_dir+'/components/'+prg_name):
            worksheet.write(row, 5, "YES, CLONE APP")
            os.mkdir(home_dir + '/components/' + prg_name)
            os.chdir(home_dir + '/components/' + prg_name)
            
            print '---'
            print ("hg clone " + hello_world)
            os.system("hg clone " + hello_world)
            print "Removing old mbed file..."
            [os.remove(f) for f in glob.glob(prg_name + os.path.sep + "mbed*")]
            print "Copying mbed-os..."
            
            if os.name is 'posix':
                os.symlink(home_dir + "/components/mbed-os", home_dir + '/components/' + prg_name + '/' + prg_name + '/mbed-os')
            else:
                import ntfsutils.junction as junction
                junction.create(home_dir + "/components/mbed-os", home_dir + '/components/' + prg_name + '/' + prg_name + '/mbed-os')

            print "Entering " + prg_name + " directory..."
            os.chdir(prg_name)

            # mbed config root .
            f = open('.mbed', 'w')
            f.write("ROOT=.")
            f.close()
            os.system("mbed deploy -vv")
        
        else:
            os.chdir(home_dir)
            worksheet.write(row, 5, "NO, SKIPPED LIBRARY")
        
        os.chdir(home_dir)
        workbook.save("mbed-components.xls")

    os.chdir(home_dir)
    workbook.save("mbed-components.xls")

def build():
    os.chdir(home_dir)

    book = xlrd.open_workbook("mbed-components.xls")
    workbook = copy(book)
    sheet = book.sheet_by_name("Components")
    worksheet = workbook.get_sheet(0)

    num_rows = sheet.nrows
    for row in range(1, num_rows):
        hello_world = sheet.cell(row, 1).value
        is_a_lib = sheet.cell(row, 2).value
        prg_name = hello_world.rsplit('/', 3)[-2]
        # verify this is an application and if a duplicate, just skip becuase we've already
        #   cloned and built this once before
        if is_a_lib == "APP" and os.path.exists(home_dir + '/components/' + prg_name):
            print "Entering " + prg_name + " directory..."

            target_list = ['k64f', 'lpc1768']
            compiler_list = ['gcc_arm', 'arm', 'armc6', 'iar']
            target_toolchain_cnt = 0
            for target in target_list:
                for compiler in compiler_list:
                    target_toolchain_cnt += 1
                    os.chdir(home_dir + '/components/' + prg_name + '/' + prg_name)
                    with open("../" + compiler + target + prg_name + "-log.txt", "w") as log:
                        if os.path.getsize("../" + compiler + target + prg_name + "-log.txt") < 100:
                            print "Compiling " + compiler + target + prg_name + "..."
                            compile_time = time.time()
                            compile_prg = subprocess.Popen("mbed compile -t " + compiler + " -m " + target, shell=True, stdout=log, stderr=log)
                            compile_prg.wait()
                            print("--- %s seconds ---" % (time.time() - compile_time))
                        else:
                            print "Compiling skipped, already built"
                        log.close()
                        
                    with open("../" + compiler + target + prg_name + "-log.txt", "r") as log:
                        if os.path.getsize("../" + compiler + target + prg_name + "-log.txt") > 0:
                            error = any('ERROR:' in line for line in log)
                            error = error or any('[Error]' in line for line in log)
                            print (str(target_toolchain_cnt) + " FAIL") if error else (str(target_toolchain_cnt) + " PASS")
                            os.chdir(home_dir)
                            worksheet.write(row, 5 + target_toolchain_cnt, "BUILD WITH ERRORS" if error else "BUILD SUCCESSFUL")
                        
                        log.close()
        else:
            os.chdir(home_dir)
            worksheet.write(row, 5, "NO, SKIPPED LIBRARY")
        
        os.chdir(home_dir)
        workbook.save("mbed-components.xls")

    os.chdir(home_dir)
    workbook.save("mbed-components.xls")

if __name__ == "__main__":
    start_time = time.time()
    
    import argparse
    parser = argparse.ArgumentParser(description='Option are prepare or build')
    parser.add_argument('--build', action='store_true', help='builds all programs in a prepared environment')
    parser.add_argument('--prepare', action='store_true', help='download and deploy all the programs')
    parser.add_argument('--clean', action='store_true', help='delete all artifacts from previous runs')

    args = parser.parse_args()

    if args.clean:
        clean()

    if args.prepare:
        prepare()
    
    if args.build:
        build()

    if not args.clean and not args.prepare and not args.build:
        print "no arguemts, performing a full clean, prepare and build"
        #clean()
        #prepare()
        #build()

    
    print("--- %s seconds ---" % (time.time() - start_time))
