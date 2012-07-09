import xlrd
import csv
import datetime
import os
import os.path as op
import sys
import glob
import numpy as np

def find_calendar_based_files(base_folder, tag):
    filenames = glob.glob(op.join(base_folder, '*', tag + '*.csv'))
    filenames.sort()
    return filenames

def find_highest_volume_files(base_folder):
    dates = os.listdir(base_folder)
    filenames = []
    for adate in dates:
        fnames_adate = glob.glob(op.join(base_folder, adate, 'IF1*.csv'))
        fsize_adate = [op.getsize(fn) for fn in fnames_adate]
        filenames.append(fnames_adate[np.argmax(fsize_adate)])
    filenames.sort()
    return filenames

def get_header():
    header = ['date', 'time', 'lastprice', 'volume', 'cumvolume', 'oichange', 
            'bid1', 'bidsize1', 'bid2', 'bidsize2', 'bid3', 'bidsize3', 
            'ask1', 'asksize1', 'ask2', 'asksize2', 'ask3', 'asksize3',
            'lastdirection']
    return header
    

def read_csv_file(filename):
    ff = open(filename, 'r')
    reader  = csv.reader(ff)
    reader.next()
    rows = []
    for row in reader:
        newrow = [str(row[0]), str(row[1])] + \
            [float(row[colid]) for colid in range(2, 18)] + \
            [str(row[18])]
        rows.append(newrow)
    ff.close()
    return rows

def read_csv_file_list(filename_list):
    rows = [get_header()]
    for filename in filename_list :
        rows += read_csv_file(filename)
    return rows

def write_csv_file(data, output='/tmp/tmp.csv'):
    ff = open(output, 'w')
    csvwriter = csv.writer(ff)
    for row in data:
        csvwriter.writerow(row)
    ff.close() 
    return output

def main(inputdir, outputdir, option='highest_volume'): ## option in ['highest_volume', 'front', 'second', 'third', 'fourth']
    month = op.split(inputdir)[-1].replace('ZJ', '')
    if option == 'highest_volume':
        filename_list = find_highest_volume_files(inputdir)
        newfile_tag = 'IFHV_'
    elif option == 'front':
        filename_list = find_calendar_based_files(inputdir, 'IF16_')
        newfile_tag = 'IF16_'
    elif option == 'second':
        filename_list = find_calendar_based_files(inputdir, 'IF17_')
        newfile_tag = 'IF17_'
    elif option == 'third':
        filename_list = find_calendar_based_files(inputdir, 'IF18_')
        newfile_tag = 'IF18_'
    elif option == 'fourth':
        filename_list = find_calendar_based_files(inputdir, 'IF19_')
        newfile_tag = 'IF19_'
    else :
        raise "unknown option(%s); option in ['highest_volume', 'front', 'second', 'third', 'fourth']"%option
    
    newfilename = op.join(outputdir, newfile_tag + month + '.csv')
    print "Reading \n%s \n"%'\n'.join(filename_list)
    data = read_csv_file_list(filename_list)
    print "Writing %s ..."%newfilename
    write_csv_file(data, newfilename)
    print "Done."
                          
def print_options():
    print "python indexfut_csv_andrew.py input_dir output_dir option"
    print "option in ['highest_volume', 'front', 'second', 'third', 'fourth']"


if __name__ == '__main__':
    if len(sys.argv) < 4:
        print_options()
        sys.exit()
    input_dir = sys.argv[1]
    output_dir = sys.argv[2]
    option = sys.argv[3]
    main(input_dir, output_dir, option)
        
