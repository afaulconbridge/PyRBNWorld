import random
    
class hashabledict(dict):
    __slots__=["_hash"]
    def __hash__(self):
        rval = getattr(self, '_hash', None)
        if rval is None:
            rval = self._hash = hash(frozenset(self.iteritems()))
        return rval
    
class rbn(object):

    __slots__ = ["states", "functions", "inputs", "bonding", "_hash", "_states", "seed", "_run_and_cycle"]
    
    #these are set to None in the class version
    #so that __init__ can tell between recycled instance passed 
    #on from __new__  through a generator function
    #and a fresh instance from __new__ioter
    #states = None
    #functions = None
    #inputs = None
    #bonding = None
    #_hash = None


    @property
    def states(self):
        return self._states


    @classmethod
    def generate(cls, n, seed=None, rng = None, b=0):
        states = []
        functions = []
        inputs = []
        if rng is None:
            if seed is not None:
                rng = random.Random(seed)
            else:
                rng = random.Random()
        for i in xrange(n):
            states.append(rng.choice((0,1)))
            functions.append((rng.choice((0,1)), rng.choice((0,1)), rng.choice((0,1)), rng.choice((0,1))))
            inputs.append((rng.choice(xrange(n)), rng.choice(xrange(n))))
        bonding = {}
        for i in xrange(b):
            bonding[i] = 0
        newrbn = cls(states, functions, inputs, bonding)
        newrbn.seed = seed
        return newrbn
        
    @classmethod
    def from_genome(cls, genome, b=0):
        #genome is n nodes each with 2 inputs
        n = len(genome)/7
        states = []
        functions = []
        inputs = []
    
        for i in xrange(n):
            states.append(genome[(7*i)+6])
            f00 = genome[(7*i)+0]
            f01 = genome[(7*i)+1]
            f10 = genome[(7*i)+2]
            f11 = genome[(7*i)+3]
            functions.append((f00, f01, f10, f11))
            input1 = genome[(7*i)+4]
            input2 = genome[(7*i)+5]
            inputs.append((input1, input2))
    
        bonding = {}
        for i in xrange(b):
            bonding[i] = 0
            
        newrbn = cls(states, functions, inputs, bonding)
        #newrbn.genome = genome
        return newrbn

    def __init__(self, states, functions, inputs, bonding = {}):
        try:  
            self.states
        except AttributeError:
            if not isinstance(states, tuple):
                states = tuple(states)
            self._states = states
            if not isinstance(functions, tuple):
                functions = tuple(functions)
            self.functions = functions
            
            self.inputs = tuple([tuple(x) for x in inputs])
        
        #this should be a frozen dict, but dont have one of those right now...
        self.bonding = hashabledict(bonding)
        self._hash = None
        self.seed = None
        self._run_and_cycle = None
        
        #assert set(bonding.keys()) <= set(xrange(len(self.states)))
        assert len(states) == len(functions)
        assert len(states) == len(inputs)
        
    def __getstate__(self):
        return (self.states, self.functions, self.inputs, tuple(self.bonding.items()), self.seed, self._run_and_cycle)
        
    def __setstate__(self, state):
        states, functions, inputs, bonding, seed, _run_and_cycle = state
        self._states = states
        self.functions = functions
        self.inputs = inputs
        self.bonding = hashabledict(bonding)
        self.seed =  seed
        self._run_and_cycle = _run_and_cycle
        self._hash = None
        
    def __hash__(self):
        if self._hash is None:
            self._hash = hash(self.states) ^ hash(self.functions) ^ hash(self.inputs)
        return self._hash
        
    def __eq__(self, other):
        if other is None:
            return False
        if other is self:
            return True
        toreturn = self.states == other.states and self.functions == other.functions and self.inputs == other.inputs and self.bonding == other.bonding
        if toreturn:
            assert hash(self) == hash(other)
        return toreturn
        
    def __ne__(self, other):
        return not self == other
        
    def __lt__(self, other):
        if self == other:
            return False
        elif self.functions != other.functions:
            return self.functions < other.functions
        elif self.inputs != other.inputs:
            return self.inputs < other.inputs
        elif self.states != other.states:
            return self.states < other.states
        elif self.bonding != other.bonding:
            return self.bonding < other.bonding
        else:
            return False
            
    def __gt__(self, other):
        if self == other:
            return False
        elif self.functions != other.functions:
            return self.functions > other.functions
        elif self.inputs != other.inputs:
            return self.inputs > other.inputs
        elif self.states != other.states:
            return self.states > other.states
        elif self.bonding != other.bonding:
            return self.bonding > other.bonding
        else:
            return False
            
    def __le__(self, other):
        if self == other:
            return True
        else:
            return self < other
            
    def __ge__(self, other):
        if self == other:
            return True
        else:
            return self > other
        
    def __add__(self, other):
        reactants = (self, other)
        #even though we only have two reactants here
        #allow for an arbitary number in case
        #of future expansion
        
        selfn = len(self.states)
        #these all use append
        #might be faster to create lists of the right length
        #and fill them in.
        newstates = []
        for reactant in reactants:
            newstates += reactant.states
        newfunctions = []
        for reactant in reactants:
            newfunctions += reactant.functions
        newinputs = []
        for i in xrange(len(reactants)):
            #inputs in the other are offset by the size of previous things
            offset = len(newinputs)
            for inputs in reactants[i].inputs:
                inputset = []
                for j in inputs:
                    inputset.append(j+offset)
                newinputs.append(list(inputs))
        
        assert len(newstates) == sum((len(x.states) for x in reactants))
        assert len(newinputs) == sum((len(x.inputs) for x in reactants))
        assert len(newfunctions) == sum((len(x.functions) for x in reactants))
        assert len(newstates) == len(newinputs)
        assert len(newstates) == len(newfunctions)
        
        #copy bonding pattern over
        newbonding = {}
        for i in xrange(len(reactants)):
            #ensure that bonding is offset correctly
            offset = 0
            for j in xrange(i):
                offset += len(reactants[j].states)
                
            for b in reactants[i].bonding:
                newbonding[b+offset] = reactants[i].bonding[b]
        
        assert set(newbonding.keys()) <= set(xrange(len(newstates)))
            
        #now replace the last bonding site in the first and the first in the second with direct reciprocal inputs
        for i in xrange(len(reactants)-1):
        
            b1 = max(reactants[i].bonding)
            b2 = min(reactants[i+1].bonding)
            
            #add offsets
            offset = 0
            for j in xrange(i):
                offset += len(reactants[j].states)
                
            b1 += offset
            b2 += offset+len(reactants[i].states)
                            
            del newbonding[b1]
            del newbonding[b2]
            
            #print "_"*10
            #print len(newinputs)
            #print b1
            #print b2
            #print "_"*10
            
            newinputs[b1][0] = b2
            newinputs[b2][0] = b1
        
        #use the class reference so subclassing will work appropriately
        sumobj = self.__class__(newstates, newfunctions, newinputs, newbonding)
        
        return sumobj       
    
    def update(self, states):
        #given a set of states, get the next state 
        #this does not use self.states so that 
        # A) it can be repeated without creating lots
        #    of custom objects
        # B) it can be called without modifying the original
        #    e.g. to map the basins of attraction
        
        #this may need optimizing, it will get called a LOT
        n = len(self.functions)
        nextstates = [None]*n
        for i in xrange(n):
            input1 = self.inputs[i][0]
            input2 = self.inputs[i][1]
            state1 = states[input1]
            state2 = states[input2]
            
            if i in self.bonding:
                state1 = self.bonding[i]                
            nextstates[i] = self.functions[i][(1*state1)+(2*state2)]
        out = tuple(nextstates)
        return out
        
    #here are several convenience functions
            
    def run_and_cycle(self):
        if self._run_and_cycle is None:
            states = self.states
            history = []
            while states not in history:
                history.append(states)
                states = self.update(states)
            i = history.index(states)
            self._run_and_cycle = (tuple(history[:i]), tuple(history[i:]))
        return self._run_and_cycle
            
    def cycle(self):
        return self.run_and_cycle()[1] 
        
    def basin(self):
        basin = {}
        import itertools
        for states in itertools.product((0,1), repeat = len(self.states)):
            nextstates = self.update(states)
            basin[states] = nextstates
        return basin
        
    @property
    def n(self):
        return len(self.states)
    
        
    def fill_l(self):
        return self.fill(min(self.bonding))
        
    def fill_r(self):
        return self.fill(max(self.bonding))
        
    def fill(self, bondingsite):
        assert bondingsite in self.bonding
        if self.bonding[bondingsite] == 1:
            return self
        bonding = dict(self.bonding)
        bonding[bondingsite] = 1
        return self.__class__(self.states, self.functions, self.inputs, bonding)
    
        
    def empty_l(self):
        return self.empty(min(self.bonding))
        
    def empty_r(self):
        return self.empty(max(self.bonding))
        
    def empty(self, bondingsite):
        assert bondingsite in self.bonding
        if self.bonding[bondingsite] == 0:
            return self
        bonding = dict(self.bonding)
        bonding[bondingsite] = 0
        return self.__class__(self.states, self.functions, self.inputs, bonding)
    
        
    def flip_l(self):
        return self.flip(min(self.bonding))
        
    def flip_r(self):
        return self.flip(max(self.bonding))
        
    def flip(self, bondingsite):
        assert bondingsite in self.bonding
        bonding = dict(self.bonding)
        if bonding[bondingsite] == 0:
            bonding[bondingsite] = 1
        else:
            bonding[bondingsite] = 0
        return self.__class__(self.states, self.functions, self.inputs, bonding)
        
