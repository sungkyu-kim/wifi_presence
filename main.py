import numpy as np
import os
import os.path
import json
import seaborn as sns
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import math

colors = {'PCroom':'g.', 'Living':'c.', 'Kitchen':'m.'}
colorstr = {'PCroom':'g', 'Living':'c', 'Kitchen':'m'}

FIGSIZE_X, FIGSIZE_Y = 25, 15

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

def draw_time_graph(data, graph_info, info=None, location=None) :
    legend_string = []

    plt.rcParams['figure.figsize'] = [FIGSIZE_X, FIGSIZE_Y]

    # draw graph
    for temp_dic in data :
        loc = temp_dic['loc']
        if location :
            if loc != location :
                continue
        legend_string = np.append(legend_string, loc)
        if loc in colors :
            color = colors[loc]
        else :
            color = 'k.'
        print('loc : %s , rssi length : %d'%(loc, len(temp_dic['rssi'])))
        plt.plot(temp_dic['time_list'], color)

    if graph_info['start_time'] :
        time_delta = timedelta(minutes=30)
        start_time = graph_info['start_time']
        end_time = graph_info['end_time']
        xline_time = start_time
    else :
        time_delta = timedelta(hours=6)
        start_time = graph_info['min_time']
        end_time = graph_info['max_time']
        xline_time = start_time.replace(hour=0, minute=0, second=0)

    #draw X line
    while xline_time <= end_time + time_delta :
        plt.axhline(y=xline_time, color='silver', linestyle='--', linewidth=1)
        xline_time = xline_time + time_delta
    '''
    # write event info
    if info :
        for event in info['event'] :
            start_time = event['start_time']
            loc = event['loc']
            action = event['action']
            event_text = ' loc : ' + loc + '\n act : ' + action
            if loc in colorstr :
                color = colorstr[loc]
            else :
                color = 'black'
            plt.text(start_time, graph_info['rssi_min']-1, event_text,
                verticalalignment='bottom', color=color)

    title = (start_time.strftime('%Y-%m-%d %H:%M') + ' ~ ' +
                end_time.strftime('%m-%d %H:%M') + ' , ' +
                'Wi-Fi Signal Variation')
    print('\n' + title)
    plt.title(title)
    '''   
    plt.xlabel('time')
    plt.ylabel('RSSI')
    plt.legend(legend_string, loc='upper right')
    plt.grid(True, axis='y', linestyle='--')
    #plt.yticks(np.arange(graph_info['rssi_min']-1, graph_info['rssi_max']+1))
    #plt.xticks([start_time, end_time])
    #figManager = plt.get_current_fig_manager()
    #figManager.window.showMaximized()
    plt.show()

def draw_rssi_graph(data, graph_info, info=None, location=None, tash=False) :
    legend_string = []

    plt.rcParams['figure.figsize'] = [FIGSIZE_X, FIGSIZE_Y]

    # draw graph
    for temp_dic in data :
        loc = temp_dic['loc']
        if location :
            if loc != location :
                continue
        legend_string = np.append(legend_string, loc)
        if loc in colors :
            color = colors[loc]
        else :
            color = 'k.'
        print('loc : %s , rssi length : %d'%(loc, len(temp_dic['rssi'])))
        plt.plot(temp_dic['time_list'], temp_dic['rssi'], color)

    if graph_info['start_time'] :
        start_time = graph_info['start_time']
        end_time = graph_info['end_time']
    else :
        start_time = graph_info['min_time']
        end_time = graph_info['max_time']

    # set time_delta
    gap_time = end_time - start_time
    if gap_time > timedelta(days=10) :
        time_delta = timedelta(days=1)
    elif gap_time > timedelta(days=6) :
        time_delta = timedelta(hours=12)
    elif gap_time > timedelta(days=3) :
        time_delta = timedelta(hours=6)
    elif gap_time > timedelta(days=1) :
        time_delta = timedelta(hours=3)
    elif gap_time > timedelta(hours=12) :
        time_delta = timedelta(hours=1)
    else :
        time_delta = timedelta(minutes=30)

    # write event info
    if info :
        if info['event'] :
            time_delta = timedelta(minutes=30)
            for event in info['event'] :
                start_time_event = event['start_time']
                loc = event['loc']
                action = event['action']
                event_text = ' loc : ' + loc + '\n act : ' + action
                if loc in colorstr :
                    color = colorstr[loc]
                else :
                    color = 'black'
                plt.text(start_time_event, graph_info['rssi_min']-1, event_text,
                    verticalalignment='bottom', color=color)

    # draw tash event
    if tash :
        for temp_dic in data :
            loc = temp_dic['loc']
            if location :
                if loc != location :
                    continue
            
            if loc in colors :
                color = colorstr[loc]
            else :
                color = 'black'
            tash_list = temp_dic['tash']
            for tash_time in tash_list :
                plt.axvline(x=tash_time, color=color, linestyle='--', linewidth=1)

    # draw X line
    xline_time = start_time.replace(hour=0, minute=0, second=0)
    while xline_time + time_delta <= start_time :
        xline_time = xline_time + time_delta

    while xline_time <= end_time + time_delta :
        plt.axvline(x=xline_time, color='silver', linestyle='--', linewidth=1)
        xline_time = xline_time + time_delta

    title = (start_time.strftime('%Y-%m-%d %H:%M') + ' ~ ' +
                end_time.strftime('%m-%d %H:%M') + ' , ' +
                'Wi-Fi Signal Variation')
    print('\n' + title)
    plt.title(title)
    plt.xlabel('time')
    plt.ylabel('RSSI')
    plt.legend(legend_string, loc='upper right')
    plt.grid(True, axis='y', linestyle='--')
    plt.yticks(np.arange(graph_info['rssi_min']-1, graph_info['rssi_max']+1))
    #plt.xticks([start_time, end_time])
    #figManager = plt.get_current_fig_manager()
    #figManager.window.showMaximized()
    plt.show()

