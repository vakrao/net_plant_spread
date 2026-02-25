import numpy as np
import copy
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from helpers import *
from graph_helpers import *
days = {1:31,2:28,3:31,4:30,5:31,6:30,7:31,8:31,9:30,10:31,11:30,12:31}
fig_x,fig_y = 40,20
fs = 4
hmin,hmax = 0,30



"""
description
for plotting regular heatmap, not of posterior
only for qb, qw formatting
this is for dataframes containing qb,qw  only
INPUTS 
rmse_df: dataframe, columns must be
    RMSE,q_b,q_w,....
save_fn: string specifying save folder
hmap_lab: title for heatmap
"""
def create_hmap_df(post_config,top_pct):
    # from post_config, we
    # create a dictionary called
    # combos, where the keys is
    # a tuple of (b_w,b_b) and the value
    # is a list of RMSE values
    combos = {}
    freq = {}
    for tup in post_config:
        r = tup[1]
        bet = tup[0][2]
        within = tup[0][3]
        if((bet,within)) in combos:
            combos[(bet,within)].append(r)
            freq[(bet,within)] += 1/(len(post_config))
        else:
            combos[(bet,within)] = [r]
            freq[(bet,within)] = 1/(len(post_config))

    b_b,b_w= [],[]
    freq_amount,combo_values = [],[]
    # now, take average of top RMSE values for 
    # each b_w,b_b configuration
    for c in combos:
        sort_combos = sorted(combos[c])
        last_idx = int(top_pct*len(sort_combos))
        avg_rmse = np.mean(sort_combos[0:last_idx])
        combos[c] = avg_rmse
        b_b.append(float(c[0]))
        b_w.append(float(c[1]))
        combo_values.append(avg_rmse)

        freq_amount.append(freq[c])
    # pandas boilerplate to create heatmap
    hmap_dict = {'b_b':b_b,'b_w':b_w,'rmse':combo_values}
    hmap_df = pd.DataFrame.from_dict(hmap_dict)
    hmap_df["b_b"] = hmap_df["b_b"].astype(float)
    hmap_df["b_w"] = hmap_df["b_w"].astype(float)
    # index is y, columsn are x for plotting purposes
    hmap_data = hmap_df.pivot(index="b_w", columns="b_b", values="rmse")
    hmap_data.sort_index(level=0, ascending=False, inplace=True)
    return hmap_data

def create_post_hmap_df(post_list,all_bb,all_bw):
     # from post_config, we
    # create a dictionary called
    # combos, where the keys is
    # a tuple of (b_w,b_b) and the value
    # is a list of RMSE values
    combos = {}
    freq = {}
    for b in all_bb:
        for w in all_bw:
            combos[(b,w)] = [-1]
            freq[(b,w)] = 0
    for tup in post_list:
        r = tup[1]
        bet = tup[0][2]
        within = tup[0][3]
        if(combos[(bet,within)][0] != -1):
            combos[(bet,within)].append(r)
            freq[(bet,within)] += 1/(len(post_list))
        else:
            combos[(bet,within)] = [r]
            freq[(bet,within)] = 1/(len(post_list))

    b_w,b_b= [],[]
    freq_amount = []
    combo_values = []
    # now, take average of top RMSE values for 
    # each b_w,b_b configuration
    for c in combos:
        sort_combos = sorted(combos[c])
        avg_rmse = np.mean(sort_combos)
        #avg_rmse = min(sort_combos)
        combos[c] = avg_rmse
        b_b.append(float(c[0]))
        b_w.append(float(c[1]))
        combo_values.append(avg_rmse)
        freq_amount.append(freq[c])
    # pandas boilerplate to create heatmap
    hmap_dict = {'b_b':b_b,'b_w':b_w,'rmse':combo_values}
    freq_dict = {'b_b':b_b,'b_w':b_w,'freq':freq_amount}
    hmap_df = pd.DataFrame.from_dict(hmap_dict)
    hmap_df["b_b"] = hmap_df["b_b"].astype(float)
    hmap_df["b_w"] = hmap_df["b_w"].astype(float)
    freq_df = pd.DataFrame.from_dict(freq_dict)
    freq_df["b_b"] = freq_df["b_b"].astype(float)
    freq_df["b_w"] = freq_df["b_w"].astype(float)
    hmap_df.fillna(-1)
    freq_df.fillna(-1)

    # index is y, columsn are x for plotting purposes
    hmap_data = hmap_df.pivot(index="b_w", columns="b_b", values="rmse")
    hmap_data.sort_index(level=0, ascending=False, inplace=True)
    # index is y, columsn are x for plotting purposes
    freq_data = freq_df.pivot(index="b_w", columns="b_b", values="freq")
    freq_data.sort_index(level=0, ascending=False, inplace=True)
    return hmap_data,freq_data


