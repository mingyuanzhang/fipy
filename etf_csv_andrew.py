import xlrd
import csv
import datetime
import os.path as op
import sys


def converter_loop_simple(reader):
    rows = []
    for row in reader:
        if len(row) > 19 or len(row) == 0:
            continue
        newrow = [str(row[0]), str(row[1])] + \
            [float(row[colid]) for colid in range(2, 18)] + \
            [str(row[18])]
        rows.append(newrow)
    return rows

def converter_loop_ampm(reader):
    rows = []
    def ampm_convert(ampm, timestamp):
        if ampm == 'AM':
            return timestamp
        else :
            hour = int(timestamp.split(':')[0]) + 12
            timestamp = str(hour) + timestamp[2:]
            return timestamp
    for row in reader:
        newrow = [str(row[0]), ampm_convert(str(row[1]), str(row[2]))] + \
            [float(row[colid]) for colid in range(3, 19)] + \
            [str(row[19])]
        rows.append(newrow)
    return rows

def read_xls_file(filename):
    ff = open(filename, 'r')
    reader  = csv.reader(ff, delimiter='\t')
    reader.next()
    rows = [['date', 'time', 'lastprice', 'volume', 'cumvolume', 'volumevalue', 
             'bid1', 'bidsize1', 'bid2', 'bidsize2', 'bid3', 'bidsize3', 
             'ask1', 'asksize1', 'ask2', 'asksize2', 'ask3', 'asksize3',
             'lastdirection']]
    #try:
    rows += converter_loop_simple(reader)
    #except:
    #    rows += converter_loop_ampm(reader)
    ff.close()
    return rows

def write_csv_file(data, output='/tmp/tmp.csv'):
    ff = open(output, 'w')
    csvwriter = csv.writer(ff)
    for row in data:
        csvwriter.writerow(row)
    ff.close() 
    return output

def main(filename, outputdir):
    newfilename = op.join(outputdir, op.split(filename)[-1].replace('.xls', '.csv'))
    print "Reading %s ..."%filename
    data = read_xls_file(filename)
    print "Writing %s ..."%newfilename
    write_csv_file(data, newfilename)
    print "Done."
                          
def print_options():
    print "python etf_csv_andrew.py input.xls output_dir"


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print_options()
        sys.exit()
    input_file = sys.argv[1]
    output_dir = sys.argv[2]
    main(input_file, output_dir)
        
