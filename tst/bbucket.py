import os
import sys
sys.path.append(os.path.abspath("."))
sys.path.append(os.path.abspath("../PyAChemKit/"))

from guppy import hpy
import cProfile
import pstats

import tempfile
import random


from rbnworld import rbnmol
from rbnworld import reaction
from rbnworld import rbnmol_cached

import AChemKit
import AChemKit.sims_simple
import AChemKit.sims_gillespie
import AChemKit.bucket

def main():
    rbncls = rbnmol.rbnmol_total_sumzero
    
    if len(sys.argv) >= 2 and sys.argv[1] == "cached":
        rbncls = rbnmol_cached.rbnmol_cached_total_sumzero
        print "Using cached rbnmol class"
    
    time = 20.0
    seeds = 20
    copies = 25
    
    rng = random.Random(42)
    content = []
    for seed in xrange(seeds):
        content += [rbncls.generate(10, seed)]*copies

    
    
    rbnworld = AChemKit.sims_simple.AChemAbstract()
    rbnworld.noreactants = 2
    rbnworld.react = reaction.react

    #events = AChemKit.sims_simple.simulate_itterative_iter(rbnworld, self.content, time, rng)
    
    #events = AChemKit.sims_simple.simulate_stepwise_multiprocessing_iter(rbnworld, self.content, time, rng)
    #events = AChemKit.sims_simple.simulate_stepwise_iter(rbnworld, self.content, time, rng)
    events = AChemKit.sims_gillespie.simulate_gillespie_iter(rbnworld, content, time, rng)
    b = AChemKit.bucket.Bucket(events)
    h = hpy()
    print h.heap()
    

if __name__ == "__main__":
    tmp = tempfile.NamedTemporaryFile(delete = False)
    filename = tmp.name
    tmp.close()
    cProfile.run('main()', filename)
    s = pstats.Stats(filename)
    s.sort_stats("time")
    s.print_stats(10)
    os.remove(filename)
    #main()
