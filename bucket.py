import random
import rbnmol
import reaction

def mols_to_string(mols):
    toreturn = ""
    for thing in mols:
        toreturn = toreturn + str(thing) + " + "
    return toreturn[:-3]

def printout(reatants, products):
    print str(reactants[0]), "+", str(reactants[1]),
    print "=>",
    for thing in products:
        print str(thing),
        if thing is not products[-1]:
            print "+",
    print ""
    
def to_elements(mols):
    elements = []
    for mol in mols:
        for letter in str(mol):
            if letter in "ABCDEFGHIJLKMNOPQRSTUVWXYZ":
                elements.append(letter)
    return elements

if __name__=="__main__":
    bucket = []
    seed = 20
    copies = 200
    steps = 200
    rng = random.Random(42)
    
    
    for i in xrange(seed):
        bucket = bucket + [rbnmol.rbnmol.generate(10, i) for j in xrange(copies)]
        
    for i in xrange(steps):
        rng.shuffle(bucket)
        nextbucket = []
        for j in xrange(0, len(bucket), 2):
            if j < len(bucket)-1:
                reactants = (bucket[j], bucket[j+1])
                assert bucket[j] is not bucket[j+1]
                #print "Reactants:", mols_to_string(reactants)
                products = tuple(reaction.reaction(*reactants))
                if reactants != products:
                    printout(reactants, products)
                    
                #sanity check it is all the same stuff
                assert to_elements(reactants) == to_elements(products)
                    
                nextbucket = nextbucket + list(products)
            else:
                nextbucket.append(bucket[j])
        bucket = nextbucket
