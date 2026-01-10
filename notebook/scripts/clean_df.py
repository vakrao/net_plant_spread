import pandas as pd
from gen_heatmap import *
from helpers import *

def clean_big_df(fn,real_infec):
    data = pd.read_csv(fn)
    all_qw = set(data["q_w"])
    all_qb = set(data["q_b"])
    
    beta_dict = {}
    data_dict = {}
    shift_dict = {}
    h_dict = {}
    for qb in all_qb:
        for qw in all_qw:
            # find matching qb and qw
            filt_df = data.query('q_w == @qw')
            filt_df = filt_df.query('q_b == @qb')
            seeds = set(filt_df['seed'])
            shifts = list(filt_df['shift_amount'])
            avg_shift = np.sum(shifts)/len(shifts)
            avg_rmse = 0
            if len(seeds) == 0:
                avg_rmse = -10
                beta_dict[(qb,qw)] = -10
                shift_dict[(qb,qw)] = 0
            else:
                for s in seeds:
                    seed_df = filt_df.query('seed == @s')
                    cuml_infec = list(seed_df["monthly_cuml"])
                    h_seed = list(seed_df["monthly_h"])
                    seed_inc = calc_month_incidence(cuml_infec)
                    if (qb,qw) not in data_dict:
                        data_dict[(qb,qw)] = [cuml_infec]
                        h_dict[(qb,qw)] = [h_seed]
                    else:
                        data_dict[(qb,qw)].append(cuml_infec)
                        h_dict[(qb,qw)].append(h_seed)
                    rmse_val = rmse_calc(seed_inc,real_infec)
                    avg_rmse += rmse_val
                avg_rmse = avg_rmse / len(seeds)
                beta_dict[(qb,qw)] = avg_rmse
                shift_dict[(qb,qw)] = avg_shift
    return beta_dict,data_dict,shift_dict,h_dict

def clean_big_static_df(fn,real_infec):
    data = pd.read_csv(fn)
    all_qw = set(data["q_w"])
    all_qb = set(data["q_b"])
    
    beta_dict = {}
    data_dict = {}
    shift_dict = {}
    h_dict = {}
    for qb in all_qb:
        for qw in all_qw:
            # find matching qb and qw
            filt_df = data.query('q_w == @qw')
            filt_df = filt_df.query('q_b == @qb')
            seeds = set(filt_df['seed'])
            avg_rmse = 0
            if len(seeds) == 0:
                avg_rmse = -10
                beta_dict[(qb,qw)] = -10
                shift_dict[(qb,qw)] = 0
            else:
                for s in seeds:
                    seed_df = filt_df.query('seed == @s')
                    cuml_infec = list(seed_df["monthly_cuml"])
                    h_seed = list(seed_df["monthly_h"])
                   
                    seed_inc = calc_month_incidence(cuml_infec)
                    if (qb,qw) not in data_dict:
                        data_dict[(qb,qw)] = [cuml_infec]
                        h_dict[(qb,qw)] = [h_seed]
                    else:
                        data_dict[(qb,qw)].append(cuml_infec)
                        h_dict[(qb,qw)].append(h_seed)
                    rmse_val = rmse_calc(seed_inc,real_infec)
                    avg_rmse += rmse_val
                avg_rmse = avg_rmse / len(seeds)
                beta_dict[(qb,qw)] = avg_rmse
    return beta_dict,data_dict,h_dict

def clean_big_temp_df(fn,real_infec,start_month):
    data = pd.read_csv(fn)
    all_qw = set(data["q_w"])
    all_qb = set(data["q_b"])
    
    beta_dict = {}
    data_dict = {}
    shift_dict = {}
    h_dict = {}
    for qb in all_qb:
        for qw in all_qw:
            # find matching qb and qw
            filt_df = data.query('q_w == @qw')
            filt_df = filt_df.query('q_b == @qb')
            filt_df = filt_df.query('start_m == @start_month')
            seeds = set(filt_df['seed'])
            avg_rmse = 0
            if len(seeds) == 0:
                avg_rmse = -10
                beta_dict[(qb,qw)] = -10
                shift_dict[(qb,qw)] = 0
            else:
                for s in seeds:
                    seed_df = filt_df.query('seed == @s')
                    cuml_infec = list(seed_df["monthly_cuml"])
                    h_seed = list(seed_df["monthly_h"])
                   
                    seed_inc = calc_month_incidence(cuml_infec)
                    if (qb,qw) not in data_dict:
                        data_dict[(qb,qw)] = [cuml_infec]
                        h_dict[(qb,qw)] = [h_seed]
                    else:
                        data_dict[(qb,qw)].append(cuml_infec)
                        h_dict[(qb,qw)].append(h_seed)
                    rmse_val = rmse_calc(seed_inc,real_infec)
                    avg_rmse += rmse_val
                avg_rmse = avg_rmse / len(seeds)
                beta_dict[(qb,qw)] = avg_rmse
    return beta_dict,data_dict,h_dict




