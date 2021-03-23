from matplotlib import pyplot as plt
import seaborn as sns
from sklearn.metrics import confusion_matrix
import pandas as pd

LABELS = ["False", "Hit"]
#https://matplotlib.org/examples/color/named_colors.html
cmap_list = ['magenta', 'darkred', 'coral', 'tomato', 'firebrick', 'orangered', 'brown', 'darkviolet', 'peru']

colors = {'PCroom':'g.', 'Living':'c.', 'Kitchen':'m.'}
colorstr = {'PCroom':'g', 'Living':'c', 'Kitchen':'m'}

FIGSIZE_X, FIGSIZE_Y = 25, 15

def plot_confusion_matrix(y_true, y_pred):
    plt.clf()
    conf_matrix = confusion_matrix(y_true, y_pred)

    fig= plt.figure(figsize=(12, 12))
    sns.heatmap(conf_matrix, xticklabels=LABELS, yticklabels=LABELS, annot=True, fmt="d")
    plt.title("Confusion matrix")
    plt.ylabel('True class')
    plt.xlabel('Predicted class')
    #plt.show()
    plt.close(fig)

def plot_confusion_matrix_file(y_test_list, reconstruction_list, loc_data_list, png_dir, model_name):
    plt.clf()

    y_true_, y_pred_ = [], []
    success = 0
    for k, y_test in enumerate(y_test_list) :
        for i, y in enumerate(y_test) :
            if y :
                max_recon = 0
                max_j = -1
                for j, reconstruction in enumerate(reconstruction_list) :
                    if reconstruction[i] > max_recon :
                        max_recon = reconstruction[i]
                        max_j = j
                y_true_.append(k)
                y_pred_.append(max_j)
                if k == max_j :
                    success = success + 1

    conf_matrix = confusion_matrix(y_true_, y_pred_)

    png_name = png_dir + model_name + '_conf_' + str(success) + '.png'
    fig = plt.figure(figsize=(FIGSIZE_X, FIGSIZE_Y))
    sns.heatmap(conf_matrix, xticklabels=loc_data_list, yticklabels=loc_data_list, annot=True, fmt="d")
    plt.title(model_name)
    plt.ylabel('True class')
    plt.xlabel('Predicted class')
    plt.savefig(png_name)
    #plt.show()
    plt.close(fig)

def plot_training_history(history):
    if history is None:
        return
    plt.clf()
    plt.plot(history['loss'])
    plt.plot(history['val_loss'])
    plt.title('model loss')
    plt.ylabel('loss')
    plt.xlabel('epoch')
    plt.legend(['train', 'test'], loc='upper left')
    #plt.show()


def visualize_anomaly(y_true, reconstruction_error, threshold):
    error_df = pd.DataFrame({'reconstruction_error': reconstruction_error,
                             'true_class': y_true})
    print(error_df.describe())

    plt.clf()
    groups = error_df.groupby('true_class')
    fig, ax = plt.subplots()

    for name, group in groups:
        ax.plot(group.index, group.reconstruction_error, marker='o', ms=3.5, linestyle='',
                label="Fraud" if name == 1 else "Normal")

    ax.hlines(threshold, ax.get_xlim()[0], ax.get_xlim()[1], colors="r", zorder=100, label='Threshold')
    ax.legend(loc='upper left')
    plt.title("Reconstruction error for different classes")
    plt.ylabel("Reconstruction error")
    plt.xlabel("Data point index")
    #plt.show()

