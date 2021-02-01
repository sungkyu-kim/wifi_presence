import numpy as np
import os
import os.path
import json
import seaborn as sns
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

colors = {'PCroom':'g.', 'Living':'c.', 'Kitchen':'m.', 'livingroom':'c.', 'kitchen':'m.'}

def make_dic(st_json, start_time, end_time):
    avg_rssi = []
    time_list = []

    for json_str in st_json:
        check_start = json_str.find('{')
        check_end = json_str.find('}')
        if check_start < 0 and check_end < 0 :
            continue        
        json_str = json_str[check_start:check_end+1]
        st_python = json.loads(json_str)
        test_time = datetime.strptime(st_python['time'], "%Y-%m-%d %H:%M:%S.%f")        
        if test_time > start_time and test_time < end_time :
            avg_rssi = np.append(avg_rssi, np.mean(st_python['rssi']))
            time_list.append(test_time)
            #avg_rssi = np.append(avg_rssi, st_python['rssi'])
    #print("loc : %s , time size : %d , rssi size : %d"%(st_python['loc'], len(time_list), len(avg_rssi)))
    temp_dic = {'loc':st_python['loc'], 'time_list':time_list, 'rssi':avg_rssi}
    return temp_dic

def make_data(input_path, start_time, end_time):
    files = os.listdir(input_path)
    data = []
    rssi_max = -100
    rssi_min = 0

    for filename in files :        
        if filename.endswith('.log') :
            filepath = input_path + '/' + filename
            with open(filepath, 'r') as st_json :
                #print('\n', filename)

                temp_dic = make_dic(st_json, start_time, end_time)
                temp_dic['filename'] = filename

                if rssi_max < temp_dic['rssi'].max() :
                    rssi_max = temp_dic['rssi'].max()
                if rssi_min < temp_dic['rssi'].min() :
                    rssi_min = temp_dic['rssi'].min()
                
                data.append(temp_dic)

    graph_info = {'start_time':start_time, 'end_time':end_time, 'rssi_max':(int)(rssi_max+1), 'rssi_min':(int)(rssi_min-1)}
    return data, graph_info

def draw_rssi_graph(data, graph_info) :
    legend_string = []

    for temp_dic in data :
        loc = temp_dic['loc']
        legend_string = np.append(legend_string, loc)
        plt.plot(temp_dic['time_list'], temp_dic['rssi'], colors[loc])

    xline_time = graph_info['start_time']
    while xline_time <= graph_info['end_time'] :
        plt.axvline(x=xline_time, color='silver', linestyle='--', linewidth=1)
        xline_time = xline_time + timedelta(minutes=30)

    plt.legend(legend_string, loc='right')
    plt.title('Wi-Fi Signal Variation')
    plt.xlabel('time')
    plt.ylabel('RSSI')
    #plt.rcParams['figure.figsize'] = [20, 15]
    plt.grid(True, axis='y', linestyle='--')
    plt.yticks(np.arange(graph_info['rssi_min'], graph_info['rssi_max']))
    #plt.xticks(np.arange(start_time, end_time))
    figManager = plt.get_current_fig_manager()
    figManager.window.showMaximized()
    plt.show()
    plt.clf()

def draw_fourier_graph(data, graph_info) :
    # Fourier Transform parameters
    fmax = 200      # sampling frequency 100 Hz
    dt = 1/fmax     # sampling period
    freq_strength = []
    x_index = []

    for temp_dic in data :
        loc = temp_dic['loc']        
        #plt.plot(temp_dic['time_list'], temp_dic['rssi'], colors[loc])
        avg_rssi = temp_dic['rssi']
        
        # perform Fourier transform without sorting
        N = len(avg_rssi)
        df = fmax/N     # df = 1/N = fmax/N
        freqs = np.arange(0,N)*df      # frq = [0, df, ..., (N-1)*df]
        freq_rssi = np.fft.fft(avg_rssi)*dt

        ## plotting for understanding visually
        f_index = 2
        freq_strength = np.append(freq_strength, np.abs(freq_rssi[f_index]))
        #x_index = np.append(x_index, filename.split('_')[1])
        x_index = np.append(x_index, loc)

    plt.bar(x_index, freq_strength)
    sns.set(font_scale = 1.4)
    #plt.legend(legend_string)
    plt.title('Wi-Fi Signal Strength at ' + str(freqs[f_index]) + ' Hz')
    plt.xlabel('frequency')
    plt.ylabel('Fourier(rssi)')
    plt.rcParams['figure.figsize'] = [20, 15]
    plt.show()
    plt.clf()

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

