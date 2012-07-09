import numpy as np
import csv
import datetime
from collections import defaultdict

def readCSV(filename, date_name=None, date_format='%m/%d/%Y',
            time_name=None, time_format='%H:%M:%S',
            datetime_name=None, datetime_format='%m/%d/%Y %H:%M:%S',
            str_names=[]):
    """
    The script tries to read a csv file and returns numpy record array
    It assumes that there might be one date, time, datetime column and converts them to date,time,datetime objects
    It assumes the rest of the columns can be converted to float
    It assumes that some of the columns are strings
    It assumes that the first row is the header
    """
    f = open(filename, 'r')
    reader = csv.DictReader(f)
    result = defaultdict(list)
    for row in reader:
        for key in row.keys():
            result[key].append(row[key])
    namelist = []
    typelist = []
    if date_name is not None and date_name in result.keys():
        namelist.append(date_name)
        typelist.append(datetime.date)
        result[date_name] = [datetime.datetime.strptime(string, date_format).date() for string in result[date_name]]
    if time_name is not None and time_name in result.keys():
        namelist.append(time_name)
        typelist.append(datetime.time)
        result[time_name] = [datetime.datetime.strptime(string, time_format).time() for string in result[time_name]]
    if datetime_name is not None and datetime_name in result.keys():
        namelist.append(datetime_name)
        typelist.append(datetime.datetime)
        result[datetime_name] = [datetime.datetime.strptime(string, datetime_format) for string in result[datetime_name]]
    float_column_keys = [key for key in result.keys() if key not in str_names + [date_name, time_name, datetime_name]]
    
    namelist += str_names + float_column_keys
    typelist += ['|S1'] * len(str_names) + [float] * len(float_column_keys)
    dtypes = zip(namelist, typelist)
    for key in float_column_keys:
        result[key] = [float(item) for item in result[key]]

    rec = np.recarray((len(result.values()[0]),), dtype = dtypes)
    for key in namelist:
        rec[key] = np.array(result[key])
    f.close()
    return rec
            

