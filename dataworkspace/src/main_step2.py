# coding=utf-8
_author__ = 'Angela'
from data_structure import *
'''
主要做第二层速度模式处理

'''
cluster_num = 30
train_data_set1 = [[] for i in range(cluster_num)]        # 第一层速度层的训练数据集
def read_roadcategory(car_suffix):
    """
    :description: 读取该类型坡段信息
    :param car_suffix: 车辆信息后缀
    :return: rc_list 读取的坡段信息
    """
    file_path = "D:\Graduate Design\Experiment\dataworkspace\\newData\\routeData\\routeData_"+car_suffix
    rc_list = []
    for line in open(file_path):
        line_array = line.split()
        # Rc: 起始公里标，终止公里标，坡度值，坡度类型，限速值
        rc_list.append(Rc(line_array[0], line_array[1], line_array[2],line_array[4],line_array[3]))
    #print "rc_list length: "+ str(len(rc_list))
    return rc_list

def read_opt_point(car_suffix):
    """
    : description: 读取优化结果中的优化点信息
    :param car_suffix: 车辆信息后缀
    :return: opt_point_list 优化点集合
    """
    opt_point_list = []
    file_path = "D:\Graduate Design\Experiment\dataworkspace\\rawData\optimizeData\optimizeResult_"+car_suffix
    for line in open(file_path):
        line_array = line.split()
        # Point: 公里标，档位，速度，加速度
        opt_point_list.append(Point(line_array[0], line_array[1], line_array[2], line_array[5]))
    #print "opt_list length: "+str(len(opt_point_list))
    return opt_point_list

