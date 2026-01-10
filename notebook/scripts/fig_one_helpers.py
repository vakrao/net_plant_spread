import os
import sys
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

## function that returns 
## config that fulfills
## -> filtering 
## -> smallest RMSE
def find_best_local_configs(full_data,R,inc_fp):
    # for each seed
    # find RMSE distribution
    grouped_dat  = full_data.groupby(["b_w","b_b","shift","alpha","seed","D"])
    seed_rmse = []
    real_inc = pd.read_csv(inc_fp)
    real_inc = list(real_inc["Delta Orchard"])
    seed_configs = []
    counter = 0
    eps,pct = 30,.8
    for name,group in grouped_dat:
        
        param_cuml = list(group['monthly_cuml'])
        b_w = float(name[0])
        b_b =float(name[1])
        L = float(name[2])
        alpha = float(name[3])
        seed = float(name[4])
        D = float(name[5])
        param_inc = calc_month_incidence(param_cuml)
        if len(param_inc) < 14:
            continue
        
            
        rmse_val = calc_rmse(real_inc,param_inc)
        param_rmse = round(rmse_val,2)
        new_config = rf"$(\beta_b,\beta_w)$: ({b_b,b_w}), $D$: {str(D)}, $s_o$: {str(seed)}"
        param_config = new_config+","+" RMSE: "+str(param_rmse)
        all_tup = ((param_config,param_inc,seed),param_rmse)
        counter += 1
        if filter_seeds(param_inc,real_inc,eps,pct) == True:
            seed_configs.append(all_tup)
    sorted_by_second = sorted(seed_configs, key=lambda tup: tup[1])
   
    all_rmse =[s[1] for s in sorted_by_second]
    for a in range(0,len(all_rmse)):
        rmse_val = all_rmse[a]
        all_rmse[a] = round(rmse_val,2)
    all_rmse = set(all_rmse) 
    idx_amount = round(R*len(all_rmse)) 
    thresh_rmse = list(all_rmse)
    thresh_rmse = sorted(thresh_rmse)
    thresh_rmse = thresh_rmse[0:idx_amount]
    rmse_max = thresh_rmse[-1]
    thresh_rmse = set(thresh_rmse)
    unq_seeds = 0
    count = 0
    seed_ids = set()
    best_fit = []
    best_configs = []
    rmse_val = 0
    total_post = 0
    total_filt = 0 
    eps,pct = 30,0.8
    for count in range(0,len(sorted_by_second)):
        rmse_val = sorted_by_second[count][1]
        param_inc = sorted_by_second[count][0][1]
       
        total_post += 1
        best_configs.append(sorted_by_second[count])
        #count += 1
    print("percent of best fits: ",(total_filt/counter)*100)
    max_amount = round(R*counter)
   # max_amount = 300
    best_fit = sorted_by_second[0:max_amount]
    return best_fit

### Helper functions for best-fitting graph
def find_out_prob(full_data,inc,eps,pct):
    # for each seed
    # find RMSE distribution
    grouped_dat  = full_data.groupby(["b_w","b_b","shift","alpha","seed","D"])
    seed_rmse = []
    mean_inc = []
    seed_configs = {}
    counter = 0
    all_inc = []
    all_configs = 0
    good_seeds,all_seeds = set(),set()
    for name,group in grouped_dat:
        
        param_cuml = list(group['monthly_cuml'])
        b_w = float(name[0])
        b_b =float(name[1])
        L = float(name[2])
        alpha = float(name[3])
        seed = float(name[4])
        D = float(name[5])
        param_inc = calc_month_incidence(param_cuml)
        
        if len(param_inc) < 14:
            continue
        if len(mean_inc) == 0:
            mean_inc = [0 for i in range(0,len(param_inc))]
        if filter_seeds(param_inc,inc,eps,pct) == True:
            counter += 1
            good_seeds.add(seed)
        all_configs += 1
        all_seeds.add(seed)
    prob_out = (counter/all_configs)*100
    prob_seed = len(good_seeds)/len(all_seeds)
    return prob_out
    
def find_seed_prob(f_d,inc,eps,pct):
    g_d = f_d.groupby(["b_w","b_b","shift","alpha","seed","D"])
    seed_rmse = []
    mean_inc = []
    seed_configs = {}
    counter = 0
    all_inc = []
    all_seeds = 0
    good_seeds = set()
    all_seeds = set()
    for name,group in g_d:
        
        param_cuml = list(group['monthly_cuml'])
        b_w = float(name[0])
        b_b =float(name[1])
        L = float(name[2])
        alpha = float(name[3])
        seed = float(name[4])
        D = float(name[5])
        param_inc = calc_month_incidence(param_cuml)
        
        if len(param_inc) < 14:
            continue
        if len(mean_inc) == 0:
            mean_inc = [0 for i in range(0,len(param_inc))]
        if filter_seeds(param_inc,inc,eps,pct) == True:
            good_seeds.add(seed)
        all_seeds.add(seed)
    
    filter_prob = (len(good_seeds)/len(all_seeds))*100
    return filter_prob

def find_min_max_seed_range(seed_configs):
    min_val,max_val = [],[]
    min_val = [[] for i in range(0,len(seed_configs[0]))]
    max_val = [[] for i in range(0,len(seed_configs[0]))]
    for s in seed_configs:
        for i,value in enumerate(seed_configs[s]):
            min_val[i].append(value)
            max_val[i].append(value)
    min_err = [min(v) for v in min_val][1:]
    max_err = [max(v) for v in min_val][1:]
    return min_err,max_err
    