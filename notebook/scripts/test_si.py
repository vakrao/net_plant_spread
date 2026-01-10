import csv
from tqdm import tqdm
import random
import copy
import numpy as np
from decimal import Decimal
import math
import unittest
days = {1:31,2:28,3:31,4:30,5:31,6:30,7:31,8:31,9:30,10:31,11:30,12:31}

def read_network_data (filename):
    in_bond = {}
    out_bond = {}
    with open(filename, newline='') as csvfile:
        rows = csv.reader(csvfile, delimiter=',')
        first_row = 0
        for row in rows:
            if first_row > 0:
                s = int(row[1])
                d = int(row[2])
                w = row[3]
                if s == '0':
                    print("zero source value")
                if d == "0":
                    print("zero dest value")
                ##
                if d not in in_bond:
                    in_bond[d] = {}
                if s not in in_bond[d]:
                    in_bond[d][s] = float(0)
                in_bond[d][s] += float(w)
                if s not in out_bond:
                    out_bond[s] = {d:0}
                if d not in out_bond[s]:
                    out_bond[s][d] = float(0)
                out_bond[s][d] += float(w)
            
                ##
            first_row = 1

    return in_bond, out_bond


#def read_network_data(filename):
#    in_bond = {}
#    out_bond = {}
#    print("Reading file:", filename)
#    with open(filename, newline='') as csvfile:
#        rows = csv.reader(csvfile, delimiter=',')
#        next(rows)  # Skip header
#        for row in rows:
#            try:
#                s = int(row[1].strip())
#                d = int(row[2].strip())
#                w = float(row[3].strip())
#            except Exception as e:
#                print("Row parse error:", row, e)
#                continue
#
#            if s == 0:
#                print("zero source value")
#            if d == 0:
#                print("zero dest value")
#
#            if d not in in_bond:
#                in_bond[d] = {}
#            if s not in in_bond[d]:
#                in_bond[d][s] = 0.0
#            in_bond[d][s] += w
#
#            if s not in out_bond:
#                out_bond[s] = {}
#            if d not in out_bond[s]:
#                out_bond[s][d] = 0.0
#            out_bond[s][d] += w
#
#
#    print("Finished reading.")
#    
#    return in_bond, out_bond




#####
def read_property_data (filename):

    prop_size = {}
    with open(filename, newline='') as csvfile:
        rows = csv.reader(csvfile, delimiter=',')
        first_row = 0
        for row in rows:
            if first_row > 0:
                i = int(row[0])
                s = (1.0)
                if len(row[3])>0:
                    s = float(row[3])
                prop_size[i] = float(s)
            first_row = 1

    return prop_size



########

### tau = 365 
### (each week to give some number of infections) 
### 


"""
   Find time increment dt for each node n
    PARAMETERS
    min_value: float of minimum time increment
    state: dictionary of level of infections of nodes N
    in_bond: dictionary of dictionaries
"""
def determine_time_increment (min_value,state, in_bond, beta_bet, beta_wit,tau=365):

    min_inc = min_value
    for n in state:
        if state[n] < 1.0 and n in in_bond:
            tmp = (0)
            for m in in_bond[n]:
                
                #print("outgoing id: ",m)
                #print("run amount: ",in_bond[n][m])
                #print(out_bond['29676'])
                init_mult =(in_bond[n][m]/tau) * state[m] 
                tmp += init_mult
            sus = (1.0-state[n]) 
            tmp = tmp * beta_bet * sus
            tmp = tmp + (beta_wit * state[n]*sus)
            if tmp > 0:
                frac = sus / tmp
                if min_inc > frac:
                    min_inc = frac
    return min_inc


#####


