import pandas as pd
import numpy as np
import copy
from gen_heatmap import *
from helpers import *


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



## go through incidence 
##    -  real data falls within A(t) +- max(epsilon + epsilon*25% A(t)*25%) 
##       for each month t falls within the real data, 
##         include A in the posterior distribution."
def filter_seeds(a_i,r_i,eps,pct):
    
    for i in range(1,len(r_i)):
        lower_amount = max(0,a_i[i] - max(eps,pct*a_i[i]))
        upper_amount = a_i[i] + max(eps,pct*a_i[i])
        if r_i[i] < lower_amount or r_i[i] > upper_amount:
            return False
    return True



"""
find_best_config
DESCRIPTION: finds smallest RMSE given movement dataframe 
PARAMS: full_data (df), inc_fp (str), agg(str)
      full_data: data-frame containing all monthly incidence data
                 for every month corresponding to paramters
      inc_fp: file-path for incidence data
      agg: network aggregation type used to find configuration

RETURNS: best_config (dict) 

    returns dictionary containing best fitting parameter configuration containg:
        ({b_b,b_w,L,D,seed,RMSE,inc (monthly), total (total infections)}
"""

def find_best_config(full_data,inc_fp,agg,eps,pct):
    # for each seed
    # find RMSE distribution
    grouped_dat  = full_data.groupby(["b_w","b_b","shift","alpha","seed","D"])
    real_inc = pd.read_csv(inc_fp)
    real_inc = list(real_inc["Delta Orchard"])[1:]
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
        
        param_cuml = param_cuml[1:]
        param_inc = calc_month_incidence(param_cuml)
       
        rmse_val = calc_rmse(real_inc,param_inc)
        param_rmse = round(rmse_val,2)
        param_dict = {'b_b':b_b,"b_w":b_w,"L":L,"D":D,"seed":seed,"RMSE":param_rmse,"inc":param_inc,"total":param_cuml}
        all_tup = (param_dict,param_rmse)
        
        if filter_seeds(param_inc,real_inc,eps,pct) == True:
            seed_configs.append(all_tup)
    sorted_by_second = sorted(seed_configs, key=lambda tup: tup[1])
    best_fit = sorted_by_second[0]
    best_fit[0]["inc"] = best_fit[0]["inc"]
    best_fit[0]["total"] = best_fit[0]["total"]
    best_fit[0]["agg"] = agg
    return best_fit[0]

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
    print("num unique seeds: ",len(seed_set))
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
                #param_cuml = param_cuml[0:14]
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

"""
Description: Searches through dataframe to find smallest 
        percentage (defined as R) of RMSE values
Parameters:
    full_data (pandas dataframe: contains all cumulative infection data)
    R (float: percentage to focus RMSE on)
    inc_fp (str: string for incidecne file path)
    eps (int: int for minimum infections to add to for filter function)
    pct (float: percenrage paramter for filter parmeter ) 
"""
def find_ensemble_configs(full_data,R,inc_fp,eps,pct):
    # for each seed
    # find RMSE distribution
    grouped_dat  = full_data.groupby(["b_w","b_b","shift","alpha","seed","D"])
    seed_rmse = []
    real_inc = pd.read_csv(inc_fp)
    real_inc = list(real_inc["Delta Orchard"])
    seed_configs = []
    counter = 0
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
       # if filter_seeds(param_inc,real_inc,eps,pct) == True:
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
    eps,pct = 20,.50
    while(rmse_val <= rmse_max):
        rmse_val = sorted_by_second[count][1]
        param_inc = sorted_by_second[count][0][1]
        if filter_seeds(param_inc,real_inc,eps,pct) == True:
            total_filt += 1
        total_post += 1
        if rmse_val <= max(thresh_rmse):
            best_fit.append(sorted_by_second[count])
        #best_configs.append(sorted_by_second[count])
        count += 1
    print("percent of best fits: ",(total_filt/counter)*100)
    max_amount = round(R*counter)
   # max_amount = 300
   # best_fit = sorted_by_second[0:max_amount]
    print(best_fit[0][1])
    return best_fit
























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

def find_worst_configs(full_data,top_amount):
    # for each seed
    # find RMSE distribution
    #seed_data = full_data.query("seed == @seed_id")
    grouped_dat  = full_data.groupby(["b_w","b_b","shift","alpha","seed"])
    seed_rmse = []
    real_inc = pd.read_csv("../params/stepped_data_7.csv")
    real_inc = list(real_inc["Delta Orchard"])
    seed_configs = []
    for name,group in grouped_dat:
        param_cuml = list(group['monthly_cuml'])
        param_inc = calc_month_incidence(param_cuml)
        param_rmse = round(calc_rmse(real_inc,param_inc),2)
        param_config = str(name)+","+str(param_rmse)
        all_tup = ((param_config,param_inc),param_rmse)
        seed_configs.append(all_tup)
    sorted_by_second = (sorted(seed_configs,reverse=True, key=lambda tup: tup[1]))
    top_ten = sorted_by_second[0:top_amount]
    return top_ten


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



## seed_id: string of seed to search through
## full_data: dataframe containing seed id, beta configs, shift_vals, and alpha
def find_no_outbreak_seeds(seeds,max_outbreak,full_data):
    # for each seed
    # find RMSE distribution
    real_inc = pd.read_csv("../params/stepped_data_7.csv")
    real_inc = list(real_inc["Delta Orchard"])
    no_outbreak = []
    cause_outbreak = False
    for seed in seeds: 
        seed_data = full_data.query("seed == @seed")
        grouped_seed  = seed_data.groupby(["q_w","q_b","shift","alpha"])
        seed_rmse = []
        
        for name,group in grouped_seed:
            param_cuml = list(group['monthly_cuml'])
            outbreak_size = param_cuml[-1]
            if outbreak_size > max_outbreak:
                cause_outbreak = True
                break
        if cause_outbreak == False:
            no_outbreak.append(seed)
        cause_outbreak = True
            
    return no_outbreak

## seed_id: string of seed to search through
## full_data: dataframe containing seed id, beta configs, shift_vals, and alpha
def find_always_outbreak_seeds(seeds,max_outbreak,full_data):
    # for each seed
    # find RMSE distribution
    real_inc = pd.read_csv("../params/stepped_data_7.csv")
    real_inc = list(real_inc["Delta Orchard"])
    outbreak_seed = []
    cause_outbreak = False
    for seed in seeds: 
        seed_data = full_data.query("seed == @seed")
        grouped_seed  = seed_data.groupby(["q_w","q_b","shift","alpha"])
        seed_rmse = []
        
        for name,group in grouped_seed:
            param_cuml = list(group['monthly_cuml'])
            outbreak_size = param_cuml[-1]
            if outbreak_size < max_outbreak:
                cause_outbreak = True
                break
        
        if cause_outbreak == False:
            outbreak_seed.append(seed)
        cause_outbreak = False
    
    return outbreak_seed


def seed_shift_outbreak_size(full_data):
    ## 
     # for each seed
    # find RMSE distribution
    shifts = set(full_data['shift'])
    shift_dist = {}
    all_outs = []
    for shift in shifts:
        seed_data = full_data.query("shift == @shift")
        grouped_seed  = seed_data.groupby(["q_w","q_b","seed","alpha"])
        seed_rmse = []
        real_inc = pd.read_csv("../params/stepped_data_7.csv")
        real_inc = list(real_inc["Delta Orchard"])
        shift_dist[shift] = []
        for name,group in grouped_seed:
            param_cuml = list(group['monthly_cuml'])
            out_size = param_cuml[-1]
            shift_dist[shift].append(out_size)
        
    return shift_dist
    




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
