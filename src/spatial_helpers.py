import pandas as pd
import numpy as np
import copy
from gen_heatmap import *
from geopy.distance import geodesic

def calc_neigh_monthly_spread(infec_dict,in_bond,prop_fp,graph_type,s):
    prop_dat = pd.read_csv(prop_fp)
    proper_loc = dict(zip(prop_dat["PROPERTY_ID"], zip(
        prop_dat["GPS_CENTRE_LONGITUDE"],  # lat
        prop_dat["GPS_CENTRE_LATITUDE"]    # lon
    )))
    seed_loc = proper_loc[s]
    prev_infected = {}
    days = {1:31,2:28,3:31,4:30,5:31,6:30,7:31,8:31,9:30,10:31,11:30,12:31}
    month_nodes = {}
    cal_count = 2
    day_count = 0
    full_time = 0 
    # get all associated nodes with a time
    for node in infec_dict:
        infec_time = infec_dict[node]
        if infec_time > full_time:
            full_time = infec_time
        if infec_time not in prev_infected:
            prev_infected[infec_time]= [node]
        else:
            prev_infected[infec_time].append(node)
    month_count = 1
    # associate days with the month increme
    for i in range(1,int(full_time)+1):
        month_nodes[i] = month_count
        day_count += 1
        if day_count > days[cal_count]:
            day_count = 0
            month_count += 1
            if cal_count == 12:
                cal_count = 0
            cal_count += 1
    month_infec = {}
    cal_count = 1
    # now, do month_infected
    for t in prev_infected:
        infec_nodes = prev_infected[t]
        # find the month associated with time t
        t_month = month_nodes[t]
        # now, assign infected node to a specific month
        if t_month not in month_infec:
            month_infec[t_month] = infec_nodes
        else:
            month_infec[t_month].extend(infec_nodes)
    all_vals = [0 for _ in range(0,17)]
    neigh_dists = []
    for m in month_infec:
        monthly_infec_props = month_infec[m]
        for i in range(0,len(monthly_infec_props)):
            node_a = monthly_infec_props[i]
            neigh_a = list(in_bond[node_a].keys())
            node_a_infec_time = infec_dict[node_a]
            # go through a nodes neighbors
            # check which ones have been previously
            # infected 
            sum_dist = 0
            neigh_infected = 0
            for j in neigh_a:
                if j in infec_dict:
                    neigh_a_infec_time = infec_dict[j]
                    if m == 2:  
                        print(neigh_a_infec_time,node_a_infec_time)
                    if neigh_a_infec_time < node_a_infec_time:
                        trans_dist = geodesic(proper_loc[int(node_a)],proper_loc[int(j)]).km
                        if trans_dist == 0:
                            print("node a: ",node_a)
                            print("neigh a: ",neigh_a)
                            print("node a: ",(proper_loc[int(node_a)]," , neigh: ",proper_loc[int(j)]).km)
                        sum_dist += trans_dist
                        neigh_infected += 1
            neigh_infec = sum_dist/neigh_infected if neigh_infected > 0 else None 
            if neigh_infec == 0:
                print("key-node: ",node_a)
                print("neigh nodes: ",neigh_a)
            if neigh_infec != None:
                neigh_dists.append(neigh_infec)
            if m == 4:  
                print(neigh_a_infec_time,node_a_infec_time)
        if graph_type == "max": 
            value = max(neigh_dists) if len(neigh_dists) > 0 else -1
        if graph_type == "min":
            value = min(neigh_dists) if len(neigh_dists) > 0 else -1
        if graph_type == "avg":
            value = np.mean(neigh_dists) if len(neigh_dists) > 0 else 0
        all_vals[m-1] = value
        neigh_dists = []
            
    return all_vals

