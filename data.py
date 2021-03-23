import numpy as np
import os
import os.path
import json
from datetime import datetime, timedelta
import math

def make_data(filepath, start_time, end_time, location, avg=True):
    rssi_list = []
    time_list = []
    tash_list = []
    pre_time = datetime(2021,1,1)

    with open(filepath, 'r') as st_json :
        #print('\n', filepath)
        for json_str in st_json:
            check_start = json_str.find('{')
            check_end = json_str.find('}')
            if check_start < 0 or check_end < 0 :
                continue
            json_str_value = json_str[check_start:check_end+1]
            st_python = json.loads(json_str_value)
            if location :
                if st_python['loc'] != location :
                    return None
            test_time = datetime.strptime(st_python['time'], "%Y-%m-%d %H:%M:%S.%f")
            if start_time and end_time :
                if test_time < start_time or test_time > end_time :
                    continue
            test_time = test_time.replace(microsecond=0)
            if test_time < pre_time :
                print('\n===== time error =====')
                print(json_str)
                print(pre_time)
                print(test_time)
            pre_time = test_time

            find_tash = json_str.find('TASH')
            if find_tash < 0 :
                is_tash = False
            else :
                is_tash = True
            
            if avg :
                rssi_list = np.append(rssi_list, np.mean(st_python['rssi']))
                time_list.append(test_time)
                if is_tash :
                    tash_list.append(test_time)
            else :
                for i, rssi in enumerate(st_python['rssi']) :
                    temp_time = test_time - timedelta(seconds=len(st_python['rssi']) - i + 1)
                    time_list.append(temp_time)
                    rssi_list = np.append(rssi_list, rssi)
                    if is_tash :
                        tash_list.append(temp_time)

    #print("loc : %s , time size : %d , rssi size : %d"%(st_python['loc'], len(time_list), len(rssi_list)))
    temp_dic = {'loc':st_python['loc'], 'time_list':time_list, 'rssi':rssi_list, 'tash':tash_list}
    return temp_dic

def make_data_graph_info(data_list) :
    rssi_max, rssi_min = -100, 0
    time_max, time_min = datetime(2021,1,1), datetime(2031,1,1)
    new_data_list = []

    for data in data_list :
        if rssi_max < data['rssi'].max() :
            rssi_max = data['rssi'].max()
        if rssi_min > data['rssi'].min() :
            rssi_min = data['rssi'].min()
        if time_max < max(data['time_list']) :
            time_max = max(data['time_list'])
        if time_min > min(data['time_list']) :
            time_min = min(data['time_list'])

        find_data = False
        for new_data in new_data_list :
            if new_data['loc'] == data['loc'] :
                find_data = True
                new_data['time_list'].extend(data['time_list'])
                new_data['rssi'] = np.append(new_data['rssi'], data['rssi'])
        if find_data == False :
            new_data_list.append(data)
    graph_info = {'min_time':time_min, 'max_time':time_max, 'rssi_max':math.ceil(rssi_max), 'rssi_min':math.floor(rssi_min)}
    return new_data_list, graph_info

def make_data_list_top(input_path, info=None, location=None, avg=True):
    input_path_list = []
    folders = os.listdir(input_path)

    for foldername in folders :
        sub_foldername = os.path.join(input_path, foldername)
        input_path_list.append(sub_foldername)
    data_list, graph_info = make_data_list(input_path_list, info, location, avg)
    return data_list, graph_info

def make_data_list(input_path_list, info=None, location=None, avg=True):
    data_list = []    

    if info == None :
            start_time = None
            end_time = None
    else :
        start_time=info['start_time']
        end_time=info['end_time']

    for input_path in input_path_list :
        files = os.listdir(input_path)
        files.sort()
        for filename in files :        
            if filename.endswith('.log') :
                filepath = os.path.join(input_path, filename)
                temp_dic = make_data(filepath, start_time, end_time, location, avg)
                if not temp_dic :
                        continue
                data_list.append(temp_dic)

    data_list, graph_info = make_data_graph_info(data_list)
    graph_info['start_time'], graph_info['end_time'] = start_time, end_time
    return data_list, graph_info

def read_info(input_path) : 
    filepath = input_path + '/' + 'info.json'
    event_list = []
    if not os.path.exists(filepath) :
        return None

    with open(filepath, 'r') as st_json :
        print('\n filename : ', filepath)
        json_data = json.load(st_json)

        info_start_time = datetime.strptime(json_data['start_time'], "%Y-%m-%d %H:%M:%S")
        info_end_time = datetime.strptime(json_data['end_time'], "%Y-%m-%d %H:%M:%S")
        event_array = json_data.get('event')
        if event_array :
            for event in event_array :
                start_time = datetime.strptime(event['start_time'], "%Y-%m-%d %H:%M:%S")
                end_time = datetime.strptime(event['end_time'], "%Y-%m-%d %H:%M:%S")
                loc = event['loc']
                action = event['action']
                print("start_time %s , end_time %s , loc : %s , action : %s"
                    %(start_time.strftime("%Y/%m/%d %H:%M:%S"), end_time.strftime("%Y/%m/%d %H:%M:%S"), loc, action))
                temp_dic = {'start_time':start_time, 'end_time':end_time, 'loc':loc, 'action':action}
                event_list.append(temp_dic)
    
    info = {'start_time':info_start_time, 'end_time':info_end_time, 'event':event_list}
    return info