def cal_speed_variation(rc_list, opt_point_list, car_weight, car_length, car_suffix):
    """
    :description: 处理优化结果，得到速度变化段
    :param rc_list: 坡段信息
    :param opt_point_list: 优化结果信息
    :param car_weight: 本次处理的车辆车重
    :param car_length: 本次处理的车辆车长
    :param car_suffix: 车辆信息后缀
    :return:
    """
    k = 0
    rc_point = []       # 对应坡段，相当于二维数组，记录每个坡段中包含的优化点，X是坡段，Y是优化点
    rc_point_item = []  # 对应rc_point中的一维数组，记录某一个坡段中包含的优化点
    # 找到与坡段起始位置对应的优化点的index
    while k < len(opt_point_list):
        if opt_point_list[k].point_post >= rc_list[0].start_post:
            break
        else:
            k = k + 1
    #print "start point index: "+ str(k)


    # 将优化结果的点分配到对应的坡段中
    for i in range(len(rc_list)):
        rc_point_item = []
        while k < len(opt_point_list) and rc_list[i].start_post <= opt_point_list[k].point_post <= rc_list[i].end_post:
            rc_point_item.append(opt_point_list[k])
            k = k + 1
        '''
        print "i: "+ str(i)
        print "rc start: "+ str(rc_list[i].start_post)
        print "rc end: "+str(rc_list[i].end_post)
        print "point item length: "+ str(len(rc_point_item))
        print "point item start: "+ str(rc_point_item[0].point_post)
        print "point item end:" + str(rc_point_item[len(rc_point_item)-1].point_post)
        print "----------------------------------------"
        '''
        rc_point.append(rc_point_item)

    rc_point_set_list = []  # 记录坡段及坡段对应优化点集合
    for i in range(len(rc_point)):
        rc_point_set = RcPointSet(rc_list[i], rc_point[i])
        rc_point_set_list.append(rc_point_set)


    rc_speed_variation_list = []    # 记录所有坡段，及坡段对应的速度变化段，二维数组
    for i in range(len(rc_point_set_list)):
        last_acc = rc_point_set_list[i].point_arr[0].acc    # 坡段开始行驶的初始加速度
        last_vi = rc_point_set_list[i].point_arr[0].v       # 坡段开始行驶的初始速度
        variation_start_post = rc_point_set_list[i].point_arr[0].point_post     # 速度变化的起始公里标
        speed_variation_item = []   # 记录一个坡段的速度变化组合
        for j in range(len(rc_point_set_list[i].point_arr)):
            # 坡段i的第j个优化点和前面的加速度方向不相同，则前面的可截为一个速度变化段
            if(rc_point_set_list[i].point_arr[j].acc >= 0 and last_acc < 0) or (rc_point_set_list[i].point_arr[j].acc < 0 and last_acc >= 0):

                speed_variation_item.append(Variation(variation_start_post, rc_point_set_list[i].point_arr[j].point_post, last_vi, rc_point_set_list[i].point_arr[j].v))
                '''
                print "variation start: " + str(variation_start_post)
                print "variation end: "+ str(rc_point_set_list[i].point_arr[j].point_post)
                print "length: " + str(rc_point_set_list[i].point_arr[j].point_post-variation_start_post)
                print "--------------------------------"
                '''
                last_acc = rc_point_set_list[i].point_arr[j].acc
                last_vi = rc_point_set_list[i].point_arr[j].v
                variation_start_post = rc_point_set_list[i].point_arr[j].point_post
                #print str(speed_variation_item[len(speed_variation_item)-1].variation_type)
        # 处理该坡段最后剩余一个速度段
        rc_length = len(rc_point_set_list[i].point_arr)
        speed_variation_item.append(Variation(variation_start_post, rc_point_set_list[i].point_arr[rc_length-1].point_post, last_vi, rc_point_set_list[i].point_arr[rc_length-1].v))
        rc_speed_variation_list.append(speed_variation_item)
        #print str(speed_variation_item[len(speed_variation_item) - 1].variation_type)
        #print "***********************************************"



    # 上述过程只根据加速度的方向来划分段，可能存在相邻匀速段的情况
    # 合并相邻的匀速段，并重新分配速度段的类型：加速、匀速和减速
    for i in range(len(rc_speed_variation_list)):
        last_type = rc_speed_variation_list[i][0].variation_type
        if len(rc_speed_variation_list[i]) > 1: # 该坡段的速度组合为2个及以上
            j = 1
            while j < (len(rc_speed_variation_list[i])):
                if (rc_speed_variation_list[i][j].variation_type == last_type):
                    rc_speed_variation_list[i][j-1].update(rc_speed_variation_list[i][j].end_post, rc_speed_variation_list[i][j].v_o)
                    del rc_speed_variation_list[i][j]
                else:
                    last_type = rc_speed_variation_list[i][j].variation_type
                    j = j + 1

    for i in range(len(rc_speed_variation_list)):
        last_type = rc_speed_variation_list[i][0].variation_type
        if len(rc_speed_variation_list[i]) > 1: # 该坡段的速度组合为2个及以上
            j = 1
            while j < (len(rc_speed_variation_list[i])):
                if (rc_speed_variation_list[i][j].variation_type == last_type):
                    rc_speed_variation_list[i][j-1].update(rc_speed_variation_list[i][j].end_post, rc_speed_variation_list[i][j].v_o)
                    del rc_speed_variation_list[i][j]
                else:
                    last_type = rc_speed_variation_list[i][j].variation_type
                    j = j + 1

    '''
    out_test_file = "D:\\test.txt"
    with open(out_test_file, 'w') as f:
        for i in range(len(rc_speed_variation_list)):
            for j in range(len(rc_speed_variation_list[i])):
                f.write(str(rc_speed_variation_list[i][j].variation_type)+" ")
                #f.write(str(rc_speed_variation_list[i][j].start_post)+" "+str(rc_speed_variation_list[i][j].end_post)+" "+str(rc_speed_variation_list[i][j].variation_type) + " ")
            f.write('\n')
    f.close()
    '''


    # 计算速度变化段的百分比，以1%为单位
    for i in range(len(rc_speed_variation_list)):
        total_index = len(rc_speed_variation_list[i])-1
        total_length = float(rc_speed_variation_list[i][total_index].end_post - rc_speed_variation_list[i][0].start_post)
        percentage_sum = 0
        for j in range(len(rc_speed_variation_list[i])):
            # 如果是该坡段的最后一个速度变化段，则其百分比使用100减去前面的所有（为了保证总和为100%）
            if j == total_index:
                length_percentage = 100.0 - percentage_sum
            # 如果不是最后一个速度变化段，则按照长度计算百分比
            else:
                length = float(rc_speed_variation_list[i][j].end_post - rc_speed_variation_list[i][j].start_post)
                if total_length == 0:
                    length_percentage = 100
                else:
                    length_percentage = float(length/total_length)*100
            percentage_sum = percentage_sum + length_percentage
            rc_speed_variation_list[i][j].set_percentage(length_percentage)

    # 处理长度百分比是0的情况
    for i in range(len(rc_speed_variation_list)):
        j = 0
        while j < len(rc_speed_variation_list[i]):
            if abs(rc_speed_variation_list[i][j].percentage) < 0.001:
                del rc_speed_variation_list[i][j]
            else:
                j = j + 1

    # 获取前一段和后一段坡段的属性
    for i in range(len(rc_speed_variation_list)):
        if i == 0:
            fwd_rc = Rc(0,0,0,-1,None)
        else:
            fwd_rc = rc_list[i-1]
        if i == len(rc_list)-1:
            bwd_rc = Rc(0,0,0,-1,None)
        else:
            bwd_rc = rc_list[i+1]
        train_data_item = TrainDataItem1(car_weight, car_length, rc_list[i], fwd_rc, bwd_rc, rc_speed_variation_list[i])
        k = rc_list[i].rc_type
        train_data_set1[k].append(train_data_item)

    #print "check k cluster: " + str(len(train_data_set1))




