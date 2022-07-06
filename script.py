import os

from pm4py.algo.filtering.log.end_activities import end_activities_filter
from pm4py.objects.log.importer.xes import importer as xes_importer
from pm4py.algo.filtering.log.start_activities import start_activities_filter
from pm4py.algo.discovery.alpha import algorithm as alpha_miner
from pm4py.visualization.petri_net import visualizer as pn_visualizer
from pm4py.objects.petri_net.exporter import exporter as pnml_exporter
from pm4py.algo.discovery.heuristics import algorithm as heuristics_miner
from pm4py.visualization.heuristics_net import visualizer as hn_visualizer

# Imports the .xes File
log = xes_importer.apply('loan_application_log.xes')

# Filters the log, printing its size before and after the filtering
print('log_size =' + str(len(log)))
log = start_activities_filter.apply_auto_filter(log, parameters={start_activities_filter.Parameters.DECREASING_FACTOR: 0.5})
end_activities = end_activities_filter.get_end_activities(log)
log = end_activities_filter.apply_auto_filter(log, parameters={end_activities_filter.Parameters.DECREASING_FACTOR: 0.5})
print('log_size =' + str(len(log)))

# Iterates the log and for each event adds a custom classifier composed of name and transition
for trace in log:
    for event in trace:
        event["customClassifier"] = event["concept:name"] + event["lifecycle:transition"]

# Discovering with the Heuristic Miner
heu_net = heuristics_miner.apply_heu(log, parameters={heuristics_miner.Variants.CLASSIC.value.Parameters.DEPENDENCY_THRESH: 0.99})

# Visualizes the Heuristic Net
gviz = hn_visualizer.apply(heu_net)
hn_visualizer.view(gviz)

# Converts the Heuristic Net into a PetriNet
net, im, fm = heuristics_miner.apply(log, parameters={heuristics_miner.Variants.CLASSIC.value.Parameters.DEPENDENCY_THRESH: 0.99})
gviz = pn_visualizer.apply(net, im, fm)
pn_visualizer.view(gviz)
pnml_exporter.apply(net, im, "final_petri_net_heuristic.pnml", final_marking=fm)

# Discovering with the Alpha Miner
parameters = {alpha_miner.Variants.ALPHA_VERSION_CLASSIC.value.Parameters.ACTIVITY_KEY: "customClassifier"}
net, initial_marking, final_marking = alpha_miner.apply(log, parameters=parameters)

# Visualizes of PetriNet
gviz = pn_visualizer.apply(net, initial_marking, final_marking)
pn_visualizer.view(gviz)

# Exports the resulting PetriNet into a .pnml file
pnml_exporter.apply(net, initial_marking, "final_petri_net.pnml", final_marking=final_marking)

