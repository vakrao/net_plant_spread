import node as nd
import link as lk

# return average degree
def avg_deg(nodes):
    k = 0
    total_links = 0
    total_sout = 0 
    total_sin = 0
    total_kout = 0 
    total_kin = 0
    total_nodes = .0001
    for x in nodes:
        n = nodes[x]
        out_links = n.get_out_links()
        in_links = n.get_in_links()
        total_nodes += 1
        for o in out_links:
            total_kout += 1
            ind_out = out_links[o]
            total_sout += ind_out.get_weight()
        for i in in_links:
            total_kin += 1
            ind_in = in_links[i]
            total_sin += ind_in.get_weight()
    avg_kin = total_kin/total_nodes
    avg_kout = total_kout/total_nodes
    avg_sin = total_sin/total_nodes
    avg_sout = total_sout/total_nodes
    return (avg_kin,avg_kout,avg_sin,avg_sout)


def node_amount(nodes):
    node_amount = 0 
    for n in nodes:
        real_node = nodes[n] 
        if real_node.is_active():
            node_amount += 1
    return node_amount


def link_amount(links):
    return len(links)

    


