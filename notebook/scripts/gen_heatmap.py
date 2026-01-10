import numpy as np
import copy
import pandas as pd
import math as math
from mod_si import *


def calc_rmse(real_data,cleaned_data):
    if len(cleaned_data) != len(real_data):
        print(len(cleaned_data))
        print(len(real_data))
        raise ValueError("Invalid value provided")
        return []
    rmse = 0
    # start from 1 to ignore feburary 
    start_idx = 1
    total_count = 0
    for i in range(start_idx,len(cleaned_data)):
        diff = real_data[i]-cleaned_data[i]
        rmse += diff*diff
        total_count += 1
    rmse = rmse/(total_count*1.0)
    rmse = math.sqrt(rmse)
    return rmse

def calc_mae(real_data,cleaned_data):
    if len(cleaned_data) != len(real_data):
        print(len(cleaned_data))
        print(len(real_data))
        raise ValueError("Invalid value provided")
        return []
    mae = 0
    # start from 1 to ignore feburary 
    start_idx = 1
    total_count = 0
    for i in range(start_idx,len(cleaned_data)):
        diff = real_data[i]-cleaned_data[i]
        mae += diff*diff
        total_count += 1
    mae = mae/(total_count*1.0)
    #rmse = math.sqrt(rmse)
    return mae

# ASSUME real data is monthly
def clean_daily_data(syn_data,months):
    days_per_month = len(syn_data)//months
    f = []
    t = []
    i = days_per_month
    for m in range(0,(months)):
        f.append(syn_data[i])
        i += days_per_month
        t.append(m)
    return f,t

# get us incidence changes
def calc_month_incidence(data):
    inc = copy.deepcopy(data)
    for d in range(1,len(data)):
        inc[d] = data[d] - data[d-1]
    return inc


def read_real_data(real_file):
    real_dat = pd.read_csv(real_file)
    infec_farms = list(real_dat["Number of Orchards"])
    infec_farms = [int(i) for i in infec_farms]
    month_data = [i for i in range(0,len(infec_farms))]
    return infec_farms, month_data






    