"""
   Find new level of infection I_n for each node n 
   PARAMTERS
    old_state: dictionary of level of infections of nodes N
    in_bond: dictionary of dictionaries
        key: String node id n
        values: dictionary of incoming nodes K to node n, with weights of movements m for each node k 
    prop_size: dictionary of property sizes
    F: number of plants per hectare
    beta_bet: float of b_b param
    beta_wit: float of b_w param
    dt: float of time increment
"""
def compute_variation (old_state, in_bond,prop_size, beta_bet, beta_wit, dt,F,tau=365):
    new_state = {}
    
    for n in old_state:
        if old_state[n] < 1.0:
            bet_pct = (0)
            all_cont = (0)
            if n in in_bond:
                for m in in_bond[n]:
                    if m != n and old_state[m] > 0.0:
                        a_ij = (in_bond[n][m])
                        cont_val = (a_ij * (old_state[m]))/(tau*1.0)
                        all_cont += cont_val
            sus = (1.0 - old_state[n])
            bet_pct = all_cont*(beta_bet)*sus
            min_infec = (1/(F*prop_size[n]))
            # minimum amount to infect one plant
            if bet_pct < min_infec:
                bet_pct = 0
            wit_pct = (beta_wit) * (old_state[n])*sus
            total = float(wit_pct + bet_pct)
            new_val = float((old_state[n]) + (total * dt))
            # check if infection exceeds minimum infection
            # threshold for individaul farm
            new_state[n] = min(1.0,max(0,new_val))
        else:
            new_state[n] = float(1.0)

    return new_state



def compute_infected_hectares (state, prop_size, D):

    infected_hectares = 0.0
    infected_farms = 0
    for n in state:
        if state[n] > 0.0:
            infected_hectares += state[n] * prop_size[n]
        if state[n]  > D:
            infected_farms += 1.0

    return infected_hectares, infected_farms



"""
reference for months associated with seasons
    # for seasonal variation
    sum_monts = ["12","01","02"]
    aut_months = ["03","04","05"]
    wint_months = ["06","07","08"]
    spring_months = ["09","10","11"]
"""
"""
    deltaT = 1 or 3 or 12
    init_seed = amount to initialize seed at start
"""
def run_test_si_model (in_bond, out_bond,net_file, prop_size, b_b, b_w, D, seeds, T, max_infected,deltaT,min_inc,alpha,F,init_month=2):

    s_name = ["SM","AT","SP","WT"]
    days = {1:31,2:28,3:31,4:30,5:31,6:30,7:31,8:31,9:30,10:31,11:30,12:31}
    season = {1:"SM",2:"SM",
            3:"AT",4:"AT",5:"AT",
            6:"WT",7:"WT",8:"WT",
            9:"SP",10:"SP",11:"SP",
            12:"SM"}
    sum_duration = days[12]+days[1]+days[2]
    at_duration = days[4]+days[5]+days[6]
    wt_duration = days[7]+days[8]+days[9]
    sp_duration = days[10]+days[11]+days[12]
    season_dur = {'SM':sum_duration,'WT':wt_duration,"SP":sp_duration,"AT":at_duration}
    start_season = season[init_month]
    ##initialize state based on all properties 
    state = {}
    x, y, z = [], [], []
    month_counter = 0 
    day_counter = 1
    curr_month = init_month
    curr_month_amount = days[init_month]
    file_ending = "_2022.csv"
    tau = deltaT*30
    # choose network based on tau setting
    if deltaT == 1:
        folder = "../params/new_month_tau/"
        if curr_month < 10:
            tau_string = "0"+str(curr_month)
        else: 
            tau_string = str(curr_month)
    if deltaT == 3:
        folder = "../params/new_season_tau/"
        tau_string = season[curr_month]
    if deltaT == 12:
        folder = "../params/"
        tau_string = net_file
        file_ending = ""
        tau = 365

    if isinstance(seeds,list) == False:
        seeds = [seeds]
    ##state must be initialized from full network
    for n in in_bond:
        state[n] = float(0.0)
    #print(out_bond['29676'])
    for n in out_bond:
        if n == "29676":
            print("put in state")
        state[n]  = float(0.0)
    ##initial conditions
    for n in seeds:
        state[n] = float(alpha)
    tau_init_file = f"{folder}{tau_string}{file_ending}"