def draw_fourier_graph(data, graph_info) :
    # Fourier Transform parameters
    fmax = 200      # sampling frequency 100 Hz
    dt = 1/fmax     # sampling period
    freq_strength = []
    x_index = []
    f_index = 2

    for temp_dic in data :
        loc = temp_dic['loc']
        avg_rssi = temp_dic['rssi']
        
        # perform Fourier transform without sorting
        N = len(avg_rssi)
        df = fmax/N     # df = 1/N = fmax/N
        freqs = np.arange(0,N)*df      # frq = [0, df, ..., (N-1)*df]
        freq_rssi = np.fft.fft(avg_rssi)*dt

        ## plotting for understanding visually
        freq_strength = np.append(freq_strength, np.abs(freq_rssi[f_index]))
        x_index = np.append(x_index, loc)

    plt.rcParams['figure.figsize'] = [FIGSIZE_X, FIGSIZE_Y]
    plt.bar(x_index, freq_strength)
    sns.set(font_scale = 1.4)
    plt.title('Wi-Fi Signal Strength at ' + str(freqs[f_index]) + ' Hz')
    plt.xlabel('frequency')
    plt.ylabel('Fourier(rssi)')
    plt.show()

def get_fourier_transform(rssi, f_index) :
    # Fourier Transform parameters
    fmax = 200      # sampling frequency 100 Hz
    dt = 1/fmax     # sampling period

    # perform Fourier transform without sorting
    N = len(rssi)
    df = fmax/N     # df = 1/N = fmax/N
    freqs = np.arange(0,N)*df      # frq = [0, df, ..., (N-1)*df]
    freq_rssi = np.fft.fft(rssi)*dt            
    freq_strength = np.abs(freq_rssi[f_index])
    return freq_strength, freqs[f_index]

def draw_fourier_graph_by_time(data, graph_info) :
    f_index_count = 9
    subplot_x, subplot_y = 3, 3
    freq_strength_list = []
    freqs_list = []
    x_index = []
    rssi_index = []
    freq_strength_max = 0

    for temp_dic in data :
        loc = temp_dic['loc']
        rssi = temp_dic['rssi']
        x_index = np.append(x_index, loc)
        rssi_index.append(rssi)

    for i in range(f_index_count):
        freq_strength_list_sub = []
        ## plotting for understanding visually
        f_index = i
        for j in range(0, len(rssi_index)) : 
            freq_strength, freqs = get_fourier_transform(rssi_index[j], f_index)
            freq_strength_list_sub = np.append(freq_strength_list_sub, freq_strength)
        freq_strength_list.append(freq_strength_list_sub)
        freqs_list.append(freqs)
        if freq_strength_max < freq_strength_list_sub.max() :
            freq_strength_max = freq_strength_list_sub.max()

    plt.rcParams['figure.figsize'] = [FIGSIZE_X, FIGSIZE_Y]
    fig = plt.figure()
    for i in range(f_index_count):
        fig.add_subplot(subplot_x, subplot_y, i+1)
        plt.bar(x_index, freq_strength_list[i])
        for j, v in enumerate(x_index):
            plt.text(v, freq_strength_list[i][j], round(freq_strength_list[i][j],4), 
                horizontalalignment='center', verticalalignment='bottom', fontsize=9, color='darkblue')
            if v == graph_info['loc'] :
                plt.text(v, freq_strength_list[i][j]/4, "★", 
                horizontalalignment='center', verticalalignment='bottom', color='red', fontsize=25)      
        #plt.ylim([0,freq_strength_max*1.1])
        plt.title('Wi-Fi Signal Strength at ' + str(round(freqs_list[i],4)) + ' Hz' + ' , f_index : %d'%(i))
        plt.ylabel('Fourier(rssi)')

    title = (graph_info['start_time'].strftime('%Y-%m-%d %H:%M:%S') + ' ~ ' + 
                graph_info['end_time'].strftime('%H:%M:%S') + ' , ' + 
                'Location : ' + graph_info['loc'] + ' , ' + 
                'Action : ' + graph_info['action'])
    print('\n' + title)
    plt.suptitle(title, fontsize=15)
    #figManager = plt.get_current_fig_manager()
    #figManager.window.showMaximized()
    plt.show()

