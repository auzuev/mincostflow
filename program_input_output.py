from traceback import format_exc, print_tb
from ortools.graph import pywrapgraph

def check_ortools():   
    min_cost_flow = pywrapgraph.SimpleMinCostFlow()

    # Define four parallel arrays: sources, destinations, capacities,
    # and unit costs between each pair. For instance, the arc from node 0
    # to node 1 has a capacity of 15.
    start_nodes = [0, 0, 1, 1, 1, 2, 2, 3, 4]
    end_nodes = [1, 2, 2, 3, 4, 3, 4, 4, 2]
    capacities = [15, 8, 20, 4, 10, 15, 4, 20, 5]
    unit_costs = [4, 4, 2, 2, 6, 1, 3, 2, 3]

    # Define an array of supplies at each node.
    supplies = [20, 0, 0, -5, -15]

    # Add each arc.
    for arc in zip(start_nodes, end_nodes, capacities, unit_costs):
        min_cost_flow.AddArcWithCapacityAndUnitCost(arc[0], arc[1], arc[2],
                                                    arc[3])

    # Add node supply.
    for count, supply in enumerate(supplies):
        min_cost_flow.SetNodeSupply(count, supply)

    status = min_cost_flow.Solve()

    if status != min_cost_flow.OPTIMAL:
        print('There was an issue with the min cost flow input.')
        print(f'Status: {status}')
        exit(1)
    print('Minimum cost: ', min_cost_flow.OptimalCost())
    print('')
    print(' Arc   Flow / Capacity  Cost')
    for i in range(min_cost_flow.NumArcs()):
        cost = min_cost_flow.Flow(i) * min_cost_flow.UnitCost(i)
        print('%1s -> %1s    %3s   / %3s   %3s' %
              (min_cost_flow.Tail(i), min_cost_flow.Head(i),
               min_cost_flow.Flow(i), min_cost_flow.Capacity(i), cost))

from random import random, randint, seed
seed(1)
class Model:
    def __init__(self):
        file = 'matrix.txt'
        with open(file, 'r') as f:
            self.items_nr = int(f.readline())
            self.clusters_nr = int(f.readline())
            self.warehouses_nr = int(f.readline())
            
            warehouse_clusters = [int(x) for x in f.readline().split()]
            warehouse_caps = [int(x) for x in f.readline().split()]
            item_amounts = [int(x) for x in f.readline().split()]
            
            self.item___amount = {}
            self.warehouse___cap = {}
            self.warehouse___cluster = {}

            for wh, cap in enumerate(warehouse_caps):
                self.warehouse___cap[wh] = cap
            for wh, clus in enumerate(warehouse_clusters):
                self.warehouse___cluster[wh] = clus
            for item, amount in enumerate(item_amounts):
                self.item___amount[item] = amount

            a = f.readline()
            self.item___cluster___fee = {}
            self.item___warehouse___fee = {}
            self.item___cluster___forecast = {}
            
            item___curr_piority = [0] * self.items_nr

            for wh in range(self.warehouses_nr):
                row = [int(x) for x in f.readline().split()]
                for item, legality in enumerate(row):
                    if legality == 0:
                        continue
                    item___curr_piority[item] += 1
                    if item not in self.item___warehouse___fee:
                        self.item___warehouse___fee[item] = {}
                    self.item___warehouse___fee[item][wh] = item___curr_piority[item] + 10
                    cluster = self.warehouse___cluster[wh]

            f.readline()
            for wh in range(self.warehouses_nr):
                row = [int(x) for x in f.readline().split()]
                for item, amount in enumerate(row):
                    if amount == 0:
                        continue
                    if item not in self.item___cluster___forecast:
                        self.item___cluster___forecast[item] = {}
                    cluster = self.warehouse___cluster[wh]
                    self.item___cluster___forecast[item][cluster] = amount
            print(self.item___cluster___forecast)


            f.readline()
            for item in range(self.items_nr):
                line = f.readline().split('\t')
                for i, cluster_str in enumerate(line):
                    sp = cluster_str.split()
                    if len(sp) < 2:
                        continue
                    cluster = int(sp[1])
                    if item not in self.item___cluster___fee:
                        self.item___cluster___fee[item] = {}
                    self.item___cluster___fee[item][cluster - 1] = (i + 1) * 100000000
                
                
    def sum(self):
        return sum(self.item___amount.values())
    
    def item___node(self, item):
        assert item < self.items_nr
        return item + 2
    def warehouse___node(self, warehouse):
        assert warehouse < self.warehouses_nr
        return self.items_nr + warehouse + 2
    def item_cluster___node(self, item, cluster):
        assert item < self.items_nr
        assert cluster < self.clusters_nr
        return 2 + self.items_nr + self.warehouses_nr + item * self.clusters_nr + cluster
    def node___item_cluster(self, node):
        assert node >= 2 + self.items_nr + self.warehouses_nr
        n = node - self.items_nr - self.warehouses_nr - 2
        cluster = n % self.clusters_nr
        item = n // self.clusters_nr
        return item, cluster

    def node____readable_node(self, node):
        if node == 0:
            return 'source'
        if node == 1:
            return 'dest'
        if node < self.items_nr + 2:
            return f'item{node -2}'
        if node < self.items_nr + self.warehouses_nr + 2:
            return f'wh{node - self.items_nr - 2}'
        item, cluster = self.node___item_cluster(node)
        return f'it{item}cl{cluster}'

    def get_nodes_nr(self):
        return self.item_cluster___node(self.items_nr - 1, self.clusters_nr - 1) + 1
    
