import igraph as ig
import networkx as nx
import matplotlib.pyplot as plt
import random
import pandas as pd
from mod_si import *
"""
creates a directed network
using networkX 
- returns a graph object G, and a dictionary
where the ID from data corresponds to the ID in the network 
- the network node IDs go from 0 to N
- the data node IDs are strings, and assinged randomly in the data
"""
def create_directed_network(hort_data):
    in_data,out_data = read_network_data(hort_data)

    id_to_index = {}
    index_to_id = {}
    counter = 0

    for n in in_data:
        id_to_index[n] = counter
        index_to_id[counter] = n
        counter += 1

    for n in out_data:
        if n not in id_to_index:
            id_to_index[n] = counter
            index_to_id[counter] = n
            counter += 1


    # convet id values to 0-vertex_amount
    mod_in_data = {}
    for d in in_data:
        x = in_data[d]
        new_d = id_to_index[d]
        mod_in_data[new_d] = {}
        for s in x:
            new_s = id_to_index[s]
            mod_in_data[new_d][new_s] = x[s]

    mod_out_data = {}
    for s in out_data:
        x = out_data[s]
        new_s = id_to_index[s]
        mod_out_data[new_s] = {}
        for d in x:
            new_d = id_to_index[d]
            mod_out_data[new_s][new_d] = x[d]
    all_edges = []
    # now, create graph
    for d in mod_in_data:
        x = mod_in_data[d]
        for s in x:
            #all_edges.append((d,s))
            weight_val = mod_in_data[d][s]
            #weights.append(weight_val)
            all_edges.append((d,s,weight_val))
    G = nx.DiGraph()
    # now, add more edges to graph
    for s in mod_out_data:
        x = mod_out_data[s]
        for d in x:
            weight_val = mod_out_data[s][d]
            G.add_edge(s,d,weight=weight_val)
    #Gcc = sorted(nx.strongly_connected_components(G), key=len, reverse=True)
    #G0 = G.subgraph(Gcc[0])
    return G,id_to_index

def create_net_stats_df(G,id_dict,nodes,in_bound):

    clustering = nx.clustering(G)
    betweeneess = nx.betweenness_centrality(G)
    ev = nx.pagerank(G,weight="weight")
    all_ev,all_bet,all_clust,all_id,all_deg,all_w = [],[],[],[],[],[]
    for n in nodes:
        network_id = id_dict[n]
        clustering_val = clustering[network_id]
        bet_val = betweeneess[network_id]
        ev_val = ev[network_id]
        deg_val = G.degree(network_id)
        all_id.append(n)
        all_bet.append(bet_val)
        all_clust.append(clustering_val)
        all_ev.append(ev_val)
        all_deg.append(deg_val)
        weight_val = 0
        if n in in_bound:
            deg_dict = in_bound[n]
            for w in deg_dict:
                weight_val += deg_dict[w]
        all_w.append(weight_val)
    save_dict = {'ID':all_id,'bet_ctr':all_bet,'clust_coeff':all_clust,'pagerank':all_ev,'deg_ctr':all_deg,'weight':all_w}
    save_df = pd.DataFrame.from_dict(save_dict)
    return save_dict,save_df

def rank_nodes(stat_df,metric):
    rank_df = stat_df.sort_values(by=[metric],ascending=False)
    rank_title = metric+"_rank"
    rank_amount = len(list(rank_df["metric"]))
    ord_rank = [i for i in range(1,rank_amount+1)]
    rank_df[rank_title] = ord_rank
    merged_df = pd.merge(stat_df,rank_df,how="right",on="ID")
    return merged_df






def find_cluster_coeff():
    hort_data= "../params/horticulture365.csv"
    in_data,out_data = read_network_data(hort_data)

    id_to_index = {}
    index_to_id = {}
    counter = 0

    for n in in_data:
        id_to_index[n] = counter
        index_to_id[counter] = n
        counter += 1

    for n in out_data:
        if n not in id_to_index:
            id_to_index[n] = counter
            index_to_id[counter] = n
            counter += 1


    # convet id values to 0-vertex_amount
    mod_in_data = {}
    for d in in_data:
        x = in_data[d]
        new_d = id_to_index[d]
        mod_in_data[new_d] = {}
        for s in x:
            new_s = id_to_index[s]
            mod_in_data[new_d][new_s] = x[s]

    mod_out_data = {}
    for s in out_data:
        x = out_data[s]
        new_s = id_to_index[s]
        mod_out_data[new_s] = {}
        for d in x:
            new_d = id_to_index[d]
            mod_out_data[new_s][new_d] = x[d]
    all_edges = []
    # now, create graph
    for d in mod_in_data:
        x = mod_in_data[d]
        for s in x:
            #all_edges.append((d,s))
            weight_val = mod_in_data[d][s]
            #weights.append(weight_val)
            all_edges.append((d,s,weight_val))
    G = nx.DiGraph()
    # now, create graph
    for s in mod_out_data:
        x = mod_out_data[s]
        for d in x:
            weight_val = mod_out_data[s][d]
            G.add_edge(s,d,weight=weight_val)


    #G.add_nodes_from(counter)
    #G.add_edges_from(all_edges)
    comp_amount = 0
    max_nodes = 0
    for component in nx.strongly_connected_components(G):
        comp_amount += 1
    largest = (max(nx.strongly_connected_components(G), key=len))


    nx.draw(largest)
    #plt.show()
    plt.savefig("net_plot.png")
    #g = ig.Graph()
    #g.add_vertices(counter)
    #g.add_edges(all_edges)
    #g.es["w"] = weights
    #
    ## get connected components
    #components = g.connected_components(mode='weak')
    #fig, ax = plt.subplots()
    #ig.plot(
    #    components,
    #    target=ax,
    #    palette=ig.RainbowPalette(),
    #    vertex_size=10,
    #    vertex_color=list(map(int, ig.rescale(components.membership, (0, 200), clamp=True))),
    #    edge_width=0.2
    #)
    #plt.show()

