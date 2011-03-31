import os
import sys
sys.path.append(os.path.abspath("src/"))

import random


import rbnmol
import rbnmol_cached
import bucket

if __name__ == "__main__":
    rbncls = rbnmol.rbnmol_total_sumzero
    
    if len(sys.argv) >= 2 and sys.argv[1] == "cached":
        rbncls = rbnmol_cached.rbnmol_cached_total_sumzero
        print "Using cached rbnmol class"
    
    rng = random.Random(42)
    buck = bucket.Bucket(rbncls)
    buck.fill(xrange(10), 20)
    buck.run(200, rng)
    
    
