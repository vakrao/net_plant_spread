import pandas as pd
import multiprocessing as mp
import sys
import yaml
from tqdm import tqdm
from mod_si import *
from helpers import *
from find_seeds import *
from decimal import *
from concurrent.futures import ProcessPoolExecutor, as_completed


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
    shifts = 0
    # varying start-month
    sm = inputs['sm']
    net_file = inputs['net_file']
    deltaT = inputs['deltaT']
    # number of days associated with each 'shift month'
    # 1 = number of days in jan, 2 is number of days in december etc
    t_m = 14
    T = 435
    add_amount = 0
    # running model
    min_inc = 1
    all_t,h,i = run_si_model(in_bond, out_bond,net_file, prop_size, b_b, b_w, d, seed, T, max_infected,deltaT,min_inc,alpha,P,sm)
    p_i = prune_i(i,all_t,T)
    p_h = prune_i(h,all_t,T)
    s_list = {}
    #now, get monthly data 
    if len(i) != 0:
        clean_i,clean_t = clean_temp_shift(p_i,t_m,sm,shifts)
        clean_h,_ = clean_temp_shift(p_h,t_m,sm,shifts)
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
                  'sm':sm}

    local_write(s_list)
    return s_list

        
def local_write(write_list):
    b_w,b_b= write_list['b_w'],write_list['b_b']
    i,t,h = write_list['clean_i'],write_list['clean_t'],write_list['clean_h']
    seed_id = write_list['seed']
    d = write_list['D']
    alpha = write_list['alpha']
    P = write_list["P"]
    sm = write_list['sm']
    write_folder= write_list['write_folder']
    file_specs = str(b_w)+"_"+str(b_b)+"_"+str(sm)+"_"+str(d)+"_"+str(alpha)+"_"+str(seed_id)
    write_file = write_folder + file_specs+".csv"
    # create lists same size as i
    list_bw = [b_w for _ in i]
    list_bb = [b_b for _ in i]
    list_seed = [seed_id for _ in i]
    list_alpha= [alpha for _ in i]
    list_sm = [sm for _ in i]
    list_D = [d for _ in i]
    list_P = [P for _ in i]
    write_dict = {'b_w':list_bw,'b_b':list_bb,'monthly_cuml':i,'monthly_h':h,'months':t,'seed':list_seed,'alpha':list_alpha,'sm':list_sm,"D":list_D,"P":list_P}
    write_df = pd.DataFrame.from_dict(write_dict)
    write_df.to_csv(write_file,mode='w',header=True)

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
    sm = params.get("sm")
    all_sm = [int(q) for q in sm]
    if isinstance(param_deltaT,list):
        all_deltaT = [int(t) for t in param_deltaT]
    else:
        all_deltaT = [param_deltaT]
    P = params.get("P")
    L  = params.get("L")
    write_folder = params.get("save_folder")
    run_type = params.get("run_type")
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
        if run_type == "spec":
            seeds = params.get("seed")
        else:
            seeds = find_real_seeds(net_file,seed_amount,in_bond,out_bond,save_fn)
    real_inc = list(real_inc["Delta Orchard"])
    manager = mp.Manager()
    pool = mp.Pool(pool_amount)
    all_params = []
    for deltaT in all_deltaT:
        for p_val in P:
            for d_val in all_D:
                for sm_val in all_sm:
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
                                                'sm':sm_val,
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
