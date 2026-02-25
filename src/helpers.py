import numpy as np
import copy
import pandas as pd
from gen_heatmap import *

# days in each month 
days = {1:31,2:28,3:31,4:30,5:31,6:30,7:31,8:31,9:30,10:31,11:30,12:31}

"""
filter_seeds
@DESCRIPTION: returns boolean, if syntehtic incidence a_i is within set filter band using eps,pct of the real incidence r_i
    -  real data falls within A(t) +- max(epsilon + epsilon*25% A(t)*25%), for each month t falls within the real data 
    - include A in the posterior distribution

@PARAMS: a_i (list), r_i (list), eps (float), pct (float)

@RETURNS: boolean 
    -> TRUE: configuration in filtering band
    -> FALSE: configuration not in filtering band
"""
def filter_seeds(a_i,r_i,eps,pct):
    for i in range(1,len(r_i)):
        lower_amount = max(0,a_i[i] - max(eps,pct*a_i[i]))
        upper_amount = a_i[i] + max(eps,pct*a_i[i])
        if r_i[i] < lower_amount or r_i[i] > upper_amount:
            return False
    return True



"""
find_best_config
@DESCRIPTION: finds smallest RMSE given movement dataframe 

@PARAMS: full_data (df), inc_fp (str), agg(str)
      full_data: data-frame containing all monthly incidence data
                 for every month corresponding to paramters
      inc_fp: file-path for incidence data
      agg: network aggregation type used to find configuration

@RETURNS: best_config (dict) 

    returns dictionary containing best fitting parameter configuration containg:
        ({b_b,b_w,L,D,seed,RMSE,inc (monthly), total (total infections)}
"""

def find_best_config(full_data,inc_fp,agg,eps,pct,viable=False,R=1):
    # for each seed
    # find RMSE distribution
    grouped_dat  = full_data.groupby(["b_w","b_b","shift","alpha","seed","D"])
    real_inc = pd.read_csv(inc_fp)
    real_inc = list(real_inc["Delta Orchard"])
    seed_configs = []
    #eps,pct = 30,.8
    for name,group in grouped_dat:
        param_cuml = list(group['monthly_cuml'])
        b_w = float(name[0])
        b_b =float(name[1])
        L = float(name[2])
        alpha = float(name[3])
        seed = float(name[4])
        D = float(name[5])
        
        param_inc = calc_month_incidence(param_cuml)
       
        rmse_val = calc_rmse(real_inc,param_inc)
        param_rmse = round(rmse_val,2)
        param_dict = {'b_b':b_b,"b_w":b_w,"L":L,"D":D,"seed":seed,"RMSE":param_rmse,"inc":param_inc,"total":param_cuml}
        all_tup = (param_dict,param_rmse)
        
        # creates viable set
        if filter_seeds(param_inc,real_inc,eps,pct) == True:
            seed_configs.append(all_tup)
    sorted_by_second = sorted(seed_configs, key=lambda tup: tup[1])
    best_fit = sorted_by_second[0]
    best_fit[0]["inc"] = best_fit[0]["inc"]
    best_fit[0]["total"] = best_fit[0]["total"]
    best_fit[0]["agg"] = agg

    if R < 1:
        max_amount = int(R * len(sorted_by_second))
        sorted_by_second = sorted_by_second[0:max_amount]

    if viable:
        viable_dict = {'b_b':[],
                      'b_w':[],
                      'RMSE':[],
                      'seed':[],
                      'D':[]}
        for config in sorted_by_second:
            for label in config[0]:
                if label in viable_dict:
                    val = config[0][label]
                    viable_dict[label].append(val)
        return viable_dict
    return best_fit[0]

"""
Finds number of eps,x configurations that 'fit' inside the constructed filtering band
"""
def num_fitting(full_data,inc_fp,agg,all_eps,all_pct):
    # for each seed
    # find RMSE distribution
    grouped_dat  = full_data.groupby(["b_w","b_b","shift","alpha","D","seed"])
    real_inc = pd.read_csv(inc_fp)
    real_inc = list(real_inc["Delta Orchard"])
    seed_configs = []

def prune_i(full_i,all_t,T):
    clean_i = {}
    finished_i = []
    last_val = full_i[-1]
    if last_val > T:
        for i in range(0,len(full_i)):
            rounded_t = round(all_t[i])
            if rounded_t not in clean_i:
                clean_i[rounded_t] = [full_i[i]]  
            else:
                clean_i[rounded_t].append(full_i[i])
        for c in clean_i:
            clean_i[c] = np.max(clean_i[c])
        finished_i = list(clean_i.values())
        return finished_i
    else:
        finished_i = copy.deepcopy(full_i)
        for i in range(len(full_i),T):
            finished_i.append(full_i[-1])
    return finished_i



"""
clean_temp_shift 
Description: shortens daily infection list to create
monthly infection list. We strictly filter the daily infection based on the number of days in a month
Parameters: 
    i(list) - daily list of infections
    t_m(int) - lenght of list of real infections
    cal_month(int) - starting calendar month ID
    shifts(int) - determines how many months left shift occurs
Returns:
    shift_i (list) - aggregated monthly infections
    clean_t (list) - month associated with each shift
"""
def clean_temp_shift(i,t_m,cal_month,shifts):
    month_counter = 0
    shift_i = []
    curr_days = 0
    ord_count = cal_month
    assert(len(i) > 0 ),"Error: i is too small"
    while(month_counter < t_m):
        days_amount = days[ord_count]
        curr_days += days_amount
        assert(curr_days <= len(i)), f"Error: curr_days:{curr_days} is greater than length of i: {len(i)}"
        # this samples the cumulative value for the month, subtract by 1 to account for indexing of lists
        month_value = i[curr_days-1]
        shift_i.append(month_value) 
        ord_count += 1
        if ord_count > 12:
            ord_count = 1
        month_counter += 1
    # pop out the shifts
    shift_i = shift_i[shifts:]
    clean_t = [i for i in range(0,len(shift_i))]
    return shift_i,clean_t

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
