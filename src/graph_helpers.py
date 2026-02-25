import pandas as pd
import numpy as np
import copy
from gen_heatmap import *
from helpers import *


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
    num_amount = 0
    ret_dict = {}
    for a in all_eps:
        for b in all_pct:
            ret_dict[(a,b)] = 0
    seed_set = set()
    for name,group in grouped_dat:
        param_cuml = list(group['monthly_cuml'])
        b_w = float(name[0])
        b_b =float(name[1])
        L = float(name[2])
        alpha = float(name[3])
        D = float(name[4])
        seed = float(name[5])
        
        param_inc = calc_month_incidence(param_cuml)
        if len(param_inc) > 14:
            print(name) 
            continue
        if len(param_inc) < 14:
            continue
        
            
        rmse_val = calc_rmse(real_inc,param_inc)
        param_rmse = round(rmse_val,1)
        for a in all_eps:
            for b in all_pct:         
                if filter_seeds(param_inc,real_inc,a,b):
                    ret_dict[(a,b)] += 1
                    seed_set.add(seed)
    return ret_dict
    


"""
create_posterior_distribution
Description: takes in large. csv file and returns dataframe with rmse data
             and paramater configurations associated with rmse value
Returns: list of tuple(list{all config vals},int{RMSE})
"""

def create_posterior_distribution(full_data,inc_fp,post_fp,top_percent=1,eps=900,pct = 1):
    
    real_inc = pd.read_csv(inc_fp)
    b_b = set(full_data["b_b"])
    b_w = set(full_data["b_w"])
    real_inc = pd.read_csv(inc_fp)
    real_inc = list(real_inc["Delta Orchard"])
    beta_rmse = {}
    all_out,all_rmse,all_bw,all_bb,all_seed,all_shift,all_alpha,all_d = [],[],[],[],[],[],[],[]
    all_configs = []
    for bb in b_b:
        for ww in b_w:
            beta_rmse[(bb,ww)] = []
    for b in b_b:
        bb_dat = full_data.query("b_b == @b")
        for w in b_w: 
            filt_dat = bb_dat.query("b_w == @w")
            grouped_seed  = filt_dat.groupby(["seed","shift","alpha","D"])
            for name,group in grouped_seed:
                seed_val,shift_val,alpha_val,D_val = name[0],name[1],name[2],name[3]
                param_cuml = list(group['monthly_cuml'])
                if len(param_cuml) < 14:
                    diff = 14 - len(param_cuml)
                    d = [2000 for d in range(0,diff)]
                    param_cuml = param_cuml + d
                
                param_inc = calc_month_incidence(param_cuml)
               
                    
                #if (param_inc[1]) < 1:
                #    param_inc = [0 for i in range(0,len(param_inc))]
                
                param_rmse = calc_rmse(real_inc,param_inc)
                param_outbreak = param_cuml[-1]
                #if filter_seeds(param_inc,real_inc,30,.95):
                if filter_seeds(param_inc,real_inc,eps,pct):
                    all_configs.append(((param_outbreak,param_rmse,b,w,seed_val,shift_val,alpha_val,D_val),param_rmse))
                    beta_rmse[(b,w)].append(param_rmse)
                
    sort_config = sorted(all_configs,key=lambda x: x[1])
    min_amount = int(top_percent*len(all_configs))
    sort_config = sort_config[0:min_amount]
    # now save the sort_config:
    for (s,_) in sort_config:
        all_out.append(s[0])
        all_rmse.append(s[1])
        all_bb.append(s[2])
        all_bw.append(s[3])
        all_seed.append(s[4])
        all_shift.append(s[5])
        all_alpha.append(s[6])
        all_d.append(s[7])
    
    post_dict = {"Outbreak Size": all_out,"RMSE":all_rmse,"b_b":all_bb,"b_w":all_bw,"seed":all_seed,"shift":all_shift,"alpha":all_alpha,"D":all_d}
    post_df = pd.DataFrame.from_dict(post_dict)
                
    return sort_config,post_df

def top_fitting_seeds(seed_fn):
    all_tups = []
    with open(seed_fn,mode="r") as seed_dat:
        csvFile = csv.reader(seed_dat)
        for lines in csvFile:
            if lines[1] == "seed":
                continue
            seed_id = lines[1]
            rmse = round(float(lines[2]),2)
            tup = (seed_id,rmse)
            all_tups.append(tup)
    sorted_by_second = sorted(all_tups, key=lambda tup: tup[1])
    return sorted_by_second

