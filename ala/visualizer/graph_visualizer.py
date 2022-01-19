import pandas as pd
from itertools import chain
import pygraphviz
from more_itertools import pairwise
from collections import Counter
from ALparser.ALParser import ApacheLogParser
from config import Configuration
import os
import time

def APDiscovery(w_net, ev_end_set, currentNode, visited, ap, parent, low, disc, time=0):
  if currentNode in ev_end_set:
    return ap

  #Count of children in current node 
  children =0
  # Mark the current node as visited and print it 
  visited[currentNode]= True

  # Initialize discovery time and low value 
  disc[currentNode] = time 
  low[currentNode] = time 
  time += 1

  for vertex in w_net[currentNode].keys():
    if vertex in ev_end_set:
      continue

    # If vertex is not visited yet, make it a child of currentNode and visit it
    if visited[vertex] == False : 
      parent[vertex] = currentNode 
      children += 1
      ap = APDiscovery(w_net, ev_end_set, vertex, visited, ap, parent, low, disc, time) 

      # Check if the subtree rooted with vertex has a connection to one of the ancestors of currentNode
      low[currentNode] = min(low[currentNode], low[vertex]) 

      # currentNode is an articulation point in following cases 
      # (1) currentNode is root of DFS tree and has two or more children. 
      if parent[currentNode] == -1 and children > 1: 
        ap[currentNode] = True

      #(2) If currentNode is not root and low value of one of its child is more 
      # than discovery value of currentNode. 
      if parent[currentNode] != -1 and low[vertex] >= disc[currentNode]: 
        ap[currentNode] = True
        
    # Update low value of currentNode for parent function calls	 
    elif vertex != parent[currentNode]: 
      low[currentNode] = min(low[currentNode], disc[vertex])

  return ap

def APInit(w_net, ev_end_set): 
  # Mark all the vertices as not visited  
  visited = dict.fromkeys(w_net.keys(),False)
  disc = dict.fromkeys(w_net.keys(),float("Inf"))
  low = dict.fromkeys(w_net.keys(),float("Inf"))
  parent = dict.fromkeys(w_net.keys(),-1)
  ap = dict.fromkeys(w_net.keys(),False)

  for node in w_net.keys():
    if visited[node] == False: 
      ap = APDiscovery(w_net, ev_end_set, node, visited, ap, parent, low, disc) 

  return ap

def countPredecessors(graph, node):
  count = 0

  for succesors in graph.values():
    if node in succesors.keys():
      count += 1

  return count

def getHighestInputEdge(graph, node):
  value = 0
  source = None

  for pr, succesors in graph.items():
    if node in succesors.keys() and succesors[node] > value:
      value = succesors[node]
      source = pr

  return source, value

def getHighestOutputEdge(graph, node):
  value = 0
  destination = None

  for succesor, cnt in graph[node].items():
    if cnt > value:
      value = cnt
      destination = succesor

  return destination, value

