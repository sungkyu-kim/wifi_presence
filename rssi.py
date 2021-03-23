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

def draw_rssi_graph(data, graph_info, info=None, location=None, tash=False, save=False, png_dir=None) :
    print('\ndraw_rssi_graph')
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
    plt.title(title)
    plt.xlabel('time')
    plt.ylabel('RSSI')
    plt.legend(legend_string, loc='upper right')
    plt.grid(True, axis='y', linestyle='--')
    plt.yticks(np.arange(graph_info['rssi_min']-1, graph_info['rssi_max']+1))
    #plt.xticks([start_time, end_time])
    #figManager = plt.get_current_fig_manager()
    #figManager.window.showMaximized()
    if save :
        if png_dir :
            png_name = png_dir + 'RSSI_' + str(tash)+'.png'
            plt.savefig(png_name)
    else :
        plt.show()

def rssi_graph(data, graph_info, info=None, location=None, avg=True, tash=False, save=False, png_dir=None) :
    draw_rssi_graph(data, graph_info, info, location, tash, save, png_dir)

def rssi_graph_all(input_path='./data/', info=None, location=None, avg=True) :
    data, graph_info = make_data_list_top(input_path, info, location, avg)
    draw_rssi_graph(data, graph_info, info, location)

def time_graph(input_path_list, info=None, location=None, avg=True) :
    data, graph_info = make_data_list(input_path_list, info, location, avg)
    draw_time_graph(data, graph_info, info, location)

def time_graph_all(input_path='./data/', info=None, location=None, avg=True) :
    data, graph_info = make_data_list_top(input_path, info, location, avg)
    draw_time_graph(data, graph_info, info, location)

