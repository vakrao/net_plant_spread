import pandas as pd
import numpy as np
import copy
import csv


def read_property_data (filename,in_bond,out_bond):

    prop_size = {}
    with open(filename, newline='') as csvfile:
        rows = csv.reader(csvfile, delimiter=',')
        first_row = 0
        idx = 1
        for row in rows:
            if first_row > 0 and ((row[idx] in in_bond) or (row[idx] in out_bond)) :
                i = str(row[1])
                prop_size[i] = (float(row[idx+1]),float(row[idx+2]))
            first_row = 1

    return prop_size

def read_network_data (filename):
    in_bond = {}
    out_bond = {}
    with open(filename, newline='') as csvfile:
        rows = csv.reader(csvfile, delimiter=',')
        first_row = 0
        for row in rows:
            if first_row > 0:
                s = str(row[1])
                d = str(row[2])
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
                ##
                if s not in out_bond:
                    out_bond[s] = {}
                if d not in out_bond[s]:
                    out_bond[s][d] = float(0)
                out_bond[s][d] += float(w)
                ##
            first_row = 1
    return in_bond, out_bond

prop_fp  = "../data/pub_clean_prop_dat.csv"
prop_df = pd.read_csv("../data/pub_clean_prop_dat.csv")
hort_data = "../data/yearly_clean_agg.csv"

in_bond,out_bond = read_network_data(hort_data)

prop_coords = read_property_data(prop_fp,in_bond,out_bond)
neigh_lat,neigh_long = [],[]
node_lat,node_long = [],[]

# loop through all neighbors
for i in in_bond:
    coords_node = prop_coords[i]
    neighbor_nodes = in_bond[i]
    for n in neighbor_nodes:
        neigh_coords = prop_coords[n]
        neigh_lat.append(neigh_coords[0])
        neigh_long.append(neigh_coords[1])
        node_lat.append(coords_node[0])
        node_long.append(coords_node[1])

neigh_dict_lat = {"node_lat":node_lat,"node_long":node_long,"neigh_lat":neigh_lat,"neigh_long":neigh_long}
neigh_data = pd.DataFrame.from_dict(neigh_dict_lat)
neigh_data.to_csv("../data/in_bond_neighbors.csv")
    
