import random
import rbnmol
import rbnmol_cached
import reaction

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
            self.content = self.content + [self.rbncls.generate(10, seed)] * copies
            
    def run(self, steps, rng=None):
        if rng is None:
            rng = random.Random()
            
        for i in xrange(steps):
            rng.shuffle(self.content)
            nextbucket = self.step()
            self.content = nextbucket
            
    def step(self):
        nextbucket = []
        for j in xrange(0, len(self.content), 2):
            if j < len(self.content)-1:
                reactants = (self.content[j], self.content[j+1])
                products = tuple(reaction.reaction(*reactants))
                thisreaction = (reactants, products)
                if products != reactants:
                    if thisreaction not in self.reactions:
                        self.report(reactants, products)
                    self.reactions.add(thisreaction)
                    
                    
                #sanity check it is all the same stuff
                assert to_elements(reactants) == to_elements(products)
                    
                nextbucket = nextbucket + list(products)
            else:
                nextbucket.append(self.content[j])
        return nextbucket

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

    
if __name__=="__main__":
    rbncls = rbnmol.rbnmol_total_sumzero
    
    import sys
    print sys.argv
    if len(sys.argv) >= 2 and sys.argv[1] == "cached":
        rbncls = rbnmol_cached.rbnmol_cached_total_sumzero
        print "Using cached rbnmol class"
    
    rng = random.Random(42)
    bucket = Bucket(rbncls)
    bucket.fill(xrange(10), 20)
    bucket.run(100, rng)