def translate_graph(m: Model, mcf: pywrapgraph.SimpleMinCostFlow):
    # arc is edge
    # mcf.AddArcWithCapacityAndUnitCost(st, en, cap, cost)
    # source -> items cap - amount, cost 0
    for item, amount in m.item___amount.items():
        item_node = m.item___node(item)
        cost = 0
        start = 0
        mcf.AddArcWithCapacityAndUnitCost(start, item_node, amount, cost)
    # item -> item cluster
    for item in range(m.items_nr):
        # cost 0, cap forecast
        item_node = m.item___node(item)
        for cluster, forecast in m.item___cluster___forecast[item].items():
            item_cluster_node = m.item_cluster___node(item, cluster)
            cost = 0
            # print(item_node, item_cluster_node, forecast, cost)
            # print(type(forecast))
            mcf.AddArcWithCapacityAndUnitCost(item_node, item_cluster_node,
                                             int(forecast), cost)
        # cost fee, cap item amount
        for cluster, fee in m.item___cluster___fee[item].items():
            item_cluster_node = m.item_cluster___node(item, cluster)
            cap = m.item___amount[item]
            # print(item_node, item_cluster_node, cap, fee)
            # print('*', fee)
            mcf.AddArcWithCapacityAndUnitCost(item_node, item_cluster_node, cap, fee)
        
        # item cluster -> warehouse
        for warehouse, fee in m.item___warehouse___fee[item].items():
            # cost wh fee, cap inf
            cap = m.item___amount[item]
            wh_node = m.warehouse___node(warehouse)
            cluster = m.warehouse___cluster[warehouse]
            ic_node = m.item_cluster___node(item, cluster)
            # print(ic_node, wh_node, cap, fee)
            mcf.AddArcWithCapacityAndUnitCost(ic_node, wh_node, cap, fee)
            
    # warehouse -> dest to limit cap
    for wh, cap in m.warehouse___cap.items():
        wh_node = m.warehouse___node(wh)
        cost = 0
        dest = 1
        mcf.AddArcWithCapacityAndUnitCost(wh_node, dest, cap, cost)
    
    # mcf.SetNodeSupply(node, supply) # supply 0 for all nodes except source and dest
    for node in range(2, m.get_nodes_nr()):
        mcf.SetNodeSupply(node, 0)
    # source
    mcf.SetNodeSupply(0, m.sum())
    # dest
    mcf.SetNodeSupply(1, -m.sum())



if __name__ == '__main__':
    mincostflow = pywrapgraph.SimpleMinCostFlow()
    model = Model()
    translate_graph(model, mincostflow)
    mincostflow.Solve()

    min_cost_flow = mincostflow
    print('Minimum cost: ', min_cost_flow.OptimalCost())
    print('')
    print(' Edge   Flow / Capacity  Cost')
    for i in range(min_cost_flow.NumArcs()):
        cost = min_cost_flow.Flow(i) * min_cost_flow.UnitCost(i)
        print('%1s -> %1s    %3s   / %3s   %3s' %
            (model.node____readable_node(min_cost_flow.Tail(i)), 
            model.node____readable_node(min_cost_flow.Head(i)),
            min_cost_flow.Flow(i), min_cost_flow.Capacity(i), cost))

    ans = [[0] * model.items_nr for _ in range(model.warehouses_nr)]

    for i in range(min_cost_flow.NumArcs()):
            node1 = model.node____readable_node(min_cost_flow.Tail(i)) 
            node2 = model.node____readable_node(min_cost_flow.Head(i))
            if node1[:4] == 'item':
                continue
            if node1[:2] != 'it':
                continue
            if node2[:2] != 'wh':
                continue
            wh = int(node2[2:])
            item = int(node1[2:].split('c')[0])
            ans[wh][item] += min_cost_flow.Flow(i)

    for row in ans:
        print(*row)
     
    # for item in range(model.items_nr):
    #     for warehouse in range(model.warehouses_nr):
    #         model.