# over all configurations
# which seeds emerge as fitting the best
# hold shift, alpha to similar values
def find_best_source_seeds(full_data,top_pct):
    grouped_dat = full_data.groupby(["b_w","b_b","shift","alpha"])
    seed_rmse = {}
    real_inc = pd.read_csv("../params/new_psa.csv")
    real_inc = list(real_inc["Delta Orchard"])
    min_seed = {}
    match_config = {}
    for name,group in grouped_dat:
        seed_group = group.groupby("seed")
        min_group_rmse = 100000
        min_seed_id = ""
        rmse_seed = []
        for seed_name,seed_all in seed_group:
            param_cuml = list(seed_all['monthly_cuml'])
            param_cuml = param_cuml[0:14]
            param_inc = calc_month_incidence(param_cuml)
            param_rmse = round(calc_rmse(real_inc,param_inc),2)
            if param_rmse < min_group_rmse:
                min_group_rmse = param_rmse
                min_seed_id = seed_name
           
            rmse_seed.append((seed_name,param_rmse))
        sorted_by_second = sorted(rmse_seed, key=lambda tup: tup[1],reverse=True)
        top_amount = int(top_pct*len(sorted_by_second))
        sorted_by_second = sorted_by_second[0:top_amount]
        match_config[name] = []
        for i,min_tup in enumerate(sorted_by_second):
            min_seed_id = min_tup[0]
            if min_seed_id not in min_seed:
                min_seed[min_seed_id] = 1
            else:
                 min_seed[min_seed_id] += 1
            min_grop_rmse = sorted_by_second[i]
            match_config[name].append((min_seed_id,min_group_rmse))

    return match_config,min_seed



def calc_rmse_stats(rmse_df,inc_fp):
    grouped_dat  = rmse_df.groupby(["b_w","b_b","shift","alpha","seed"])
    seed_rmse = []
    real_inc = pd.read_csv(inc_fp)
    real_inc = list(real_inc["Delta Orchard"])
    seed_configs = []
    counter = 0
    for name,group in grouped_dat:
        
        param_cuml = list(group['monthly_cuml'])
        b_b = float(name[1])
        b_w =float(name[0])
        L = float(name[2])
        alpha = float(name[3])
        seed = float(name[4])
        
        param_inc = calc_month_incidence(param_cuml)
        if len(param_inc) < 14:
            continue
        rmse_val = calc_rmse(real_inc,param_inc)
        param_rmse = round(rmse_val,2)

def find_rmse_distribution(line_list,real_inc):
    all_rmse = []
    for l in line_list:
        rmse = calc_rmse(real_inc,l)
        all_rmse.apppend(rmse)
    return all_rmse


def filter_large_df(df,b_b,b_w,D):
    df = df[df["b_b"] == b_b]
    df = df[df["b_w"] == b_w]
    df = df[df["D"] == D]
    return df

def find_viable(full_data,real_inc,eps,pct):
    # for each seed
    # find RMSE distribution
    grouped_dat  = full_data.groupby(["b_w","b_b","shift","alpha","seed","D"])
    seed_rmse = []
    mean_inc = []
    viable_configs = {}
    counter = 0
    all_inc = []
    all_seeds = 0
    min_RMSE = 500
    min_seed = 0
    for name,group in grouped_dat:
        param_cuml = list(group['monthly_cuml'])
        b_w = float(name[0])
        b_b =float(name[1])
        seed = str(name[4])
        D = float(name[5])
        param_inc = calc_month_incidence(param_cuml)
        if len(param_inc) < 13:
            continue
        if len(mean_inc) == 0:
            mean_inc = [0 for i in range(0,len(param_inc))]
        if filter_seeds(param_inc,real_inc,eps,pct) == True:
            for i,p in enumerate(param_inc):
                mean_inc[i] += p
            RMSE_val = calc_rmse(param_inc,real_inc)
            if RMSE_val < min_RMSE:
                min_RMSE = RMSE_val
                min_seed = counter
            viable_configs[counter] = {'seed':seed,'inc':param_inc,'RMSE':RMSE_val,'best':False}
            counter += 1
        all_seeds += 1
    viable_configs[min_seed]['best'] = True
        
    return viable_configs

def find_best(viable_configs):
    for v in viable_configs:
        config = viable_configs[v]
        if config['best']:
            return config