def calc_monthly_spread(infec_dict,prop_fp,graph_type,s):
    prop_dat = pd.read_csv(prop_fp)
    proper_loc = dict(zip(prop_dat["PROPERTY_ID"], zip(
        prop_dat["GPS_CENTRE_LONGITUDE"],  # lat
        prop_dat["GPS_CENTRE_LATITUDE"]    # lon
    )))
    seed_loc = proper_loc[s]
    all_dist = []
    prev_infected = {}
    days = {1:31,2:28,3:31,4:30,5:31,6:30,7:31,8:31,9:30,10:31,11:30,12:31}
    month_nodes = {}
    cal_count = 2
    day_count = 0
    full_time = 0 
    # get all associated nodes with a time
    for node in infec_dict:
        infec_time = infec_dict[node]
        if infec_time > full_time:
            full_time = infec_time
        if infec_time not in prev_infected:
            prev_infected[infec_time]= [node]
        else:
            prev_infected[infec_time].append(node)
    month_count = 1
    # associate days with the month increme
    for i in range(1,int(full_time)+1):
        month_nodes[i] = month_count
        day_count += 1
        if day_count > days[cal_count]:
            day_count = 0
            month_count += 1
            if cal_count == 12:
                cal_count = 0
                
            cal_count += 1
    month_infec = {}
    cal_count = 1
    # now, do month_infected
    for t in prev_infected:
        curr_infec_nodes = prev_infected[t]
        t_month = month_nodes[t]
        if t_month not in month_infec:
            month_infec[t_month] = curr_infec_nodes
        else:
            month_infec[t_month].extend(curr_infec_nodes)
    all_diff = 0
    all_max= [0 for _ in range(0,17)]

    for m in month_infec:
        month_infec_nodes = month_infec[m]
        if graph_type == "max":
            dist = 0
        if graph_type == "min":
            dist = 100000
        
        all_combs = 0
        all_diff = 0
        for i in range(0,len(month_infec_nodes)):
            seed_id = int(month_infec_nodes[i])
            seed_prop_loc = proper_loc[int(seed_id)]
            for j in range(i,len(month_infec_nodes)):
                new_id = int(month_infec_nodes[j])
                if seed_id != new_id:
                    new_loc = proper_loc[int(new_id)]
                    trans_dist = geodesic(seed_prop_loc,new_loc).km
                    all_diff += trans_dist
                    all_combs += 1
                    if graph_type == "max" and trans_dist > dist:
                        dist = trans_dist
                    if graph_type == "min" and trans_dist < dist:
                        dist = trans_dist
        if graph_type == "avg":
            if all_combs > 0:
                all_max[m-1] = all_diff/all_combs 
            else:
                all_max[m-1] = 0
        if graph_type != "avg": 
            if dist == 100000:
                dist = 0
            all_max[m-1] = dist
    return all_max

