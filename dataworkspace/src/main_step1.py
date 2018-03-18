# coding=utf-8
_author__ = 'Angela'
from sklearn.cluster import KMeans
from data_structure import *
import matplotlib.pyplot as plt
from sklearn.manifold import TSNE
from sklearn import preprocessing
import pandas as pd

'''
主要做坡段聚类处理，是整个研究路线的第一个部分
'''
if __name__ == '__main__':
    car_info_file = "D:\Graduate Design\Experiment\dataworkspace\\rawData\carInfo\carInfo.txt"
    route_data = []
    label_data = []

    # 读取限速信息，记录在limit_list中
    limit_data_file = "D:\Graduate Design\Experiment\dataworkspace\\rawData\\routeData_down\\newLimit"
    limit_list = []
    for line in open(limit_data_file):
        line_array = line.split()
        limit_list.append(Limit(line_array[0], line_array[1], line_array[2]))

    # 合并相邻限速值相同的限速段
    limit_merge_list = []
    last_value = limit_list[0].limit_value  # 记录当前限速值
    last_start_post = limit_list[0].start_post
    for i in range(len(limit_list)):
        if limit_list[i].limit_value != last_value:
            limit_merge_list.append(Limit(last_start_post, limit_list[i].start_post, last_value))
            last_value = limit_list[i].limit_value
            last_start_post = limit_list[i].start_post
    limit_merge_list.append(Limit(last_start_post, limit_list[len(limit_list) - 1].end_post, last_value))

    out = "D:/newList"
    with open(out,'w') as f:
        for i in range(len(limit_merge_list)):
            f.write(str(limit_merge_list[i].start_post)+" "+str(limit_merge_list[i].end_post)+" "+str(limit_merge_list[i].limit_value)+"\n")
    f.close()


    for car in open(car_info_file):
        car_info_array = car.split()
        car_weight = car_info_array[0]
        car_length = int(float(car_info_array[1]))
        car_suffix = str(car_weight)+"_"+str(car_length)

        # 读取坡段信息，记录在rc_list中
        route_data_file = "D:\Graduate Design\Experiment\dataworkspace\\rawData\\routeData_down\\cat_info_"+car_suffix
        rc_list = []
        for line in open(route_data_file):
            line_array = line.split()
            rc_list.append(Rc(line_array[0], line_array[1], line_array[2],line_array[3],None))

        #print len(rc_list)


        # 找到限速信息在路段中的起始下标和终止下标
        rc_start_post = rc_list[0].start_post
        rc_end_post = rc_list[len(rc_list) - 1].end_post
        limit_start_index = -1  # 有效限速信息的起始下标
        limit_end_index = len(limit_merge_list) - 1  # 有效限速信息的终止下标
        for i in range(len(limit_merge_list)):
            #print "i: "+str(i)
            #print "rc_start_post: "+str(rc_start_post)
            #print "rc_end_post: "+str(rc_end_post)
            #print "limit_start_post: "+str(limit_merge_list[i].start_post)
            #print "limit_end_post: "+str(limit_merge_list[i].end_post)
            #print "-----------------------------"
            if (rc_start_post <= limit_merge_list[i].start_post <= rc_end_post or rc_start_post <= limit_merge_list[i].end_post <= rc_end_post):
                limit_start_index = i
                break
            if limit_merge_list[i].start_post <= rc_start_post <= limit_merge_list[i].end_post:
                limit_start_index = i
                break
        for i in range(limit_start_index, len(limit_merge_list)):
            if limit_merge_list[i].start_post >= rc_end_post:
                limit_end_index = i - 1
                break

        # 合并限速信息和坡段信息
        rc_merge_list = []
        k = limit_start_index
        i = 0
        while i < len(rc_list):
            # 当前坡段全部在一个限速段里
            if rc_list[i].end_post <= limit_merge_list[k].end_post or k > limit_end_index:
                new_rc = Rc(rc_start_post, rc_list[i].end_post, rc_list[i].gradient, rc_list[i].rc_type,None)
                new_rc.set_limit(limit_merge_list[k].limit_value)
                rc_merge_list.append(new_rc)
                rc_start_post = rc_list[i].end_post
                i = i + 1
            # 当前坡段跨两个限速段
            elif k <= limit_end_index:
                new_rc = Rc(rc_start_post, limit_merge_list[k].end_post, rc_list[i].gradient, rc_list[i].rc_type, None)
                new_rc.set_limit(limit_merge_list[k].limit_value)
                rc_merge_list.append(new_rc)
                rc_start_post = limit_merge_list[k].end_post
                k = k + 1


        # 将新分割的坡段信息写入新的数据文件中，并将数据存储在route_data中，用于整个做聚类

        for i in range(len(rc_merge_list)):
            route_data_item = []
            route_data_item.append(rc_merge_list[i].gradient)
            route_data_item.append((rc_merge_list[i].end_post-rc_merge_list[i].start_post))
            route_data_item.append(rc_merge_list[i].limit_value)

            label_data_item = []
            label_data_item.append(car_weight)
            label_data_item.append(car_length)
            label_data_item.append(rc_merge_list[i].start_post)
            label_data_item.append(rc_merge_list[i].end_post)
            label_data_item.append(rc_merge_list[i].gradient)
            label_data_item.append((rc_merge_list[i].end_post-rc_merge_list[i].start_post))
            label_data_item.append(rc_merge_list[i].limit_value)

            if(i == 0):
                route_data_item.append(0)
                label_data_item.append(0)
            else:
                route_data_item.append(rc_merge_list[i-1].gradient)
                label_data_item.append(rc_merge_list[i-1].gradient)
            if(i==len(rc_merge_list)-1):
                route_data_item.append(0)
                label_data_item.append(0)
            else:
                route_data_item.append(rc_merge_list[i+1].gradient)
                label_data_item.append(rc_merge_list[i+1].gradient)
            route_data.append(route_data_item)
            label_data.append(label_data_item)

    print len(route_data)
    print len(label_data)

    route_data_backup = route_data  #备份route_data
    # route_data用于聚类，需要进行归一化操作
    route_data = preprocessing.scale(route_data,axis = 0)

    # 输出归一化之后的数据，用于检查归一化
    out_path = "D:\Graduate Design\Experiment\dataworkspace\\processData\\normalizeData1.txt"
    with open(out_path, 'w') as f:
        for i in range(len(route_data)):
            for j in range(len(route_data[i])):
                f.write(str(route_data[i][j])+" ")
            f.write("\n")
    f.close()

    # 暂定：由于坡度值和长短影响较大，将归一化后的这两列属性*2
    for i in range(len(route_data)):
        route_data[i][0] = route_data[i][0]*2
        route_data[i][1] = route_data[i][1]*2



    #tsne = pd.DataFrame(tsne.embedding_, index = route_data.index)

    '''

    # 循环检查k从10到100的类间距离，选出比较合适的聚类个数k值
    out_path = "D:/inertia.txt"
    with open(out_path,'w') as f:
        for k in range(10,100):
            estimator = KMeans(n_clusters=k,random_state=0)
            s = estimator.fit(route_data)
            inertia = estimator.inertia_
            f.write(str(k)+" "+str(inertia)+"\n")
            print str(k)+":  " + str(inertia)
    f.close()



    '''
    # 暂时选出30比较合适，进行k=30的聚类
    estimator = KMeans(n_clusters=30, random_state=0)
    s = estimator.fit(route_data)
    inertia = estimator.inertia_
    print inertia



    # 按照聚类结果，将数据分类写入文件
    out_path = "D:\Graduate Design\Experiment\dataworkspace\\processData\\routeCluster\clusterRoute.txt"
    for j in range(0,30):
        out_path = "D:\Graduate Design\Experiment\dataworkspace\\processData\\routeCluster\clusterRoute_"+str(j)+".txt"
        with open(out_path,'w') as f:
            for i in range(len(route_data_backup)):
                if(str(estimator.labels_[i]) == str(j)):
                    string = ""
                    string = string + str(route_data_backup[i][0]) + " " + str(route_data_backup[i][1]) + " " + str(route_data_backup[i][2]) + " " + str(route_data_backup[i][3]) + " " + str(route_data_backup[i][4]) + " "
                    string = string + str(estimator.labels_[i])+"\n"
                    f.write(string)
        f.close()

    '''
    # 根据聚类结果，将数据全部写入文件，并打上类标
    out_path = "D:\Graduate Design\Experiment\dataworkspace\\trainData\\routeData\\routeData_label.txt"
    with open(out_path,'w') as f:
        for i in range(len(route_data_backup)):
            string = str(route_data_backup[i][0]) + " " + str(route_data_backup[i][1]) + " " + str(route_data_backup[i][2]) + " " + str(route_data_backup[i][3]) + " " + str(route_data_backup[i][4]) + " "
            string = string + str(estimator.labels_[i]) + "\n"
            f.write(string)
    f.close()
    '''
    '''
    # 将数据使用tsne降维，可视化聚类结果
    tsne = TSNE(n_components=2, init='pca',random_state=0)
    X_tsne = tsne.fit_transform(route_data)
    plt.figure(figsize=(12,10))
    plt.scatter(X_tsne[:,0],X_tsne[:,1],c=estimator.labels_,label=str(k))
    plt.show()
    '''


    # 根据聚类结果对数据进行打标
    label_file_path = "D:\Graduate Design\Experiment\dataworkspace\\newData\labelData\\routeData_label.txt"
    # 车重，车长，起始公里标，终止公里标，坡度值，长度，限速值，前坡段坡度值，后坡段坡度值
    with open(label_file_path,'w') as f:
        for i in range(len(label_data)):
            for j in range(len(label_data[i])):
                f.write(str(label_data[i][j])+" ")
            f.write(str(estimator.labels_[i])+"\n")
    f.close()


    k = 0
    for car in open(car_info_file):
        car_info_array = car.split()
        car_weight = car_info_array[0]
        car_length = int(float(car_info_array[1]))
        car_suffix = str(car_weight)+"_"+str(car_length)

        with open("D:\Graduate Design\Experiment\dataworkspace\\newData\\routeData\\routeData_"+car_suffix,'w') as f:
            while k < len(label_data):
                if(str(label_data[k][0])+"_"+str(label_data[k][1])!=car_suffix):
                    break
                else:
                    # 起始公里标，终止公里标，坡度值，限速，类型，长度
                    f.write(str(label_data[k][2])+" "+str(label_data[k][3])+" "+str(label_data[k][4])+" "+str(label_data[k][6])+" "+str(estimator.labels_[k])+" "+str(label_data[k][5])+"\n")
                    k=k+1
        f.close()



    # 将所有优化结果按照坡段类型的不同写入到各自的文件中
    for car in open(car_info_file):
        car_info_array = car.split()
        car_weight = car_info_array[0]
        car_length = int(float(car_info_array[1]))
        car_suffix = str(car_weight) + "_" + str(car_length)

        # 读取坡段信息，记录在rc_list中
        route_data_file = "D:\Graduate Design\Experiment\dataworkspace\\newData\\routeData\\routeData_" + car_suffix
        rc_list = []
        for line in open(route_data_file):
            line_array = line.split()
            rc = Rc(line_array[0], line_array[1], line_array[2], line_array[4], None)
            rc.set_limit(line_array[3])
            rc_list.append(rc)


        opt_list = []
        opt_data_file = "D:\Graduate Design\Experiment\dataworkspace\\rawData\\optimizeData\\optimizeResult_"+car_suffix

        for line in open(opt_data_file):
            line_array = line.split()
            opt_list.append(Point(line_array[0], line_array[1], line_array[2], None))
        #print len(opt_list)
        k = 0
        i = 0
        out_file_path = "D:\Graduate Design\Experiment\dataworkspace\\processData\\routeData\\rc-"
        while k < len(rc_list):
            start_post = rc_list[k].start_post
            end_post = rc_list[k].end_post
            #print "start_post: "+str(start_post)+"   end_post: "+str(end_post)
            file_path = out_file_path + str(rc_list[k].rc_type)
            with open(file_path,'a') as f:
                while i < len(opt_list):
                    point_post = int(opt_list[i].point_post)
                    if start_post > point_post:
                        i = i + 1
                    elif start_post <= point_post <= end_post:
                        #print "yes"
                        f.write(str(opt_list[i].v)+' ')
                        i = i + 1
                    else:
                        f.write("\n")
                        break
                if i >= len(opt_list):
                    f.write("\n")
            f.close()
            k = k + 1




    