def draw_fourier_graph_full(data, graph_info, data_len=100) :
    f_index_count = 6
    subplot_x, subplot_y = 6, 1
    freq_strength_list = []
    freqs_list = []
    time_list = []
    x_index = []
    rssi_index = []

    for temp_dic in data :
        loc = temp_dic['loc']
        rssi = temp_dic['rssi']
        time = temp_dic['time_list']
        x_index = np.append(x_index, loc)
        rssi_index.append(rssi)
        time_list.append(time)

    for i in range(f_index_count):
        freq_strength_list_sub = []
        ## plotting for understanding visually
        f_index = i
        for j in range(0, len(rssi_index)) : 
            freq_strength_temp_list = []
            for k in range(int(data_len/2), len(rssi_index[j]) - data_len) :
                freq_strength, freqs = get_fourier_transform(rssi_index[j][k:k+data_len], f_index)
                freq_strength_temp_list.append(round(freq_strength,4))
            freq_strength_list_sub.append(freq_strength_temp_list)
        freq_strength_list.append(freq_strength_list_sub)
        freqs_list.append(freqs)

    plt.rcParams['figure.figsize'] = [FIGSIZE_X, FIGSIZE_Y]
    fig = plt.figure()
    for i in range(f_index_count):
        fig.add_subplot(subplot_x, subplot_y, i+1)

        for j, loc in enumerate(x_index):
            color = colorstr[loc]
            plt.plot(time_list[j][int(data_len/2):len(freq_strength_list[i][j])+int(data_len/2)], freq_strength_list[i][j], color)
        
        for temp_dic in data :
            loc = temp_dic['loc']
            if loc in colors :
                color = colorstr[loc]
            else :
                color = 'black'
            tash_list = temp_dic['tash']
            for tash_time in tash_list :
                plt.axvline(x=tash_time, color=color, linestyle='--', linewidth=1)

        plt.title('Wi-Fi Signal Strength at ' + str(round(freqs_list[i],4)) + ' Hz' + ' , f_index : %d'%(i))
        plt.ylabel('Fourier(rssi)')
        plt.grid(True, axis='y', linestyle='--')

    title = (graph_info['start_time'].strftime('%Y-%m-%d %H:%M:%S') + ' ~ ' + 
                graph_info['end_time'].strftime('%Y-%m-%d %H:%M:%S') )
    print('\n' + title)
    plt.legend(x_index, loc='upper right')
    plt.suptitle(title)

    plt.show()

