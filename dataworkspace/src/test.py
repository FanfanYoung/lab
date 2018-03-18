# coding=utf-8
_author__ = 'Angela'
import numpy as np
from data_structure import *
from sklearn.preprocessing import OneHotEncoder

if __name__ == '__main__':
   enc = OneHotEncoder(categorical_features=np.array([2]))
   enc.fit([[0,0,3],[1,1,0],[0,2,1],[1,0,2]])
   data = enc.transform([[0,1,2]]).toarray()
   for i in range(len(data)):
       for j in range(len(data[i])):
           print str(data[i][j]) +", ",
       print "\n"
