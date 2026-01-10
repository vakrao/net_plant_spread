import networkx as nx

def find_network_stats(in_bond,out_bond):
    avg_kin = 0
    avg_sin = 0
    node_ids = set()
    L = set()
    for i in in_bond:
        node_incoming = in_bond[i]
        k_in = len(node_incoming)
        s_in = 0
        node_ids.add(i)
        for n in node_incoming:
            s_in += node_incoming[n]
            L.add((n,i))
        avg_sin += s_in
        avg_kin += k_in 
    for j in out_bond:
        node_outgoing = out_bond[j]
        k_out = len(node_outgoing)
        s_out = 0
        node_ids.add(j)
        for n in node_outgoing:
            L.add((j,n))
            s_out += node_outgoing[n]
        avg_sout += s_out
        avg_kout += k_out
    
    # stats of interest
    # <k_in>,<s_in>,N,L
    avg_sin = avg_sin/(len(in_bond))
    avg_kin = avg_kin/len(in_bond)
    avg_sout = avg_sout/(len(out_bond))
    avg_kout = avg_kout/len(out_bond)
    num_links = len(L)
    num_nodes = len(node_ids)
    # other interesting stats
    # largest connected component
    stat_list = [avg_kin,avg_sin,num_nodes,num_links]
    return stat_list