def draw_fourier_graph_by_freq_sub(data, graph_info, fig, f_index, index) :
    x_index = []
    rssi_index = []
    freq_strength_max = 0
    freq_strength_list_sub = []
    subplot_x, subplot_y = 3, 3

    for temp_dic in data :
        loc = temp_dic['loc']
        rssi = temp_dic['rssi']
        x_index = np.append(x_index, loc)
        rssi_index.append(rssi)

    ## plotting for understanding visually        
    for j in range(0, len(rssi_index)) : 
        freq_strength, freqs = get_fourier_transform(rssi_index[j], f_index)
        freq_strength_list_sub = np.append(freq_strength_list_sub, freq_strength)

    if freq_strength_max < freq_strength_list_sub.max() :
        freq_strength_max = freq_strength_list_sub.max()

    fig.add_subplot(subplot_x, subplot_y, index+1)
    plt.bar(x_index, freq_strength_list_sub)
    for j, v in enumerate(x_index):
        plt.text(v, freq_strength_list_sub[j], round(freq_strength_list_sub[j], 4), 
            horizontalalignment='center', verticalalignment='bottom', color='darkblue')        
        if v == graph_info['loc'] :
            plt.text(v, freq_strength_list_sub[j]/2, "★", 
                horizontalalignment='center', verticalalignment='bottom', color='red', fontsize=25)        
    plt.ylim([0, freq_strength_max*1.1])
    plt.ylabel('Fourier(rssi)')
    title = (graph_info['start_time'].strftime('%Y-%m-%d %H:%M') + ' ~ ' + 
                graph_info['end_time'].strftime('%H:%M') + ' , ' + 
                'Location : ' + graph_info['loc'] + ' , ' + 
                'Action : ' + graph_info['action'])
    plt.title(title, fontsize=10)
    return freqs

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

def fourier_graph_by_time(input_path_list, info, location=None, avg=True) :
    for event in info['event'] :
        data, graph_info = make_data_list(input_path_list, info, location, avg)
        graph_info['loc'] = event['loc']
        graph_info['action'] = event['action']
        draw_fourier_graph_by_time(data, graph_info)

def fourier_graph_by_freq(input_path_list, info, location=None,avg=True) :
    f_index_count = 5
    for f_index in range(f_index_count) :
        plt.rcParams['figure.figsize'] = [FIGSIZE_X, FIGSIZE_Y]
        fig = plt.figure()
        for i, event in enumerate(info['event']) :
            data, graph_info = make_data_list(input_path_list, info, location, avg)
            graph_info['loc'] = event['loc']
            graph_info['action'] = event['action']
            freqs_list = draw_fourier_graph_by_freq_sub(data, graph_info, fig, f_index, i)
        title = 'Wi-Fi Signal Strength at ' + str(round(freqs_list,4)) + ' Hz' + ' , f_index : %d'%(f_index)
        print('\n' + title)
        plt.suptitle(title, fontsize=15)
        #figManager = plt.get_current_fig_manager()
        #figManager.window.showMaximized()
        plt.show()

def rssi_graph(input_path_list, info=None, location=None, avg=True, tash=False) :
    data, graph_info = make_data_list(input_path_list, info, location, avg)
    draw_rssi_graph(data, graph_info, info, location, tash)

def rssi_graph_all(input_path='./data/', info=None, location=None, avg=True) :
    data, graph_info = make_data_list_top(input_path, info, location, avg)
    draw_rssi_graph(data, graph_info, info, location)

def time_graph(input_path_list, info=None, location=None, avg=True) :
    data, graph_info = make_data_list(input_path_list, info, location, avg)
    draw_time_graph(data, graph_info, info, location)

def time_graph_all(input_path='./data/', info=None, location=None, avg=True) :
    data, graph_info = make_data_list_top(input_path, info, location, avg)
    draw_time_graph(data, graph_info, info, location)

def fourier_graph_full(input_path_list, info, location=None, avg=True, data_len=100) :
    data, graph_info = make_data_list(input_path_list, info, location, avg)
    draw_fourier_graph_full(data, graph_info, data_len=data_len)

input_path_list = []
#input_path_list.append('./data/210121')
#input_path_list.append('./data/210123')
#input_path_list.append('./data/210124')
#input_path_list.append('./data/210126')
#input_path_list.append('./data/210128')
#input_path_list.append('./data/210207')
input_path_list.append('./data/210217')
#input_path_list.append('./data/210220')
info = read_info(input_path_list[0])
fourier_graph_full(input_path_list, info, avg=True)

'''
for input_list in input_path_list :
    input_ = []
    info = read_info(input_list)
    input_.append(input_list)
    rssi_graph(input_, info, avg=True, tash=True)
'''
#input_path_list.append('./data/210128')
#input_path_list.append('./data/210207')
#info = read_info('./data/210121')
#rssi_graph(input_path_list, info, avg=True)
#time_graph(input_path_list, avg=True)
#rssi_graph(input_path_list, location='PCroom', avg=True)
#time_graph(input_path_list, location='PCroom')
#time_graph_all()
#fourier_graph_by_time(input_path_list, info) 
#fourier_graph_by_freq(input_path_list, info)
'''
rssi_graph(input_path, info, avg=False)

fourier_graph_by_time(input_path, info) 
fourier_graph_by_freq(input_path, info)

rssi_graph_all(avg=True)
rssi_graph_all(avg=False)

'''