def post_plots(full_df,rmse_df,save_fn,inc_fp,min_pct,eps,pct):
    # first get posterior
    _,post_data = create_posterior_distribution(full_df,inc_fp,"",min_pct,eps,pct)
    # round qw by 2
    # round qb by 5
    all_bw = list(set(full_df["b_w"]))
    all_bb = list(set(full_df["b_b"]))
    all_shift = list(set(full_df["shift"]))
    all_d = list(set(full_df["D"]))
    all_bb = sorted(all_bb)
    all_bw = sorted(all_bw)
    all_shift = sorted(all_shift)
    all_d = sorted(all_d)
    count_bw,count_bb,count_shift,count_d = [],[],[],[]
    # now count instances of qw, qb 
    df_qw = post_data["b_w"].value_counts(normalize=True).rename_axis('b_w').reset_index(name="proportion")
    df_qb = post_data["b_b"].value_counts(normalize=True).rename_axis('b_b').reset_index(name="proportion")
    df_shift= post_data["shift"].value_counts(normalize=True).rename_axis('shift').reset_index(name="proportion")
    df_d= post_data["D"].value_counts(normalize=True).rename_axis('D').reset_index(name="proportion")

    df_bw = df_qw.sort_values("b_w")
    df_bb = df_qb.sort_values("b_b")
    df_shift = df_shift.sort_values("shift")
    df_d = df_d.sort_values("D")

    post_bw = list(df_qw["b_w"])
    post_bb = list(df_qb["b_b"])
    post_shift = list(df_shift["shift"])
    post_d = list(df_d["D"])
    # qw iterate
    for a in all_bw:
        if a in post_bw:
            row = df_bw.loc[df_qw["b_w"].isin([a])]            
            prop_val = list(row["proportion"])
            prop_val = float(prop_val[0])
            count_bw.append(prop_val)
        else:
            count_bw.append(0)
    # qb iterate
    post_bb = list(df_qb["b_b"])
    for a in all_bb:
        if a in post_bb:
            row = df_bb.loc[df_qb["b_b"].isin([a])]            
            prop_val = list(row["proportion"])
            prop_val = float(prop_val[0])
            count_bb.append(prop_val)
        else:
            count_bb.append(0)
    # shift iterate
    post_d= list(df_d["D"])
    for a in all_d:
        if a in post_d:
            row = df_d.loc[df_d["D"].isin([a])]            
            prop_val = list(row["proportion"])
            prop_val = float(prop_val[0])
            count_d.append(prop_val)
        else:
            count_d.append(0)
    # now, plot barplots for counts for count of posterior plots
    list_bw = [str(q) for q in all_bw]
    list_bb = [str(q) for q in all_bb]
    list_shift = [str(q) for q in all_d]
    return list_bw,count_bw,list_bb,count_bb,list_shift,count_d
    """
    fig, axes = plt.subplots(1,3)
    axes[0].bar(x=list_bw,height=count_bw)
    axes[1].bar(x=list_bb,height=count_bb)
    axes[2].bar(x=list_shift,height=count_shift)
    plt.tight_layout()
    plt.suptitle("Posterior Count")
    """
    #plt.barplot(x=all_qheighteight,y=count_qw,axs=axes[1])
#
#    fig_x = 70
#
#    sns.set(rc={'figure.figsize': (fig_x,fig_y)},font_scale=fs)
#    fig, axes = plt.subplots(1,3)
#    sns.violinplot(post_data,x="b_w",y="RMSE",ax=axes[0])
#    sns.violinplot(post_data,x="b_b",y="RMSE",ax=axes[1])
#    sns.violinplot(post_data,x="shift",y="RMSE",ax=axes[2])
#    fig.suptitle("Posterior Parameter Distribution")

"""
    Plotting function for line graph comparing incidence data 
"""
def find_best_configs(full_data,top_amount):
    # for each seed
    # find RMSE distribution
    #seed_data = full_data.query("seed == @seed_id")
    grouped_dat  = full_data.groupby(["b_w","b_b","shift","alpha","seed"])
    real_inc = pd.read_csv("../params/raw_data.csv")
    real_inc = list(real_inc["Delta Orchard"])
    seed_configs = []
    for name,group in grouped_dat:
        b_w = (float(name[0]))
        b_b = (float(name[1]))
        month_dict = {1:1,2:0,8:6,9:5,10:4,11:3,12:2}
        month_shift = month_dict[name[2]]
        new_config = f"$(\beta_b,\beta_w): ({str(b_b),str(b_w)}), L: {str(month_shift)}, s: {str(name[4])}$"
        param_cuml = list(group['monthly_cuml'])
        param_inc = calc_month_incidence(param_cuml)
        param_rmse = round(calc_rmse(real_inc,param_inc),2)
        param_config = new_config+", RMSE: "+str(param_rmse)
        all_tup = ((param_config,param_inc,name[4]),param_rmse)
        seed_configs.append(all_tup)
    sorted_by_second = sorted(seed_configs, key=lambda tup: tup[1])
    unq_seeds = 0
    count = 0
    seed_ids = set()
    top_ten = []
    while(unq_seeds < top_amount):
        seed_val = sorted_by_second[count][0][2]
        seed_ids.add(seed_val)
        if len(seed_ids) > unq_seeds: 
            unq_seeds += 1
            top_ten.append(sorted_by_second[count])
        count += 1
    return top_ten

def find_line_data(full_data,inc_fp,post_fp,top_percent):
    config_list,post_df = create_posterior_distribution(full_data,inc_fp,post_fp,top_percent)
    grouped_dat = post_df.groupby(["b_w","b_b","shift","alpha","seed"])

    all_line = []
    avg_rmse = 0
    counter = 0
    for name,group in grouped_dat: 
        b_w = (float(name[0]))
        b_b = (float(name[1]))  
        L = (float(name[2]))    
        alpha = (float(name[3]))
        seed = (float(name[4]))
        line_df = full_data.query("b_w == @b_w and b_b == @b_b and shift == @L and alpha == @alpha and seed == @seed")
        line_df = line_df.reset_index(drop=True)
        line_dat = list(line_df["monthly_cuml"])
        line_rmse = float(group["RMSE"].iloc[0])
        avg_rmse += line_rmse
        counter += 1
        line_combo = (line_dat,line_rmse)
        all_line.append(line_dat)
    num_rows = np.shape(all_line)[0]
    avg_rmse = avg_rmse/counter
    return all_line,avg_rmse


        



