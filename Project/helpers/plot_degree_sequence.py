#!/usr/bin/env python
"""
===============
Degree Sequence
===============

Random graph from given degree sequence.
"""
# Author: Aric Hagberg (hagberg@lanl.gov)
# Date: 2004-11-03 08:11:09 -0700 (Wed, 03 Nov 2004)
# Revision: 503

#    Copyright (C) 2004-2018 by
#    Aric Hagberg <hagberg@lanl.gov>
#    Dan Schult <dschult@colgate.edu>
#    Pieter Swart <swart@lanl.gov>
#    All rights reserved.
#    BSD license.

import matplotlib.pyplot as plt
from networkx import nx
import numpy as np

z = np.random.uniform(4,9,2000)
z = list(map(int, z))
if sum(z) %2 !=0:
    z[0] = 5 if z[0]%2 ==0 else 6
# z = [5, 3, 3, 3, 3, 2, 2, 2, 1, 1, 1]
print(nx.is_graphical(z))

print("Configuration model")
G = nx.configuration_model(z)  # configuration model
degree_sequence = [d for n, d in G.degree()]  # degree sequence
print("Degree sequence %s" % degree_sequence)
print("max degree %s",max(degree_sequence))
print("min degree %s",min(degree_sequence))
print("Connected: %s",nx.is_connected(G))
print("Degree histogram")
hist = {}
for d in degree_sequence:
    if d in hist:
        hist[d] += 1
    else:
        hist[d] = 1
print("degree #nodes")
for d in hist:
    print('%d %d' % (d, hist[d]))

# nx.draw(G)
# plt.show()
 