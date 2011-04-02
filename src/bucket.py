import random
import reaction

import sys
import os
sys.path.append(os.path.abspath("../PyAChemKit/"))

import AChemKit.sims_simple
import AChemKit.sims_gillespie
import AChemKit.bucket as AChemBucket

def mols_to_string(mols):
    toreturn = ""
    for thing in mols:
        toreturn = toreturn + str(thing) + " + "
    return toreturn[:-3]
    
def to_elements(mols):
    elements = []
    for mol in mols:
        for letter in str(mol):
            if letter in "ABCDEFGHIJLKMNOPQRSTUVWXYZ":
                elements.append(letter)
    return elements

class Bucket(object):
    def __init__(self, rbncls):
        self.content = []
        self.rbncls = rbncls
        self.reactions = set()
        
    def fill(self, seeds, copies):
        self.content = []
        for seed in seeds:
            for i in xrange(copies):
                self.content = self.content + [self.rbncls.generate(10, seed)]

    @classmethod
    def report(cls, reactants, products):
        for thing in reactants:
            print str(thing),
            if thing is not reactants[-1]:
                print "+",
        print "=>",
        for thing in products:
            print str(thing),
            if thing is not products[-1]:
                print "+",
        print ""
        
    def run(self, time, rng):
        rbnworld = AChemKit.sims_simple.AbstractAChem()
        rbnworld.noreactants = 2
        rbnworld.react = reaction.reaction
    
        #events = AChemKit.sims_simple.simulate_itterative_iter(rbnworld, self.content, time, rng)
        
        #events = AChemKit.sims_simple.simulate_stepwise_multiprocessing_iter(rbnworld, self.content, time, rng)
        #events = AChemKit.sims_simple.simulate_stepwise_iter(rbnworld, self.content, time, rng)
        events = AChemKit.sims_gillespie.simulate_gillespie_iter(rbnworld, self.content, time, rng)
        b = AChemBucket.Bucket(events)
        str(b.reactionnet)
        #print str(b.reactionnet)
