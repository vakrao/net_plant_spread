import numpy as np
import copy
import pandas as pd
from gen_heatmap import *

days = {1:31,2:28,3:31,4:30,5:31,6:30,7:31,8:31,9:30,10:31,11:30,12:31}



def create_D_distribution(full_data,inc_fp,top_percent=1):
    
    real_inc = pd.read_csv(inc_fp)
    D = set(full_data["D"])
    real_inc = pd.read_csv(inc_fp)
    real_inc = list(real_inc["Delta Orchard"])
    all_out,all_rmse,all_d,all_seed,all_shift,all_alpha = [],[],[],[],[],[]
    all_configs = []
    for d_val in D:
        filt_dat = full_data.query("D == @d_val")
        grouped_seed  = filt_dat.groupby(["q_b","q_w","seed","shift","alpha"])
        for name,group in grouped_seed:
            seed_val,shift_val,alpha_val = name[2],name[3],name[4]
            param_cuml = list(group['monthly_cuml'])
            param_inc = calc_month_incidence(param_cuml)
            param_rmse = calc_rmse(param_inc,real_inc)
            param_outbreak = param_cuml[-1]
            all_configs.append(((param_outbreak,param_rmse,seed_val,shift_val,alpha_val,d_val),param_rmse))
                
    sort_config = sorted(all_configs,key=lambda x: x[1])
    min_amount = int(top_percent*len(all_configs))
    sort_config = sort_config[0:min_amount]
    # now save the sort_config:
    for (s,r) in sort_config:
        all_out.append(s[0])
        all_rmse.append(s[1])
        all_seed.append(s[2])
        all_shift.append(s[3])
        all_alpha.append(s[4])
        all_d.append(s[5])
    post_dict = {"Outbreak Size": all_out,"RMSE":all_rmse,"D":all_d,"seed":all_seed,"shift":all_shift,"alpha":all_alpha}
    post_df = pd.DataFrame.from_dict(post_dict)

    return sort_config,post_df
