import os
import sys
import pandas as pd
#import polars as pl
import seaborn as sns
import matplotlib.pyplot as plt
# Build an absolute path from this notebook's parent directory
module_path = os.path.abspath(os.path.join('..', 'src'))
print(module_path)
# Add to sys.path if not already present
if module_path not in sys.path:
    sys.path.append(module_path)
print(module_path)
# Now you can import the desired function or class
from clean_df import *
from graph_helpers import *
from helpers import *
from mod_si import *
from plots import *
from find_net_stats import *

def local_write(write_list):
    b_w,b_b= write_list['b_w'],write_list['b_b']
    i,t,h = write_list['clean_i'],write_list['clean_t'],write_list['clean_h']
    seed_id = write_list['seed']
    d = write_list['D']
    alpha = write_list['alpha']
    P = write_list["P"]
    shift = write_list['shift']
    write_folder= write_list['write_folder']
    file_specs = str(b_w)+"_"+str(b_b)+"_"+str(shift)+"_"+str(d)+"_"+str(alpha)+"_"+str(seed_id)
    write_file = write_folder + file_specs+".csv"
    # create lists same size as i
    list_bw = [b_w for _ in i]
    list_bb = [b_b for _ in i]
    list_seed = [seed_id for _ in i]
    list_alpha= [alpha for _ in i]
    list_shift = [shift for _ in i]
    list_D = [d for _ in i]
    list_P = [P for _ in i]
    write_dict = {'b_w':list_bw,'b_b':list_bb,'monthly_cuml':i,'monthly_h':h,'months':t,'seed':list_seed,'alpha':list_alpha,'shift':list_shift,"D":list_D,"P":list_P}
    write_df = pd.DataFrame.from_dict(write_dict)
    write_df.to_csv(write_file,mode='w',header=True)

def si_worker(inputs):
    # ALL PARAMETER VALUES HERE
    b_w,b_b = inputs['b_w'],inputs['b_b']
    in_bond,out_bond= inputs['in_bond'],inputs['out_bond']
    prop_size = inputs['prop_size']
    d,T = inputs['D'],inputs['T']
    real_infec,seed = inputs['real_infec'],inputs['seed']
    P = inputs['P']
    max_infected =inputs['max_infected']
    max_infected = 3000
    alpha= inputs['alpha']
    write_folder = inputs['write_folder']
    shifts = inputs['shift_val']
    net_file = inputs['net_file']
    deltaT = inputs['deltaT']
    # number of days associated with each 'shift month'
    # 1 = number of days in jan, 2 is number of days in december etc
    increase_amount = {1:31,0:0,6:31,5:30,4:31,3:30,2:31}
    t_m = 14
    add_amount = 0
    if shifts > 0:
        t_m = t_m + shifts
        for s in range(1,shifts+1):
            add_amount += increase_amount[s]
    T += add_amount
    # running model
    min_inc = 1
    month_convert = {0:2,1:1,2:12,3:11,4:10,5:9,6:8}
    cal_month = month_convert[shifts]
    all_t,h,i = run_si_model(in_bond, out_bond,net_file, prop_size, b_b, b_w, d, seed, T, max_infected,deltaT,min_inc,alpha,P,cal_month)
    p_i = prune_i(i,all_t,T)
    p_h = prune_i(h,all_t,T)
    s_list = {}
    #now, get monthly data 
    if len(i) != 0:
        clean_i,clean_t = clean_temp_shift(p_i,t_m,cal_month,shifts)
        clean_h,_ = clean_temp_shift(p_h,t_m,cal_month,shifts)
        s_list = {'b_w': b_w,
                  'b_b': b_b,
                  'clean_i':clean_i,
                  'clean_t':clean_t,
                  'clean_h':clean_h,
                  'seed':seed,
                  'alpha':alpha,
                  'D':d,
                  'P':P,
                  'write_folder':write_folder,
                  'shift':shifts}

    local_write(s_list)
    return s_list


net_file = "../params/horticulture365.csv"
prop_size = read_property_data("../params/prop_dat.csv")
inc_fp  = "../params/new_psa.csv"
post_fp = "sent_post.csv"
in_bond,out_bond = read_network_data(net_file)

