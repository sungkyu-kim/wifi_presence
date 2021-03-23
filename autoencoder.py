import os
import gc

import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler

from keras_anomaly_detection.library.plot_utils import visualize_reconstruction_error, plot_training_history_file, \
    plot_confusion_matrix_file, visualize_anomaly_errors, visualize_reconstruction_error_list
from keras_anomaly_detection.library.evaluation_utils import report_evaluation_metrics_file

from keras_anomaly_detection.model.CnnLstmAutoEncoder import CnnLstmAutoEncoder
from keras_anomaly_detection.model.LstmAutoEncoder import LstmAutoEncoder
from keras_anomaly_detection.model.Conv1DAutoEncoder import Conv1DAutoEncoder
from keras_anomaly_detection.model.BidirectionalLstmAutoEncoder import BidirectionalLstmAutoEncoder

import matplotlib.pyplot as plt
import time

from data import read_info, make_data_list
from fourier import fourier_data, fourier_graph_full
from rssi import rssi_graph

DO_TRAINING = False
RANDOM_SEED = 42

adjusted_threshold = 2

def create_directory(directory_path):
    if os.path.exists(directory_path):
        return None
    else:
        try:
            os.makedirs(directory_path)
        except:
            # in case another machine created the path meanwhile !:(
            return None
        return directory_path

def AutoEncoder_test_train(X_data, test_dir, model_name, ae) :
    model_dir_path = test_dir + model_name + '/'
    create_directory(model_dir_path)
    
    loss_dir = test_dir + 'loss/'
    create_directory(loss_dir)
    
    # fit the data and save model into model_dir_path
    history = ae.fit(X_data, model_dir_path=model_dir_path)

    plot_training_history_file(history, loss_dir, model_name)

def AutoEncoder_pred(X_data, Y_data, ae) :
    Ypred = []
    reconstruction_error = []
    # ae.load_model(model_dir_path)
    anomlay_information = ae.anomaly(X_data)

    for idx, (is_anomaly, dist) in enumerate(anomlay_information):
        predicted_label = 1 if is_anomaly else 0
        Ypred.append(predicted_label)
        reconstruction_error.append(dist)
    return Ypred, reconstruction_error

def main_train(x_train_list, model_name, ae, test_dir):
    print('\n' + model_name + 'train start')
    AutoEncoder_test_train(np.array(x_train_list), test_dir, model_name, ae)
    print(model_name + 'train end' + '\n')

def main_pred(x_test_list, y_test_list, ae) :
    y_pred, reconstruction = AutoEncoder_pred(np.array(x_test_list), np.array(y_test_list), ae)
    return y_pred, reconstruction

def main_test(test_dir, date_str, input_path_list, info, avg, f_index_count, data_len):
    np.random.seed(RANDOM_SEED)

    x_train_list = []
    x_test_list = []
    y_test_list = []
    time_test_list = []
    X_scaler_data_list = []
    tash_min_index = 9999999999

    create_directory(test_dir)

    data, graph_info = make_data_list(input_path_list, info=info, avg=avg)
    x_data_list, y_data_list, time_data_list, loc_data_list = fourier_data(data, graph_info, f_index_count, data_len)

    rssi_graph(data, graph_info, info, avg=avg, tash=False, save=True, png_dir=test_dir)
    rssi_graph(data, graph_info, info, avg=avg, tash=True, save=True, png_dir=test_dir)
    
    fourier_graph_full(x_data_list, y_data_list, time_data_list, loc_data_list, graph_info, tash=False, save=True, png_name=test_dir+'Fourier_ori_False.png')
    fourier_graph_full(x_data_list, y_data_list, time_data_list, loc_data_list, graph_info, tash=True, save=True, png_name=test_dir+'Fourier_ori_True.png')

    for y_data in y_data_list :
        if tash_min_index > y_data.index(True) :
            tash_min_index = y_data.index(True)
    tash_min_index = int(tash_min_index * 0.8)

    scaler = MinMaxScaler()
    for x_data in x_data_list :
        X_scaler_data_list.append(scaler.fit_transform(x_data))

    fourier_graph_full(X_scaler_data_list, y_data_list, time_data_list, loc_data_list, graph_info, tash=False, save=True, png_name=test_dir+'Fourier_trans_False.png')
    fourier_graph_full(X_scaler_data_list, y_data_list, time_data_list, loc_data_list, graph_info, tash=True, save=True, png_name=test_dir+'Fourier_trans_True.png')

    for i, x_data in enumerate(X_scaler_data_list):
        x_train_list.append(x_data[:tash_min_index])
        x_test_list.append(x_data[tash_min_index:])
        y_test_list.append(y_data_list[i][tash_min_index:])
        time_test_list.append(time_data_list[i][tash_min_index:])

    loc_num = len(loc_data_list)

    model_name_list = ['Conv1DAutoEncoder']
    model_name_list = ['LstmAutoEncoder', 'CnnLstmAutoEncoder', 'BidirectionalLstmAutoEncoder']

    for model_name in model_name_list :
        ae_list = []
        y_pred_list = []
        reconstruction_list = []
        for i in range(loc_num) :
            if model_name == 'Conv1DAutoEncoder' :
                ae = Conv1DAutoEncoder()                
            elif model_name == 'LstmAutoEncoder' :
                ae = LstmAutoEncoder()
            elif model_name == 'CnnLstmAutoEncoder' :
                ae = CnnLstmAutoEncoder()
            elif model_name == 'BidirectionalLstmAutoEncoder' :
                ae = BidirectionalLstmAutoEncoder()
            ae_list.append(ae)
            main_train(x_train_list[i], model_name, ae_list[i], test_dir)

        for i in range(loc_num) :
            y_pred, reconstruction = main_pred(x_test_list[i], y_test_list[i], ae_list[i])
            y_pred_list.append(y_pred)
            reconstruction_list.append(reconstruction)
        visualize_reconstruction_error_list(y_test_list, reconstruction_list, time_test_list, loc_data_list, model_name, test_dir+model_name+'_test.png')
        plot_confusion_matrix_file(y_test_list, reconstruction_list, loc_data_list, test_dir, model_name)
        del y_pred_list
        del reconstruction_list
        y_pred_list = []
        reconstruction_list = []
        for i in range(loc_num) :
            y_pred, reconstruction = main_pred(X_scaler_data_list[i], y_data_list[i], ae_list[i])
            y_pred_list.append(y_pred)
            reconstruction_list.append(reconstruction)
        visualize_reconstruction_error_list(y_data_list, reconstruction_list, time_data_list, loc_data_list, model_name, test_dir+model_name+'_all.png')
        del ae_list
        del y_pred_list
        del reconstruction_list
    del x_train_list
    del x_test_list
    del y_test_list
    del time_test_list
    del X_scaler_data_list

#if __name__ == '__main__':
#    main()

RESULT_DIR = './Results/'
date_str = time.strftime("%m%d_%H%M")
test_dir = RESULT_DIR + date_str + '/'

input_path_list = []
input_path_list.append('./data/210322')
info = read_info(input_path_list[0])

avg_list = [False]
f_index_count_list = [6]
data_len_list = [30,60,120,130]

create_directory(test_dir)
for avg in avg_list :
    for f_index_count in f_index_count_list :
        for data_len in data_len_list:
            date_str = time.strftime("%m%d_%H%M")
            sub_test_dir = test_dir + date_str +'_'+str(avg)+'_'+str(f_index_count)+'_'+str(data_len) + '/'
            main_test(sub_test_dir, date_str, input_path_list, info, avg, f_index_count, data_len)
            gc.collect()    

