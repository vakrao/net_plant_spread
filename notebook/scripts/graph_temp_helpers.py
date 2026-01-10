import pandas as pd
import numpy as np
import copy
from gen_heatmap import *
from helpers import *


def find_rmse_distribution(line_list,real_inc):
    all_rmse = []
    for l in line_list:
        rmse = rmse_calc(l,real_inc)
        all_rmse.apppend(rmse)
    return all_rmse


## seed_id: string of seed to search through
## full_data: dataframe containing seed id, beta configs, shift_vals, and alpha
def filter_seeds(seed_id,full_data):
    # for each seed
    # find RMSE distribution
    seed_data = full_data.query("seed == @seed_id")
    grouped_seed  = seed_data.groupby(["q_w","q_b","start_month","alpha"])
    seed_rmse = []
    real_inc = pd.read_csv("../params/stepped_data_7.csv")
    real_inc = list(real_inc["Delta Orchard"])
    for name,group in grouped_seed:
        param_cuml = list(group['monthly_cuml'])
        param_inc = calc_month_incidence(param_cuml)
        param_rmse = calc_rmse(real_inc,param_inc)
        seed_rmse.append(param_rmse)
    return seed_rmse
def shift_rmse_dist(full_data):
    # for each seed
    # find RMSE distribution
    shifts = set(full_data['start_month'])
    shift_dist = {}
    for shift in shifts:
        seed_data = full_data.query("start_month == @start_month")
        grouped_seed  = seed_data.groupby(["q_w","q_b","seed","alpha"])
        seed_rmse = []
        real_inc = pd.read_csv("../params/stepped_data_7.csv")
        real_inc = list(real_inc["Delta Orchard"])
        for name,group in grouped_seed:
            param_cuml = list(group['monthly_cuml'])
            param_inc = calc_month_incidence(param_cuml)
            param_rmse = calc_rmse(real_inc,param_inc)
            seed_rmse.append(param_rmse)
        shift_dist[shift] = seed_rmse
    return shift_dist
def alpha_rmse_dist(full_data):
    # for each seed
    # find RMSE distribution
    alphas = set(full_data['alpha'])
    alpha_dist = {}
    for alpha in alphas:
        seed_data = full_data.query("alpha == @alpha")
        grouped_seed  = seed_data.groupby(["q_w","q_b","seed","shift"])
        seed_rmse = []
        real_inc = pd.read_csv("../params/stepped_data_7.csv")
        real_inc = list(real_inc["Delta Orchard"])
        for name,group in grouped_seed:
            param_cuml = list(group['monthly_cuml'])
            param_inc = calc_month_incidence(param_cuml)
            param_rmse = calc_rmse(real_inc,param_inc)
            seed_rmse.append(param_rmse)
        alpha_dist[alpha] = seed_rmse
    return alpha_dist

def find_rmse_seeds(seeds,full_data,param_configs):
    all_rmse = {}
    for s in seeds:
        seed_rmse = filter_seeds(s,full_data)
        all_rmse[s] = seed_rmse
    return all_rmse
def qb_qw_rmse_dist(full_data,param_configs):
    q_b = set(full_data["q_b"])
    q_w = set(full_data["q_w"])
    beta_rmse = {}
    real_inc = pd.read_csv("../params/stepped_data_7.csv")
    real_inc = list(real_inc["Delta Orchard"])
    for b in q_b:
        for w in q_w:
            beta_rmse[(b,w)] = []

    for b in q_b:
        bb_dat = full_data.query("q_b == @b")
        for w in q_w: 
            filt_dat = bb_dat.query("q_w == @w")
            grouped_seed  = filt_dat.groupby(["seed","shift","alpha"])
            seed_rmse = []
            for name,group in grouped_seed:
                param_cuml = list(group['monthly_cuml'])
                param_inc = calc_month_incidence(param_cuml)
                param_rmse = calc_rmse(param_inc,real_inc)
                beta_rmse[(b,w)].append(param_rmse)
    return beta_rmse
def generate_rmse_df(seeds,full_data,param_configs={}):
    seed_rmse_all = find_rmse_seeds(seeds,full_data,param_configs)
    all_seed = []
    rmse_dist = []
    for seed in seed_rmse_all:
        seed_rmse_dist = seed_rmse_all[seed]
        seed_id = [seed for i in range(0,len(seed_rmse_dist))]
        rmse_dist = rmse_dist+seed_rmse_dist
        all_seed = all_seed + seed_id
    
    data_dict = {'seed':all_seed,'rmse_dist':rmse_dist}
    dist_df = pd.DataFrame.from_dict(data_dict)
    dist_df.to_csv("../src/E0/seed_dist.csv")
    return dist_df

def generate_qbqw_rmse_df(full_data,param_configs):
    beta_rmse_all = qb_qw_rmse_dist(full_data,param_configs)
    all_qw,all_qb,all_rmse = [],[],[]
    rmse_dist = []
    for beta in beta_rmse_all:
        seed_rmse_dist = beta_rmse_all[beta]
        qw = [beta[1] for i in range(0,len(seed_rmse_dist))]
        qb = [beta[0] for i in range(0,len(seed_rmse_dist))]
        all_qw = all_qw + qw
        all_qb = all_qb + qb
        all_rmse = all_rmse + seed_rmse_dist
    
    data_dict = {'qw':all_qw,'qb':all_qb,'rmse_dist':all_rmse}
    dist_df = pd.DataFrame.from_dict(data_dict)
    dist_df.to_csv("../src/E0/qwqb_dist.csv")
    return dist_df

    
def generate_shift_rmse_df(full_data,param_configs):
    shifts = set(full_data["shift"])
    shift_rmse_all = shift_rmse_dist(full_data)
    all_shift,all_rmse = [],[]
    for shift in shifts:
        shift_rmse  = shift_rmse_all[shift]
        shift_val = [shift for i in range(0,len(shift_rmse))]
        all_shift = all_shift + shift_val
        all_rmse = all_rmse + shift_rmse
    
    data_dict = {'shift':all_shift,'rmse_dist':all_rmse}
    dist_df = pd.DataFrame.from_dict(data_dict)
    dist_df.to_csv("../src/E0/shift_dist.csv")
    return dist_df


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


def generate_alpha_rmse_df(full_data,param_configs):
    alphas = set(full_data["alpha"])
    alpha_rmse_all = alpha_rmse_dist(full_data)
    all_alpha,all_rmse = [],[]
    for alpha in alphas:
        alpha_rmse  = alpha_rmse_all[alpha]
        alpha_val = [alpha for i in range(0,len(alpha_rmse))]
        all_alpha = all_alpha + alpha_val
        all_rmse = all_rmse + alpha_rmse
    
    data_dict = {'alpha':all_alpha,'rmse_dist':all_rmse}
    dist_df = pd.DataFrame.from_dict(data_dict)
    dist_df.to_csv("../src/E0/shift_dist.csv")
    return dist_df

def find_best_configs(full_data,top_amount):
    # for each seed
    # find RMSE distribution
    #seed_data = full_data.query("seed == @seed_id")
    grouped_dat  = full_data.groupby(["q_w","q_b","shift","alpha","seed"])
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
    sorted_by_second = sorted(seed_configs, key=lambda tup: tup[1])
    top_ten = sorted_by_second[0:top_amount]
    return top_ten
    

def find_worst_configs(full_data,top_amount):
    # for each seed
    # find RMSE distribution
    #seed_data = full_data.query("seed == @seed_id")
    grouped_dat  = full_data.groupby(["q_w","q_b","shift","alpha","seed"])
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