class GraphVisualizer:
    def __init__(self, formatedLogs):
        self.visFormLogs = formatedLogs
        if not os.path.exists(Configuration.resultDir):
            Configuration.ALAprint("Create result directory", 1)
            os.makedirs(Configuration.resultDir)

    def applyPredictions(self, sus_requests):
      attacked = [item for sublist in list(sus_requests.values()) for item in sublist]
      req = []
      for item in attacked:
        normRequest = ApacheLogParser.parseExternalLine(item).lower().split(" ")[1]
        normRequest = normRequest.split("?")[0]
        url = normRequest.split(".")
        if normRequest[len(normRequest) - 1] == '/':
            normRequest = normRequest[:len(normRequest)-1]
        if len(normRequest) > 0 and (len(url) == 1 or url[len(url)-1].lower() not in Configuration.extensionsToRemove):
            req.append(normRequest)

      for item in req:
        try:
          node = self.G.get_node(item)
          node.attr['fillcolor'] = "red"
        except KeyError:
            print(item)

      drawPath = os.path.join(Configuration.resultDir, "logs_flow_graph.png")
      self.G.draw(drawPath, prog='dot')
      self.G.close()

    def generateBaseGraph(self):
        Configuration.ALAprint("Generate base graph", 1)
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
        if trace_max == trace_min:
            trace_max = trace_min + 1
        color_min = ev_counter.min()
        color_max = ev_counter.max()
        self.G = pygraphviz.AGraph(strict= False, directed=True)
        self.G.graph_attr['rankdir'] = 'LR'
        self.G.node_attr['shape'] = 'Mrecord'

        for event, succesors in w_net.items():
          value = ev_counter[event]
          try:
            color = int(float(color_max-value)/float(color_max-color_min)*100.00)
            my_color = "#ff9933"+str(hex(color))[2:]
            self.G.add_node(event, style="rounded,filled", fillcolor=my_color)
            for pr, cnt in succesors.items(): # preceeding event, count
              self.G.add_edge(event, pr, penwidth=4*cnt/(trace_max-trace_min)+0.1, label=cnt)
          except KeyError:
              print(event)

        for ev_end in ev_end_set:
            end = self.G.get_node(ev_end)
            end.attr['shape'] = 'circle'
            end.attr['label'] = ''

        self.G.add_node("start", shape="circle", label="Start")
        for ev_start in ev_start_set:
            self.G.add_edge("start", ev_start)

        drawPath = os.path.join(Configuration.resultDir, "logs_flow_graph_unfiltered.png")
        self.G.draw(drawPath, prog='dot')

        self.G = pygraphviz.AGraph(strict= False, directed=True)
        self.G.graph_attr['rankdir'] = 'LR'
        self.G.node_attr['shape'] = 'Mrecord'

        w_net_corrected = dict()
        ap = APInit(w_net, ev_end_set)
        try:
            for event, succesors in w_net.items():
                value = ev_counter[event]
                if value <= Configuration.event_max or ap[event] or event in ev_start_set:
                    w_net_corrected[event] = Counter()
                for pr, cnt in succesors.items(): # preceeding event, count
                    # if event should be drawn at all and cnt is within treshold
                    if (pr in ev_end_set or ev_counter[pr] <= Configuration.event_max or ap[pr] or pr in ev_start_set) and cnt <= Configuration.flow_max:
                        w_net_corrected[event][pr] += cnt
        except KeyError:
            print(event)

        visited = dict.fromkeys(w_net.keys(),False)

        for event in ev_end_set:
            if not countPredecessors(w_net_corrected, event):
                new_node, new_value = getHighestInputEdge(w_net, event)
                if not w_net_corrected.get(new_node):
                    w_net_corrected[new_node] = Counter()
                w_net_corrected[new_node][event] += new_value

        for event, succesors in w_net_corrected.items():
            visited[event] = True
            value = ev_counter[event]
            if len(succesors) or countPredecessors(w_net_corrected, event) or event in ev_start_set:
            # event should be drawn but has only input edges
                if not len(succesors):
                    new_node, new_value = getHighestOutputEdge(w_net, event)
                    succesors[new_node] += new_value
                # event should be drawn but has only output edges
                elif not countPredecessors(w_net_corrected, event) and not event in ev_start_set:
                    new_node, new_value = getHighestInputEdge(w_net, event)
                    if not visited[new_node]:
                        w_net_corrected[new_node][event] += new_value
                    else:
                        self.G.add_edge(new_node, event, penwidth=4*new_value/(trace_max-trace_min)+0.1, label=new_value)
            color = int(float(color_min-value)/float(color_min-color_max)*100.00)
            my_color = "#ff9933"+str(hex(color))[2:]
            self.G.add_node(event, style="rounded,filled", fillcolor=my_color)
            for pr, cnt in succesors.items(): # preceeding event, count
                # if pr not in ev_end_set:
                #     pr = pr + f' {ev_counter[pr]}'
                self.G.add_edge(event, pr, penwidth=4*cnt/(trace_max-trace_min)+0.1, label=cnt)

        for ev_end in ev_end_set:
            end = self.G.get_node(ev_end)
            end.attr['shape'] = 'circle'
            end.attr['label'] = ''

        self.G.add_node("start", shape="circle", label="Start")
        for ev_start in ev_start_set:
            self.G.add_edge("start", ev_start)

        drawPath = os.path.join(Configuration.resultDir, "logs_flow_graph.png")
        self.G.draw(drawPath, prog='dot')
        
        end = time.time()
        Configuration.ALAprint(f"Generated graph. Took: {end-start}s", 2)

        return drawPath