def same_betas_avg_rmse(fn,real_infec):
    data = pd.read_csv(fn)
    all_months = set(data["start_m"])
    all_qw = set(data["q_w"])
    all_qb = set(data["q_b"])
    all_s = set(data['seed'])
    
    min_month_params = {}
    for m in all_months:
        min_rmse = 0
        min_qw,min_qb = [],[]
        month_data = data.query('start_m == @m')
        grouped_data = month_data.groupby(['q_w','q_b','seed','start_m'])
        month_seed = {}
        # find best RMSE for each group 
        for (q_w,q_b,seed,start_m),group in grouped_data:
            monthly_data = group["monthly_cuml"].values 
            h_seed = group["monthly_h"].values
            seed_inc = calc_month_incidence(list(monthly_data))
            
            seed_rmse = rmse_calc(seed_inc,real_infec)
            if (q_w,q_b) not in month_seed:
                month_seed[(q_w,q_b)] = [seed_rmse]
            else:
                month_seed[(q_w,q_b)].append(seed_rmse)
        min_val = 10000
        min_qb = 0
        min_qw = 0
        for ms in month_seed:
            month_seed[ms] = np.mean(month_seed[ms])
            if month_seed[ms] < min_val:
                min_val = month_seed[ms]
                min_qb = ms[1]
                min_qw = ms[0]
        min_month_params[m] = {'q_w':min_qw,'q_b':min_qb,'min_rmse':min_val}
    return min_month_params



def clean_big_init_df(fn,real_infec):
    data = pd.read_csv(fn)
    all_qw = set(data["q_w"])
    all_qb = set(data["q_b"])
    all_s = set(data['seed'])
    
    min_month_params = {}
    min_rmse = 0
    min_qw,min_qb = [],[]
    grouped_data = data.groupby(['q_w','q_b','seed'])
    month_seed = {}
    # find best RMSE for each group 
    for (q_w,q_b,seed),group in grouped_data:
        monthly_data = group["monthly_cuml"].values 
        h_seed = group["monthly_h"].values
        seed_inc = calc_month_incidence(list(monthly_data))
        
        seed_rmse = rmse_calc(seed_inc,real_infec)
        if (q_w,q_b) not in month_seed:
            month_seed[(q_w,q_b)] = [seed_rmse]
        else:
            month_seed[(q_w,q_b)].append(seed_rmse)
     
    for ms in month_seed:
        month_seed[ms] = np.mean(month_seed[ms])
            
    return month_seed

def clean_temporal_init_df(fn,real_infec):
    data = pd.read_csv(fn)
    all_qw = set(data["q_w"])
    all_qb = set(data["q_b"])
    all_s = set(data['seed'])
    
    min_month_params = {}
    min_rmse = 0
    min_qw,min_qb = [],[]
    grouped_data = data.groupby(['q_w','q_b','seed'])
    month_seed = {}
    # find best RMSE for each group 
    for (q_w,q_b,seed),group in grouped_data:
        monthly_data = group["monthly_cuml"].values 
        h_seed = group["monthly_h"].values
        seed_inc = calc_month_incidence(list(monthly_data))
        
        seed_rmse = rmse_calc(seed_inc,real_infec)
        if (q_w,q_b) not in month_seed:
            month_seed[(q_w,q_b)] = [seed_rmse]
        else:
            month_seed[(q_w,q_b)].append(seed_rmse)
     
    for ms in month_seed:
        month_seed[ms] = np.mean(month_seed[ms])
            
    return month_seed




def find_point_data(fn,real_infec):
    data = pd.read_csv(fn)
    all_qw = set(data["q_w"])
    all_qb = set(data["q_b"])
    all_s = set(data['seed'])
    
    min_month_params = {}
    min_rmse = 0
    min_qw,min_qb = [],[]
    grouped_data = data.groupby(['q_w','q_b','seed'])
    month_seed = {}
    # find best RMSE for each group 
    for (q_w,q_b,seed),group in grouped_data:
        monthly_data = group["monthly_cuml"].values 
        h_seed = group["monthly_h"].values
        seed_inc = calc_month_incidence(list(monthly_data))
            
        seed_rmse = rmse_calc(seed_inc,real_infec)
        if (q_w,q_b) not in month_seed:
            month_seed[(q_w,q_b)] = [seed_inc]
        else:
            month_seed[(q_w,q_b)].append(seed_inc)
    
            
    return month_seed

def find_temp_shift_point_data(fn,real_infec):
    data = pd.read_csv(fn)
    all_qw = set(data["q_w"])
    all_qb = set(data["q_b"])
    all_s = set(data['seed'])
    
    min_month_params = {}
    min_rmse = 0
    min_qw,min_qb = [],[]
    grouped_data = data.groupby(['q_w','q_b','seed','start_m'])
    month_seed = {}
    # find best RMSE for each group 
    for (q_w,q_b,seed,_),group in grouped_data:
        monthly_data = group["monthly_cuml"].values 
        h_seed = group["monthly_h"].values
        seed_inc = calc_month_incidence(list(monthly_data))
            
        seed_rmse = rmse_calc(seed_inc,real_infec)
        if (q_w,q_b) not in month_seed:
            month_seed[(q_w,q_b)] = [seed_inc]
        else:
            month_seed[(q_w,q_b)].append(seed_inc)
    
            
    return month_seed