# now, filter for best fits 
# month best fit: (.04,.1,33297)
# seas best fit: (.03,.08,21709)
# year best fit: (.08,.04,21906)
m_bb,m_bw,m_s = .04,.1,["33297" ]
s_bb,s_bw,s_s = .03,.08,["21709"]
y_bb,y_bw,y_s = .08,.04,["21906"]
D,T,alpha,F,max_infected = 0.2,425,0.1,625,3000
D_list = [0.05,0.1,.2,0.4,0.8]
min_inc = 1
cal_month = 2
t_m = 14
m_D,s_D,y_D = {},{},{}
for D in D_list:
    m_t,m_h,m_i = run_si_model (in_bond, out_bond,net_file, prop_size, m_bb, m_bw, D, m_s, T, max_infected,1,min_inc,alpha,F,init_month=2)
    s_t,s_h,s_i = run_si_model (in_bond, out_bond,net_file, prop_size, s_bb, s_bw, D, s_s, T, max_infected,3,min_inc,alpha,F,init_month=2)
    y_t,y_h,y_i = run_si_model (in_bond, out_bond,net_file, prop_size, y_bb, y_bw, D, y_s, T, max_infected,12,min_inc,alpha,F,init_month=2)
    m_clean = clean_temp_shift(m_i,t_m,cal_month,0)
    s_clean = clean_temp_shift(s_i,t_s,cal_month,0)
    y_clean = clean_temp_shift(y_i,t_y,cal_month,0)



        

"""
    Runner script requires 1 command line inputs
        yaml_file: "plant_run.yaml"
"""
if __name__ == '__main__':
    if len(sys.argv) < 2: 
        print("not enough arguments!")
        sys.exit()
    yaml_path = sys.argv[1]
    # Load YAML configuration
    with open(yaml_path, "r") as file:
        config = yaml.safe_load(file)
    params = config["params"]
    # read all the parameter values
    net_file = params.get("net_file")
    max_infected = params.get("max_infected")
    b_within = params.get("b_w")
    b_within = [float(q) for q in b_within]
    b_between = params.get("b_b")
    b_between = [float(q) for q in b_between]
    alphas = params.get("alpha")
    alphas = [float(q) for q in alphas]
    all_D = params.get("D")
    all_D = [float(q) for q in all_D]
    T = params.get("T")
    param_deltaT  = params.get("deltaT")
    if isinstance(param_deltaT,list):
        all_deltaT = [int(t) for t in param_deltaT]
    else:
        all_deltaT = [param_deltaT]
    P = params.get("P")
    L  = params.get("L")
    write_folder = params.get("save_folder")
    run_type = params.get("run_type")
    L = [int(q) for q in L]
    P = [int(q) for q in P]
    prop_fn = params.get("prop_fn")
    in_bond, out_bond = read_network_data(net_file)
    pool_amount = params.get("pool_amount")
    prop_size = read_property_data("../params/prop_dat.csv")
    inc_fp = params.get("inc_file")
    real_inc = pd.read_csv(inc_fp)
    save_fn = "hort_seeds.csv"
    seed_amount = 2412
    if run_type == "calib":
        seeds = find_conn_comp_calib_seeds(net_file,seed_amount,in_bond,out_bond,save_fn)
    else:
        seeds = find_real_seeds(net_file,seed_amount,in_bond,out_bond,save_fn)
    real_inc = list(real_inc["Delta Orchard"])
    manager = mp.Manager()
    pool = mp.Pool(pool_amount)
    all_params = []
    for deltaT in all_deltaT:
        for p_val in P:
            for d_val in all_D:
                for shift_val in L:
                    for alpha in alphas:
                        for b_b in b_between:
                            for b_w in b_within:
                                for s in seeds:
                                    params = {  'b_w':b_w,
                                                'b_b':b_b,
                                                'in_bond':in_bond,
                                                'out_bond':out_bond,
                                                'prop_size':prop_size,
                                                'D':d_val,
                                                'P':p_val,
                                                'T':T,
                                                'seed':s,
                                                'deltaT':deltaT,
                                                'real_infec':real_inc,
                                                'max_infected':max_infected,
                                                'alpha':alpha,
                                                'shift_val':shift_val,
                                                'write_folder':write_folder,
                                                'net_file':net_file
                                            }
                                    all_params.append(params)
    print("number of possible jobs: ",len(all_params))
    results = []
    jobs = []
    for p in all_params:
        job = pool.apply_async(si_worker,(p,))
        jobs.append(job)
    for job in tqdm(jobs):
        j = job.get()
    pool.close()
    pool.join()