def calc_largest_diameter(infec_dict,prop_fp,s):
    prop_dat = pd.read_csv(prop_fp)
    proper_loc = dict(zip(prop_dat["PROPERTY_ID"], zip(
        prop_dat["GPS_CENTRE_LONGITUDE"],  # lat
        prop_dat["GPS_CENTRE_LATITUDE"]    # lon
    )))
    seed_loc = proper_loc[s]
    all_dist = []
    prev_infected = {}
    days = {1:31,2:28,3:31,4:30,5:31,6:30,7:31,8:31,9:30,10:31,11:30,12:31}
    month_nodes = {}
    cal_count = 1
    day_count = 0
    full_time = 0 
    # get all associated nodes with a time
    for node in infec_dict:
        infec_time = infec_dict[node]
        full_time = infec_time
        if infec_time not in prev_infected:
            prev_infected[infec_time]= [node]
        else:
            prev_infected[infec_time].append(node)
    month_count = 1
    # associate days with the month increme
    for i in range(1,int(full_time)+1):
        month_nodes[i] = month_count
        day_count += 1
        if day_count > days[cal_count]:
            day_count = 0
            month_count += 1
            if cal_count == 12:
                cal_count = 0
                
            cal_count += 1
    month_infec = {}
    cal_count = 1
    # now, do month_infected
    for t in prev_infected:
        
        infec_nodes = prev_infected[t]
        t_month = month_nodes[t]
        if t_month not in month_infec:
            month_infec[t_month] = infec_nodes
        else:
            month_infec[t_month].extend(infec_nodes)
    all_diff = 0
    all_avg = {}
    all_max= [0 for _ in range(0,17)]
    dist = 0
    # now, do month_infected
    for m in month_infec:
        infec_nodes = month_infec[m]
        all_avg[m] = 0
        all_diff = 0
        for i in range(0,len(infec_nodes)):
            seed_id = int(infec_nodes[i])
            seed_prop_loc = proper_loc[int(seed_id)]
            for j in range(i,len(infec_nodes)):
                if i != j:
                    new_id = int(infec_nodes[j])
                    new_loc = proper_loc[int(new_id)]
                    trans_dist = geodesic(seed_prop_loc,new_loc).km
                    all_diff += trans_dist
                    if trans_dist > dist:
                        dist = trans_dist
        all_max[m-1] = dist
    return all_max

    """
def calc_monthly_spread(infec_dict,s):
    prop_dat = pd.read_csv(prop_fp)
    proper_loc = dict(zip(prop_dat["PROPERTY_ID"], zip(
        prop_dat["GPS_CENTRE_LONGITUDE"],  # lat
        prop_dat["GPS_CENTRE_LATITUDE"]    # lon
    )))
    country = dict(zip(prop_dat["PROPERTY_ID"],prop_dat["COUNTRY"]))
    seed_loc = proper_loc[s]
    all_dist = []
    prev_infected = {}
    days = {1:31,2:28,3:31,4:30,5:31,6:30,7:31,8:31,9:30,10:31,11:30,12:31}
    start_month = 2
    month_nodes = {}
    cal_count = 1
    day_count = 0
    full_time = 0 
    # get all associated nodes with a time
    for node in infec_dict:
        infec_time = infec_dict[node]
        full_time = infec_time
        if infec_time not in prev_infected:
            prev_infected[infec_time]= [node]
        else:
            prev_infected[infec_time].append(node)
    month_count = 1
    # associate days with the month increme
    for i in range(1,int(full_time)+1):
        month_nodes[i] = month_count
        day_count += 1
        if day_count > days[cal_count]:
            day_count = 0
            month_count += 1
            if cal_count == 12:
                cal_count = 0
                
            cal_count += 1
    month_infec = {}
    cal_count = 1
    # now, do month_infected
    for t in prev_infected:
        
        infec_nodes = prev_infected[t]
        t_month = month_nodes[t]
        if t_month not in month_infec:
            month_infec[t_month] = infec_nodes
        else:
            month_infec[t_month].extend(infec_nodes)
    all_max = []
    all_diff = 0
    all_avg = {}
    all_max= [0 for i in range(0,17)]
    for m in month_infec:
        infec_nodes = month_infec[m]
        
        close_loc = 0
        max_dist = 0
        all_avg[m] = 0
        all_combs = 0
        all_diff = 0
        for i in range(0,len(infec_nodes)):
            seed_id = int(infec_nodes[i])
            seed_prop_loc = proper_loc[int(seed_id)]
            for j in range(i,len(infec_nodes)):
                if i != j:
                    new_id = int(infec_nodes[j])
                    new_loc = proper_loc[int(new_id)]
                    if new_id in country and seed_id in country:
                        new_country = country[new_id]
                        seed_country = country[seed_id] 
                        if new_country == seed_country and new_country == "NZ" and seed_country == "NZ":
                            trans_dist = geodesic(seed_prop_loc,new_loc).km
                            all_diff += trans_dist
                            all_combs += 1
                            if trans_dist > max_dist:
                                max_dist = trans_dist
        if all_combs > 0:
            avg_val = all_diff/all_combs
            all_avg[m] = avg_val
        all_max[m-1] = max_dist
    return all_max,all_avg
    """