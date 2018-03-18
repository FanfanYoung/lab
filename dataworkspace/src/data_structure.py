#coding=utf-8
class Rc:
    def __init__(self, start_post, end_post, gradient, rc_type, limit_value = None):
        self.start_post = int(start_post)
        self.end_post = int(end_post)
        self.gradient = float(gradient)
        self.rc_type = int(rc_type)
        self.length = self.end_post - self.start_post
        if limit_value is None:
            self.limit_value = 80.0
        else:
            self.limit_value = limit_value
    def set_limit(self, limit_value):
        self.limit_value = float(limit_value)

class Point:
    def __init__(self, point_post, gear=None, v=None, acc = None):
        self.point_post = float(point_post)
        if gear is None:
            self.gear = -100
        else:
            self.gear = int(gear)
        if v is None:
            self.v = 0.0
        else:
            self.v = float(v)
        if acc is None:
            self.acc = 0.0
        else:
            self.acc = float(acc)

# 原始限速信息
class Limit:
    def __init__(self, start_post, end_post, limit_value):
        self.start_post = int(start_post)
        self.end_post = int(end_post)
        self.limit_value = float(limit_value)


# 坡段-该坡段相应优化点集合
class RcPointSet:
    def __init__(self, rc_info, point_arr = []):
        self.rc_info = rc_info
        self.point_arr = point_arr

# 速度变化段
class Variation:
    def __init__(self, start_post, end_post, v_i, v_o):
        self.start_post = float(start_post)
        self.end_post = float(end_post)
        self.v_i = float(v_i)
        self.v_o = float(v_o)
        if abs(self.v_o - self.v_i) < 4.0:      # 速度变化在4以内，则认为是匀速
            self.variation_type = 0
        elif self.v_o > self.v_i:               # 末速度大于入速度，变化类型为加速
            self.variation_type = 1
        else:                                   # 末速度小于入速度，变化类型为减速
            self.variation_type = -1
    # update函数主要用于合并前后速度段，更新新的末位置和末速度
    def update(self, end_post, v_o):
        self.end_post = end_post
        self.v_o = v_o
        if abs(self.v_o - self.v_i) < 4.0:
            self.variation_type = 0
        elif self.v_o > self.v_i:
            self.variation_type = 1
        else:
            self.variation_type = -1
    def set_percentage(self, percentage):
        self.percentage = percentage


# 速度层训练数据项
class TrainDataItem1:
    def __init__(self, car_weight, car_length, rc, fwd_rc, bwd_rc, variation_arr = []):
        self.car_weight = car_weight
        self.car_length = car_length
        self.rc = rc
        self.fwd_rc = fwd_rc
        self.bwd_rc = bwd_rc
        self.variation_arr = variation_arr
