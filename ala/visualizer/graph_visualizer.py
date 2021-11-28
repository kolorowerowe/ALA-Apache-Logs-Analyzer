import pandas as pd
from itertools import chain
import pygraphviz
from more_itertools import pairwise
from collections import Counter
from config import Configuration
import os
import time

class GraphVisualizer:
    def __init__(self, formatedLogs):
        self.visFormLogs = formatedLogs
        if not os.path.exists(Configuration.resultDir):
            print("Create result directory")
            os.makedirs(Configuration.resultDir)

    def generateBaseGraph(self):
        print("Generate base graph")
        start = time.time()
        self.visFormLogs = pd.DataFrame(self.visFormLogs)
        ev_counter = self.visFormLogs.groupby(['Activity']).Activity.count()
        ev_counter.to_csv(os.path.join(Configuration.resultDir, "logs_counter.csv"))

        self.visFormLogs = self.visFormLogs.sort_values(by=['caseId', 'index']).groupby(['caseId']).agg({'Activity': ';'.join})

        self.visFormLogs['count'] = 0
        self.visFormLogs = self.visFormLogs.groupby('Activity', as_index=False).count().sort_values(['count'], ascending=False).reset_index(drop=True)

        self.visFormLogs['trace'] = [trace.split(';') for trace in self.visFormLogs['Activity']]

        w_net = dict()
        ev_start_set = set()
        ev_end_set = set()
        for index, row in self.visFormLogs[['trace','count']].iterrows():
            if row['trace'][0] not in ev_start_set:
                ev_start_set.add(row['trace'][0])
            if row['trace'][-1] not in ev_end_set:
                ev_end_set.add(row['trace'][-1])
            for ev_i, ev_j in pairwise(row['trace']):
                if ev_i not in w_net.keys():
                    w_net[ev_i] = Counter()
                w_net[ev_i][ev_j] += row['count']

        trace_counts = sorted(chain(*[c.values() for c in w_net.values()]))
        trace_min = trace_counts[0]
        trace_max = trace_counts[-1]
        color_min = ev_counter.min()
        color_max = ev_counter.max()
        G = pygraphviz.AGraph(strict= False, directed=True)
        G.graph_attr['rankdir'] = 'LR'
        G.node_attr['shape'] = 'Mrecord'
        for event, succesors in w_net.items():
            try:
                value = ev_counter[event]
                color = int(float(color_max-value)/float(color_max-color_min)*100.00)
                my_color = "#ff9933"+str(hex(color))[2:]
                G.add_node(event, style="rounded,filled", fillcolor=my_color)
                for pr, cnt in succesors.items(): # preceeding event, count
                    G.add_edge(event, pr, penwidth=4*cnt/(trace_max-trace_min)+0.1, label=cnt)
            except KeyError:
                print(event)

        for ev_end in ev_end_set:
            end = G.get_node(ev_end)
            end.attr['shape'] = 'circle'
            end.attr['label'] = ''

        G.add_node("start", shape="circle", label="")
        for ev_start in ev_start_set:
            G.add_edge("start", ev_start)

        drawPath = os.path.join(Configuration.resultDir, "logs_flow_graph.png")
        G.draw(drawPath, prog='dot')
        
        end = time.time()
        print(f"Generated graph. Took: {end-start}s")

        return drawPath