def visualize_reconstruction_error(Y_data, reconstruction_error, threshold, gap_dir_1, gap_dir_2, train_length, png_title, error_list, is_threshold_list = False):
    plt.clf()

    gap_name_info_1 = gap_dir_1 + png_title + '_gap.png'
    gap_name_info_2 = gap_dir_2 + png_title + '_gap.png'

    plt.plot(reconstruction_error, marker='o', ms=3.5, linestyle='', label='Point')

    error_name = ["Normal"]
    for i in range(1, len(error_list)) :
        error_name.append(error_list[i])

    if is_threshold_list :
        plt.plot(threshold, marker='o', ms=3.5, linestyle='', label='Threshold')
    else :
        plt.hlines(threshold, xmin=0, xmax=len(reconstruction_error)-1, colors="b", zorder=100, label='Threshold')
    y_size = len(Y_data)
    ymax = max(reconstruction_error)
    for j in range(1, len(error_list)):
        x_list = []
        is_error = False
        for i in range (train_length, y_size) :
            if Y_data[i] == j :
                x_list.append(i)

                is_error = True
                #plt.text(i+1, ymax/2+0.1, error_txt)
        if is_error == True :
            plt.vlines(x=x_list, ymin=0, ymax=ymax,colors=cmap_list[j], label=error_list[j])
    
    plt.legend(loc='upper left')
    plt.title(png_title)
    plt.ylabel("Reconstruction error")
    plt.xlabel("Data point index")
    plt.grid()
    plt.savefig(gap_name_info_1)
    plt.savefig(gap_name_info_2)
    #plt.show()

def visualize_reconstruction_error_list(Y_data, reconstruction_error, time_test_list, location_list, model_name, png_name):
    plt.clf()
    location_num = len(location_list)
    
    plt.rcParams['figure.figsize'] = [FIGSIZE_X, FIGSIZE_Y]
    fig = plt.figure()
    ymax = 0
    for y in reconstruction_error :
        if ymax < max(y) :
            ymax = max(y)

    for i in range(location_num) :
        plt.plot(time_test_list[i], reconstruction_error[i], colorstr[location_list[i]], marker='o', ms=1.5, linestyle='', label=location_list[i])
        #plt.hlines(threshold, xmin=0, xmax=len(reconstruction_error)-1, colors="b", zorder=100, label='Threshold')
        x_line_list = []
        for j, y in enumerate(Y_data[i]) :
            if y :
                x_line_list.append(time_test_list[i][j])
        
        plt.vlines(x=x_line_list, ymin=ymax*1.1, ymax=ymax*1.2, colors=colorstr[location_list[i]], linestyle='--')
    
    plt.legend(loc='upper left')
    plt.title(model_name)
    plt.ylabel("Reconstruction error")
    plt.xlabel("Data point index")
    plt.grid()
    plt.savefig(png_name)

    #plt.show()

def visualize_anomaly_errors(Y_data, reconstruction_error, threshold, anomaly_dir_1, anomaly_dir_2, train_length, png_title, error_list, is_threshold_list = False):
    anomaly_name_info_1 = anomaly_dir_1 + png_title + '_anomaly.png'
    anomaly_name_info_2 = anomaly_dir_2 + png_title + '_anomaly.png'
    
    error_df = pd.DataFrame({'reconstruction_error': reconstruction_error, 'true_class': Y_data})
    print(error_df.describe())

    plt.clf()
    groups = error_df.groupby('true_class')
    fig, ax = plt.subplots()

    error_name = ["Normal"]
    for i in range(1, len(error_list)) :
        error_name.append(error_list[i])

    for name, group in groups:
        ax.plot(group.index, group.reconstruction_error, marker='o', ms=3.5, linestyle='', label=error_name[name])

    if is_threshold_list :
        ax.plot(threshold, marker='o', ms=3.5, linestyle='', label='Threshold')
    else :
        ax.hlines(threshold, ax.get_xlim()[0], ax.get_xlim()[1], colors="r", zorder=100, label='Threshold')
    ax.legend(loc='upper left')
    #plt.title("Reconstruction error for different classes")
    plt.title(png_title)
    plt.ylabel("Reconstruction error")
    plt.xlabel("Data point index")
    plt.savefig(anomaly_name_info_1)
    plt.savefig(anomaly_name_info_2)    
    #plt.show()
    plt.close(fig)

def plot_training_history_file(history, loss_dir, model_name):
    if history is None:
        return
    plt.clf()
    loss_dir_str = loss_dir + 'loss_' + model_name + '.png'
    plt.plot(history['loss'])
    plt.plot(history['val_loss'])
    plt.title('model loss')
    plt.ylabel('loss')
    plt.xlabel('epoch')
    plt.legend(['train', 'test'], loc='upper right')
    plt.savefig(loss_dir_str)
    #plt.show()