def draw_fourier_graph_by_test(data, graph_info) :
    f_index_count = 9    
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

    fig = plt.figure()    
    for i in range(f_index_count):
        fig.add_subplot(3,3,i+1)
        plt.bar(x_index, freq_strength_list[i])
        for j, v in enumerate(x_index):
            plt.text(v, freq_strength_list[i][j], round(freq_strength_list[i][j],4), 
                horizontalalignment='center', verticalalignment='bottom', fontsize=9, color='darkblue')
            if v == graph_info['loc'] :
                plt.text(v, freq_strength_list[i][j]/4, "★", 
                horizontalalignment='center', verticalalignment='bottom', color='red', fontsize=25)      
        #plt.ylim([0,freq_strength_max*1.1])
        plt.title('Wi-Fi Signal Strength at ' + str(round(freqs_list[i],4)) + ' Hz' + ' , f_index : %d'%(i))
        #plt.xlabel('frequency')
        plt.ylabel('Fourier(rssi)')

    figManager = plt.get_current_fig_manager()
    figManager.window.showMaximized()
    plt.suptitle(graph_info['start_time'].strftime('%Y-%m-%d %H:%M:%S') + ' ~ ' + 
                graph_info['end_time'].strftime('%H:%M:%S') + ' , ' + 
                'Location : ' + graph_info['loc'] + ' , ' + 
                'Action : ' + graph_info['action']
                , fontsize=15)
    plt.show()

def draw_fourier_graph_by_freq_sub(data, graph_info, fig, f_index, index) :
    x_index = []
    rssi_index = []
    freq_strength_max = 0

    for temp_dic in data :
        loc = temp_dic['loc']
        rssi = temp_dic['rssi']
        x_index = np.append(x_index, loc)
        rssi_index.append(rssi)

    freq_strength_list_sub = []
    ## plotting for understanding visually        
    for j in range(0, len(rssi_index)) : 
        freq_strength, freqs = get_fourier_transform(rssi_index[j], f_index)
        freq_strength_list_sub = np.append(freq_strength_list_sub, freq_strength)

    if freq_strength_max < freq_strength_list_sub.max() :
        freq_strength_max = freq_strength_list_sub.max()

    fig.add_subplot(3,3,index+1)
    plt.bar(x_index, freq_strength_list_sub)
    for j, v in enumerate(x_index):
        plt.text(v, freq_strength_list_sub[j], round(freq_strength_list_sub[j], 4), 
            horizontalalignment='center', verticalalignment='bottom', color='darkblue')        
        if v == graph_info['loc'] :
            plt.text(v, freq_strength_list_sub[j]/2, "★", 
                horizontalalignment='center', verticalalignment='bottom', color='red', fontsize=25)        
    plt.ylim([0,freq_strength_max*1.1])
    plt.ylabel('Fourier(rssi)')
    
    plt.title(graph_info['start_time'].strftime('%Y-%m-%d %H:%M') + ' ~ ' + 
                graph_info['end_time'].strftime('%H:%M') + ' , ' + 
                'Location : ' + graph_info['loc'] + ' , ' + 
                'Action : ' + graph_info['action']
                , fontsize=10)
    return freqs

def read_info(input_path):    
    filepath = input_path + '/' + 'info.json'
    event_list = []

    with open(filepath, 'r') as st_json :
        print('\n filename : ', filepath)
        json_data = json.load(st_json)
        
        info_start_time = datetime.strptime(json_data['start_time'], "%Y-%m-%d %H:%M:%S")
        info_end_time = datetime.strptime(json_data['end_time'], "%Y-%m-%d %H:%M:%S")
        event_array = json_data.get('event')
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

def fourier_graph_by_test(info) :
    for event in info['event'] :
        data, graph_info = make_data(input_path, event['start_time'], event['end_time'])
        graph_info['loc'] = event['loc']
        graph_info['action'] = event['action']
        draw_fourier_graph_by_test(data, graph_info)

def fourier_graph_by_freq(info) :
    f_index_count = 5
    for f_index in range(f_index_count) :
        fig = plt.figure()
        for i, event in enumerate(info['event']) :
            data, graph_info = make_data(input_path, event['start_time'], event['end_time'])
            graph_info['loc'] = event['loc']
            graph_info['action'] = event['action']
            freqs_list = draw_fourier_graph_by_freq_sub(data, graph_info, fig, f_index, i)
        figManager = plt.get_current_fig_manager()
        figManager.window.showMaximized()
        plt.suptitle('Wi-Fi Signal Strength at ' + str(round(freqs_list,4)) + ' Hz' + ' , f_index : %d'%(f_index), fontsize=15)
        plt.show()

def rssi_graph(info) :
    data, graph_info = make_data(input_path, info['start_time'], info['end_time'])
    draw_rssi_graph(data, graph_info)


input_path = './210124'
info = read_info(input_path)

#rssi_graph(info)
fourier_graph_by_test(info) 
#fourier_graph_by_freq(info)