#    in_bond,out_bond = {},{}
    #initial network based on first tau month
    in_bond, out_bond = read_network_data(tau_init_file)
    t = 0.0

    infected_hectares, infected_farms = compute_infected_hectares(state, prop_size, D)

    b_b = float(b_b)
    b_w = float(b_w)
    tau = float(tau)
    # minimum time increment for the model
    min_value = min_inc
    day_counter = 0
    test_season = []
    test_month = []
    while (t) < T and infected_farms < max_infected:
        curr_season =  season[curr_month]
        test_month.append(curr_month)
        test_season.append(curr_season)
        old_state = copy.deepcopy(state)
        dt = determine_time_increment (min_value,old_state, in_bond, b_b, b_w,tau)
        t += dt
        day_counter += dt
        new_state= compute_variation (old_state, in_bond,prop_size, b_b, b_w, dt,F,tau)
        infected_hectares, infected_farms = compute_infected_hectares (new_state, prop_size, D)
        state = copy.deepcopy(new_state)
        new_state = {}
        if day_counter == curr_month_amount and deltaT >= 1:
            assert(day_counter == days[curr_month])
            month_counter += 1
            day_counter = 0
            # updating network 
            update_file = f"{tau_string}{file_ending}"
            update_file = folder+update_file
            # potential for network to change every month
            # depending on deltaT
            if month_counter == 1 and deltaT != 12:
                next_month = curr_month + 1
                update_file = ""
                # delta == 1 is monthly aggregation
                if deltaT == 1:
                    # check if we exceed 12 months
                    if next_month == 13:
                        next_month = 1
                    tau_string = str(next_month)
                    if next_month < 10:
                        tau_string = "0"+tau_string
                    update_file = f"{tau_string}{file_ending}"
                    update_file = folder+update_file

                    # change how many days in month
                    curr_month_amount = days[next_month]
                    curr_month = next_month
                    # updating in,out bound dicts
                    in_bond,out_bond = {},{}
                    new_in,new_out = read_network_data(update_file)
                    in_bond = new_in
                    out_bond = new_out
                # deltaT == 3 is seasonal
                if deltaT == 3:
                    if next_month  == 13:
                        next_season = season[1]
                        curr_season = season[12]
                        next_month = 1
                    else:
                        curr_season = season[curr_month]
                        next_season = season[next_month]
                    if curr_season != next_season:
                        tau_string = next_season
                        update_file = f"{tau_string}{file_ending}"
                        update_file = folder+update_file
                        # updating in,out bound dicts
                        new_in,new_out = read_network_data(update_file)
                        in_bond = new_in
                        out_bond = new_out
                    curr_month_amount = days[next_month]
                    curr_month = next_month
                month_counter =0 
                # avoiding exceeding 12 months
        

        x.append(t)
        y.append(infected_hectares)
        z.append(infected_farms)

    if len(x) != T:
        diff_amount = T - len(x)
        last_x = x[-1]
        last_y = y[-1]
        last_z = z[-1]
        for i in range(0,diff_amount):
            x.append(last_x)
            y.append(last_y)
            z.append(last_z)

    return x, y, z,test_season,test_month

# need to write test checking season swapping 
if __name__=="__main__":
    net_file = "../params/horticulture365_check_NZ.csv"
    prop_file = "../params/2024_prop_dat.csv"
    in_bond,out_bond = read_network_data(net_file)
    prop_size = read_property_data(prop_file)
    b_b,b_w = 0.1,0.01
    D = 0.2
    T = 425
    max_infected = 2400
    deltaT = 3
    min_inc = 1
    alpha = 0.1
    F = 625
    all_in_seeds = list(in_bond.keys())
    seeds = random.sample(all_in_seeds,1)
    # check seasonal switching
    _,_,_,s,_ = run_test_si_model(in_bond, out_bond,net_file, prop_size, b_b, b_w, D, seeds, T, max_infected,deltaT,min_inc,alpha,F,init_month=2)
    # check monthly switching
    print("finished running season")
    deltaT = 1
    _,_,_,_,m = run_test_si_model(in_bond, out_bond,net_file, prop_size, b_b, b_w, D, seeds, T, max_infected,deltaT,min_inc,alpha,F,init_month=2)
    # create check vaalues for s and m
    start_m = 2
    check_m,check_s = [],[]
    month = start_m
    day_move = days[month]
    counter = 0
    season = {1:"SM",2:"SM",
            3:"AT",4:"AT",5:"AT",
            6:"WT",7:"WT",8:"WT",
            9:"SP",10:"SP",11:"SP",
            12:"SM"}
    for i in range(0,len(s)): 
        if counter == day_move:
            month += 1 
            if month > 12:
                month = 1
            day_move = days[month]
            counter = 0
        check_m.append(month)
        check_s.append(season[month])
        counter += 1
    assert(s == check_s)
    assert(m == check_m)
    print("test complete! Seasonal, monthly switching aligned")

        
        

