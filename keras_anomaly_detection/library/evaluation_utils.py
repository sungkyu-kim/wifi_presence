from sklearn.metrics import average_precision_score, recall_score, precision_score, f1_score


def report_evaluation_metrics(y_true, y_pred):
    average_precision = average_precision_score(y_true, y_pred)
    precision = precision_score(y_true, y_pred, labels=[0, 1], pos_label=1)
    recall = recall_score(y_true, y_pred, labels=[0, 1], pos_label=1)
    f1 = f1_score(y_true, y_pred, labels=[0, 1], pos_label=1)

    print('Average precision-recall score: {0:0.2f}'.format(average_precision))
    print('Precision: {0:0.2f}'.format(precision))
    print('Recall: {0:0.2f}'.format(recall))
    print('F1: {0:0.2f}'.format(f1))

def report_evaluation_metrics_file(y_true, y_pred, metrics_dir_1, metrics_dir_2, title, model_name):

    output_file_1 = metrics_dir_1 + model_name + '_evaluation.txt'

    y_true_, y_pred_ = [], []
    for i in range (len(y_true)) :
        if y_true[i] > 0 :
            y_true_.append(1)
        else :
            y_true_.append(0)
        if y_pred[i] > 0 :
            y_pred_.append(1)
        else :
            y_pred_.append(0)

    average_precision = average_precision_score(y_true_, y_pred_)
    precision = precision_score(y_true_, y_pred_, labels=[0, 1], pos_label=1)
    recall = recall_score(y_true_, y_pred_, labels=[0, 1], pos_label=1)
    f1 = f1_score(y_true_, y_pred_, labels=[0, 1], pos_label=1)

    print('Average precision-recall score: {0:0.2f}'.format(average_precision))
    print('Precision: {0:0.2f}'.format(precision))
    print('Recall: {0:0.2f}'.format(recall))
    print('F1: {0:0.2f}'.format(f1))

    f = open(output_file_1, mode='at')
    f.write('\n' + title + '\n')
    f.write('Average precision-recall score: {0:0.2f}\n'.format(average_precision))
    f.write('Precision: {0:0.2f}\n'.format(precision))
    f.write('Recall: {0:0.2f}\n'.format(recall))
    f.write('F1: {0:0.2f}\n'.format(f1))
    f.close()

    if metrics_dir_2 != 'NULL' :
        output_file_2 = metrics_dir_2 + title + '_evaluation.txt'
        f = open(output_file_2, mode='at')
        f.write('\n' + title + '\n')
        f.write('Average precision-recall score: {0:0.2f}\n'.format(average_precision))
        f.write('Precision: {0:0.2f}\n'.format(precision))
        f.write('Recall: {0:0.2f}\n'.format(recall))
        f.write('F1: {0:0.2f}\n'.format(f1))
        f.close()
