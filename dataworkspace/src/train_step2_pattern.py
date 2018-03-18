# coding=utf-8
_author__ = 'Angela'
from sklearn import metrics
import pandas as pd
import time
import pickle
from pandas import DataFrame, Series
from sklearn import preprocessing

def gradient_boosting_classifier(train_x, train_y):
    from sklearn.ensemble import GradientBoostingClassifier
    model = GradientBoostingClassifier(n_estimators=200)
    model.fit(train_x, train_y)
    return model

def read_data(train_data_file, test_data_file):
    columns_name = ['car_weight','car_length','gradient','type','length','limit_value','fwd_gradient','fwd_type','fwd_length','bwd_gradient','bwd_type','bwd_length','combination']
    train = pd.read_table(train_data_file, header=None, sep=',', names=columns_name)
    train_y = train['combination']
    train_x = train.drop(['combination'], axis=1)
    test = pd.read_table(test_data_file, header=None, sep=',', names=columns_name)
    test_y = test['combination']
    test_x = test.drop(['combination'], axis=1)
    return train_x, train_y, test_x, test_y

if __name__ == '__main__':

    model_list_file = "D:\Graduate Design\Experiment\dataworkspace\model\model_list.txt"
    cluster_num = 30

    for k in range(0,cluster_num):
        train_data_file = "D:\Graduate Design\Experiment\dataworkspace\\trainData\level1_speedPattern\pattern\pattern_rc_"+str(k)
        test_data_file = "D:\Graduate Design\Experiment\dataworkspace\\testData\level1_speedPattern\pattern\pattern_rc_"+str(k)
        train_x, train_y, test_x, test_y = read_data(train_data_file, test_data_file)
        if len(test_y) == 0:
            continue
        print('***********************  %d  ************************' % k)
        i = 0
        first_class = train_y[0]
        multi_class_flag = False
        while i< len(train_y):
            if first_class != train_y[i]:
                multi_class_flag = True
                break;
            else:
                i = i+1
        if multi_class_flag == False:
            # 如果只有一个类，则model list中对应的是类标,N表示直接为类标，Y表示为模型文件名称
            with open(model_list_file, 'a') as f:
                f.write(str(k) + " N " + first_class+"\n")
            f.close()
            predict_arr = []
            for i in range(len(test_y)):
                predict_arr.append(first_class)
            predict_y = pd.Series(predict_arr)

        else:
            # 如果不止一个类，则对应model文件的名称
            with open(model_list_file, 'a') as f:
                f.write(str(k) + " Y route_predict_GBDT_"+str(k)+".pkl\n")
            f.close()

            start_time = time.time()
            model = gradient_boosting_classifier(train_x, train_y)
            print('training took %f s!' % (time.time() - start_time))

            # 将训练模型序列化保存在文件中
            model_file_path = "D:\Graduate Design\Experiment\dataworkspace\model\level1_speedPattern\pattern\\route_predict_GBDT_"+str(k)+".pkl"
            output = open(model_file_path, 'wb')
            pickle.dump(model, output)
            output.close()

            # 从文件中重构model
            #pkl_file = open(model_file_path, 'rb')
            #read_model = pickle.load(pkl_file)

            predict_y = model.predict(test_x)
            #predict2 = read_model.predict(test_x)

        accuracy1 = metrics.accuracy_score(test_y, predict_y)

        print('accuracy1: %.2f%%' % (100 * accuracy1))

        # 将速度模式预测的数据加入预测参数的数据中
        param_out_file = "D:\Graduate Design\Experiment\dataworkspace\\testData\level1_speedPattern\pattern_param\pattern_param_rc_"+str(k)
        with open(param_out_file,'w') as f:
            for i in range(len(test_x)):
                line = ""
                for j in range(len(test_x.ix[i])):
                    line = line + str(test_x.ix[i][j]) + ","
                line = line + predict_y[i] +","
                label = predict_y[i][1:-1]
                label_arr = label.split()
                for j in range(len(label_arr)):
                    line1 = line + label_arr[j] + "," + str(j+1) + ",0,0\n"
                    f.write(line1)
        f.close()
