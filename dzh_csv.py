import xlrd
import csv
import datetime
import os.path as op
import sys

DZH_INTRADAY_FILE='/home/mingyuan/Projects/DZH_data/cache/zs.xls'
DZH_DAILY_FILE='/home/mingyuan/Projects/DZH_data/cache/fx.xls'

DZH_DAILY_TARGET_DIR = '/home/mingyuan/Projects/DZH_data/Daily'
DZH_INTRADAY_TARGET_DIR = '/home/mingyuan/Projects/DZH_data/Intraday'


def read_intraday_file(filename):
    xls_file = xlrd.open_workbook(filename, encoding_override='gb18030')
    xls_sheet = xls_file.sheet_by_index(0)
    stock = str(xls_sheet.cell(0,0).value)
    rows = [['Time', 'Price']]
    for ii in range(2, xls_sheet.nrows):
        newrow = [str(xls_sheet.cell(ii,0).value).split('.')[0], float(xls_sheet.cell(ii,1).value)]
        rows.append(newrow)
    return stock, rows

def write_intraday_file(stock, data, output=''):
    timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    pathname = op.join(DZH_INTRADAY_TARGET_DIR, '_'.join([output, stock, timestamp]) + '.csv')
    ff = open(pathname, 'w')
    csvwriter = csv.writer(ff)
    for row in data:
        csvwriter.writerow(row)
    ff.close() 
    return pathname

def read_historical_intraday_file(filename):
    xls_file = xlrd.open_workbook(filename, encoding_override='gb18030')
    xls_sheet = xls_file.sheet_by_index(0)
    stock = str(xls_sheet.cell(0,1).value)
    rows = [['Datetime', 'Open', 'High', 'Low', 'Close', 'Volume', 'Amount']]
    cur_year = datetime.datetime.now().year
    pre_month = datetime.datetime.now().month
    for ii in range(2, xls_sheet.nrows):
        mdtime = str(xls_sheet.cell(ii,0).value).split('.')[0]
        if len(mdtime) < 8:
            mdtime = '0' + mdtime
        cur_month = int(mdtime[:2])
        if cur_month > pre_month:
            cur_year -= 1
        ymdtime = str(cur_year) + mdtime
        pre_month = cur_month
        newrow = [ymdtime] + [float(xls_sheet.cell(ii,jj).value) for jj in range(1, 7)]
        rows.append(newrow)
    return stock, rows    

def read_daily_file(filename):
    xls_file = xlrd.open_workbook(filename, encoding_override='gb18030')
    xls_sheet = xls_file.sheet_by_index(0)
    stock = str(xls_sheet.cell(0,1).value)
    rows = [['Date', 'Open', 'High', 'Low', 'Close', 'Volume', 'Amount']]
    for ii in range(2, xls_sheet.nrows):
        date = str(xls_sheet.cell(ii,0).value).split('.')[0]
        newrow = [date] + [float(xls_sheet.cell(ii,jj).value) for jj in range(1, 7)]
        rows.append(newrow)
    return stock, rows    

def write_daily_file(stock, data, output=''):
    timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    pathname = op.join(DZH_DAILY_TARGET_DIR, '_'.join([output, stock, timestamp]) + '.csv')
    ff = open(pathname, 'w')
    csvwriter = csv.writer(ff)
    for row in data:
        csvwriter.writerow(row)
    ff.close()
    return pathname

def print_options():
    print("Unknown option")
    print("Options need to be:")
    print("d: daily data")
    print("i: historical intraday data")
    print("t: top day intraday data")    


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print_options()
        sys.exit()
    option = sys.argv[1]
    if len(sys.argv) > 2:
        tag = sys.argv[2]
    else :
        tag = ''
    if option == 'd':
        print("Reading daily data....")
        stock, data = read_daily_file(DZH_DAILY_FILE)
        filename = write_daily_file(stock, data, tag)
        print("Daily data wrote to %s"%filename)
    elif option == 'i':
        print("Reading historical intraday data....")
        stock, data = read_historical_intraday_file(DZH_DAILY_FILE)
        filename = write_daily_file(stock, data, tag)
        print("Historical intraday data wrote to %s"%filename)
    elif option == 't':
        print("Reading top day intraday data....")
        stock, data = read_intraday_file(DZH_INTRADAY_FILE)
        filename = write_intraday_file(stock, data, tag)
        print("Top day intraday data wrote to %s"%filename)
    else :
        print_options()
        
        
