import numpy as np
import os
import os.path
import json
import seaborn as sns
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import math

from data import make_data_list, make_data_list_top

colors = {'PCroom':'g.', 'Living':'c.', 'Kitchen':'m.'}
colorstr = {'PCroom':'g', 'Living':'c', 'Kitchen':'m'}

FIGSIZE_X, FIGSIZE_Y = 25, 15

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

def fourier_graph_full(x_data_list, y_data_list, time_data_list, loc_data_list, graph_info, tash=False, save=False, png_name=None) :
    print('\nfourier_graph_full')
    f_index_count = len(x_data_list[0][0])
    subplot_x = f_index_count
    subplot_y = 1
    x_data_trans_list = []
    for x_data in x_data_list :
        x_data_trans_list.append(np.transpose(x_data)) 

    plt.rcParams['figure.figsize'] = [FIGSIZE_X, FIGSIZE_Y]
    fig = plt.figure()
    for i in range(f_index_count):
        fig.add_subplot(subplot_x, subplot_y, i+1)

        for j, loc in enumerate(loc_data_list):
            color = colorstr[loc]
            plt.plot(time_data_list[j], np.transpose(x_data_trans_list[j][i]), color)
            if tash :
                for k, y_data in enumerate(y_data_list[j]) :
                    if y_data :
                        plt.axvline(x=time_data_list[j][k], color=color, linestyle='--', linewidth=1)

        #plt.title('Wi-Fi Signal Strength at ' + str(round(freqs_list[i],4)) + ' Hz' + ' , f_index : %d'%(i))
        plt.ylabel('Fourier(rssi)')
        plt.grid(True, axis='y', linestyle='--')

    title = (graph_info['start_time'].strftime('%Y-%m-%d %H:%M:%S') + ' ~ ' + 
                graph_info['end_time'].strftime('%Y-%m-%d %H:%M:%S') )
    plt.legend(loc_data_list, loc='upper right')
    plt.suptitle(title)

    if save :
        if png_name :            
            plt.savefig(png_name)
    else :
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

def fourier_data(data, graph_info, f_index_count=5, data_len=100) :
    freq_strength_list = []
    time_list =[]
    tash_list=[]
    loc_list=[]
    rssi_index=[]

    for temp_dic in data :
        loc = temp_dic['loc']
        rssi = temp_dic['rssi']
        time = temp_dic['time_list']
        tash = temp_dic['tash']
        loc_list.append(loc)
        rssi_index.append(rssi)
        time_list.append(time)
        tash_list.append(tash)
    
    for i in range(len(rssi_index)) :
        freq_strength_list_sub = []
        for f in range(f_index_count):
            f_index = f
            freq_strength_temp_list = []
            for k in range(int(data_len/2), len(rssi_index[i]) - data_len) : 
                freq_strength, freqs = get_fourier_transform(rssi_index[i][k:k+data_len], f_index)
                freq_strength_temp_list.append(round(freq_strength,4))
            freq_strength_list_sub.append(freq_strength_temp_list)
        freq_strength_list.append(freq_strength_list_sub)
        #freq_list.append(freqs)

    x_data_list = []
    y_data_list = []
    time_data_list = []
    loc_data_list = []

    for i, freq_strength in enumerate(freq_strength_list) :
        x_data = []
        y_data = []
        base_time_list = time_list[i][int(data_len/2):len(freq_strength[0])+int(data_len/2)]

        for j, base_time in enumerate(base_time_list) :
            temp_list = []
            for k in freq_strength:
                temp_list.append(k[j])
            x_data.append(temp_list)
            y_data.append(base_time in tash_list[i])

        x_data_list.append(x_data)
        y_data_list.append(y_data)
        time_data_list.append(base_time_list)
        loc_data_list.append(loc_list[i])

    return x_data_list, y_data_list, time_data_list, loc_data_list