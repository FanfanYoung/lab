# coding=utf-8
_author__ = 'Angela'
from sklearn.metrics import mean_squared_error
import numpy as np
import pandas as pd
import time
import pickle
from pandas import DataFrame, Series
from sklearn import preprocessing
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.preprocessing import OneHotEncoder

# 由label_result文件得到每个pattern映射的整数
def getMapper():
    map_file = "D:\Graduate Design\Experiment\dataworkspace\\trainData\level1_speedPattern\label_result"
    pattern_map = {}
    for line in open(map_file):
        line_arr = line.split(",")
        pattern_map[line_arr[0]] = int(line_arr[2])  # 将pattern的字符串模式转为integer
    return pattern_map

# 将数据中的pattern映射成integer
def transformPatternInteger(data, pattern_mapper):
    multi_flag = False
    first_pattern = data['pattern'][0]
    for i in range(len(data['pattern'])):
        if multi_flag == False and first_pattern != data['pattern'][i]:
            multi_flag = True
        transform_value = pattern_mapper.get(data['pattern'][i])
        data['pattern'][i] = transform_value
    return data, multi_flag

def getEncoder(data):
    enc = OneHotEncoder(categorical_features=np.array([12]))
    enc.fit(data)
    return enc

# 从数据文件中读取数据
def read_data(data_file,columns_name):
    data = pd.read_table(data_file, header=None, sep=',', names=columns_name)
    return data

if __name__ == '__main__':

    pattern_mapper = getMapper()
    columns_name = ['car_weight', 'car_length', 'gradient', 'type', 'length', 'limit_value', 'fwd_gradient', 'fwd_type', 'fwd_length', 'bwd_gradient', 'bwd_type', 'bwd_length', 'pattern', 'variation_type', 'index', 'percentage', 'v_o']

    # 获取encoder
    total_pattern_file_path = "D:\Graduate Design\Experiment\dataworkspace\\trainData\level1_speedPattern\pattern_param\\total_pattern_patram"
    total_data = read_data(total_pattern_file_path, columns_name)
    total_data,flag = transformPatternInteger(total_data, pattern_mapper)
    enc = getEncoder(total_data)

    cluster_num = 30

    for k in range(0, cluster_num):
        print "********************* " + str(k) +" *************************"
        train_data_file = "D:\Graduate Design\Experiment\dataworkspace\\trainData\level1_speedPattern\pattern_param\pattern_param_rc_" + str(k)
        # 获取训练数据的属性和label
        train = read_data(train_data_file, columns_name)
        train_y1 = train["percentage"]
        train_y2 = train["v_o"]
        train_x = train.drop(["percentage", "v_o"], axis=1)
        train_x,multi_flag = transformPatternInteger(train_x, pattern_mapper)
        train_x = enc.transform(train_x).toarray()



        start_time = time.time()
        model1 = GradientBoostingRegressor(n_estimators=100,learning_rate=0.1,max_depth=1,random_state=0,loss='ls')
        model1.fit(train_x,train_y1)
        print('training took %f s!' % (time.time() - start_time))

        # 将训练模型序列化保存在文件中
        model_file_path = "D:\Graduate Design\Experiment\dataworkspace\model\level1_speedPattern\pattern_param\\route_predict_SVM_percentage_" + str(k) + ".pkl"
        output = open(model_file_path, 'wb')
        pickle.dump(model1, output)
        output.close()

        #predict_y = model.predict(test_x)


        start_time = time.time()
        model2 = GradientBoostingRegressor(n_estimators=100,learning_rate=0.1,max_depth=1,random_state=0,loss='ls')
        model2.fit(train_x, train_y2)
        print('training took %f s!' % (time.time() - start_time))

        # 将训练模型序列化保存在文件中
        model_file_path = "D:\Graduate Design\Experiment\dataworkspace\model\level1_speedPattern\pattern_param\\route_predict_SVM_vo_" + str(
            k) + ".pkl"
        output = open(model_file_path, 'wb')
        pickle.dump(model2, output)
        output.close()

        if multi_flag == False and k!=5:
            test_data_file = "D:\Graduate Design\Experiment\dataworkspace\\testData\level1_speedPattern\pattern_param\pattern_param_rc_" + str(
                k)
            test = read_data(test_data_file, columns_name)
            test_y1 = test["percentage"]
            test_y2 = test["v_o"]
            test_x = test.drop(["percentage", "v_o"], axis=1)
            test_x, multi_flag = transformPatternInteger(test_x, pattern_mapper)
            test_x = enc.transform(test_x).toarray()

            predict_y1 = model1.predict(test_x)
            predict_y2 = model2.predict(test_x)
            mse1 = mean_squared_error(test_y1, predict_y1)
            mse2 = mean_squared_error(test_y2, predict_y2)

            print('accuracy1: %.4f' % mse1)
            print('accuracy2: %.4f' % mse2)