import array
class rbnarray(rbn):
    __slots__ = rbn.__slots__
        
    def __init__(self, *args, **kwargs):
        super(rbnarray, self).__init__(*args, **kwargs)
        self._states = array.array('H', self._states) #unsigned short
        
    @property
    def states(self):
        return self._states
        
    def __hash__(self):
        if self._hash is None:
            self._hash = hash(hash(tuple(self.states))+hash(self.functions)+hash(self.inputs))
        return self._hash

    def update(self, states):
        #given a set of states, get the next state 
        #this does not use self.states so that 
        # A) it can be repeated without creating lots
        #    of custom objects
        # B) it can be called without modifying the original
        #    e.g. to map the basins of attraction
        
        #this may need optimizing, it will get called a LOT
        n = len(self.functions)
        nextstates = array.array('H', [0]*n)
        for i in xrange(n):
            input1 = self.inputs[i][0]
            input2 = self.inputs[i][1]
            state1 = states[input1]
            state2 = states[input2]
            
            if i in self.bonding:
                state1 = self.bonding[i]                
            nextstates[i] = self.functions[i][state1+(2*state2)]
        return nextstates
        
    def run_and_cycle(self):
        states = self.states
        history = []
        
        inputs = self.inputs
        bonding = self.bonding
        functions = self.functions
        
        while states not in history:
            history.append(states)
            
            n = len(self.functions)
            nextstates = array.array('H', [0]*n)
            for i in xrange(n):
                input1 = inputs[i][0]
                input2 = inputs[i][1]
                state1 = states[input1]
                state2 = states[input2]
                
                if i in bonding:
                    state1 = bonding[i]                
                nextstates[i] = functions[i][state1+(2*state2)]
                
            states = nextstates
            
        i = history.index(states)
        return tuple(history[:i]), tuple(history[i:])
