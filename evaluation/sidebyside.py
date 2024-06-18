import os
import numpy as np
import pandas as pd

FINAL_FILE = 'side_by_side/sbug.csv'

def consolidate(tdata, tscores, ldata, lscores):
    final_data = []
    final_score = []

    for tind in range(len(tdata)):
        problem = tdata[tind]
        lind = ldata.index(problem)
        final_data.append(problem)
        final_score.append(max(tscores[tind], lscores[lind]))

    return final_data, final_score

def get_data(csv):
    with open(csv, "r") as output_file:
        existing = [i.split(",") for i in output_file.read().splitlines()]
    

    for e in existing:
        e[0] = e[0].split('.')[0]
    
    start_ind = existing[0].index('q1s')
    data = np.array(existing[1:])
    scores = []
    names = []
    for d in data:
        names.append(d[0])
        scores.append(np.mean([float(x) for x in list(d[start_ind:]) if len(x)]))
         
    return list(names), list(scores)


vdata, vscores = get_data('vanilla.csv')
bdata, bscores = get_data('bridge.csv')
tdata, tscores = get_data('tree_instruct.csv')

# ldata, lscores = get_data('zfinalized_csv/one_bug_llama_TI.csv')
# tdata, tscores = consolidate(tdata, tscores, ldata, lscores)

final_scores = []

with open(FINAL_FILE, 'a+') as f:
        f.write("low,mid,high\n")

ranks = []
for tind in range(len(tdata)):
    problem = tdata[tind]
    vind = vdata.index(problem)
    bind = bdata.index(problem)

    temp = np.array([tscores[tind], bscores[bind], vscores[vind]])
    ind = np.argsort(temp) + 1

    with open(FINAL_FILE, 'a+') as f:
        f.write(",".join([str(i) for i in ind]) + "\n")
    
    ranks.append(ind)

ranks = np.array(ranks)

percent = lambda x, y: str(np.sum(np.logical_and(ranks[:, 2] == x, ranks[:, 1] == y) + np.logical_and(ranks[:, 2] == x, ranks[:, 0] == y) + np.logical_and(ranks[:, 1] == x, ranks[:, 0] == y)) / len(ranks)) + "\n"
with open(FINAL_FILE, 'a+') as f:
    f.write('\% of TI over BRIDGE: ' + percent(1, 2))
    f.write('\% of TI over Vanilla: ' + percent(1, 3))
    f.write('\% of BRIDGE over Vanilla: ' + percent(2, 3))
    f.write('\% of BRIDGE over TI: ' + percent(2, 1))
    f.write('\% of Vanilla over TI: ' + percent(3, 1))
    f.write('\% of Vanilla over BRIDGE: ' + percent(3, 2))