if __name__ == '__main__':
    #cluster_num = 30
    #for k in range(0,30):
    #    out_pattern_file_path = "D:\Graduate Design\Experiment\dataworkspace\\trainData\level1_speedPattern\pattern\pattern_rc_"+str(k)
    #    out_pattern_param_file_path = "D:\Graduate Design\Experiment\dataworkspace\\trainData\level1_speedPattern\pattern_param\pattern_param_rc__"+str(k)

    car_info_file = "D:\Graduate Design\Experiment\dataworkspace\\rawData\carInfo\\carInfo_test.txt"
    for car in open(car_info_file):
        car_info_array = car.split()
        car_weight = car_info_array[0]
        car_length = int(float(car_info_array[1]))
        car_suffix = car_weight + '_' + str(car_length)
        rc_list = read_roadcategory(car_suffix)         # 读取线路坡段信息
        opt_point_list = read_opt_point(car_suffix)     # 读取优化结果中的优化点信息
        cal_speed_variation(rc_list, opt_point_list, int(car_weight), int(car_length), car_suffix)


    # 将速度模式的训练数据写入文件中
    out_pattern_file_path = "D:\Graduate Design\Experiment\dataworkspace\\testData\level1_speedPattern\pattern\pattern_rc_"
    out_pattern_param_file_path = "D:\Graduate Design\Experiment\dataworkspace\\testData\level1_speedPattern\pattern_param\pattern_param_rc_"
    class_type_dict = {}
    # total文件主要用于训练param的时候，需要对pattern列数据进行encoding，最好使用全部的pattern
    #total_pattern_file_path = "D:\Graduate Design\Experiment\dataworkspace\\trainData\level1_speedPattern\pattern_param\\total_pattern_patram"

    #with open(total_pattern_file_path,'w') as f:
    for k in range(len(train_data_set1)):
        with open(out_pattern_file_path+str(k),'w') as f1, open(out_pattern_param_file_path+str(k),'w') as f2:
            for i in range(len(train_data_set1[k])):
                data_str = str(train_data_set1[k][i].car_weight)+','+str(train_data_set1[k][i].car_length)
                data_str = data_str + ',' + str(train_data_set1[k][i].rc.gradient) + ',' + str(train_data_set1[k][i].rc.rc_type)  + ',' + str(train_data_set1[k][i].rc.length) + ',' + str(train_data_set1[k][i].rc.limit_value)
                data_str = data_str + ',' + str(train_data_set1[k][i].fwd_rc.gradient) + ',' + str(train_data_set1[k][i].fwd_rc.rc_type) + ',' + str(train_data_set1[k][i].fwd_rc.length)
                data_str = data_str + ',' + str(train_data_set1[k][i].bwd_rc.gradient) + ',' + str(train_data_set1[k][i].bwd_rc.rc_type) + ',' + str(train_data_set1[k][i].bwd_rc.length)
                variation_arr = train_data_set1[k][i].variation_arr
                class_str = '['
                for j in range(len(variation_arr)-1):
                    class_str = class_str + str(variation_arr[j].variation_type) + ' '
                class_str = class_str + str(variation_arr[len(variation_arr)-1].variation_type) + ']'
                if class_type_dict.has_key(class_str):
                    class_type_dict[class_str] = class_type_dict[class_str] + 1
                else:
                    class_type_dict[class_str] = 1
                f1.write(data_str + ',' + class_str + '\n')
                for j in range(len(variation_arr)):
                    f2.write(data_str + ',' + class_str + ',' + str(variation_arr[j].variation_type) + ',' + str(j+1) + ',' + str(variation_arr[j].percentage) + ',' + str(variation_arr[j].v_o) +'\n')
                        #f.write(data_str + ',' + class_str + ',' + str(variation_arr[j].variation_type) + ',' + str(j+1) + ',' + str(variation_arr[j].percentage) + ',' + str(variation_arr[j].v_o) + '\n')
        f1.close()
        f2.close()
    #f.close()

    '''
    label_data_file = "D:\Graduate Design\Experiment\dataworkspace\\trainData\level1_speedPattern\label_result"
    num = 0
    with open(label_data_file,'w') as f:
        for key, value in class_type_dict.iteritems():
            f.write(key + "," + str(value) + "," + str(num)+ "\n")
            num = num + 1
    f.close()
    '''
