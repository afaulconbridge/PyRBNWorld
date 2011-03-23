import rbn as RBN

#this is the core of all RBNMol objects
class rbnmol(object):
    #this isnt just a molecule but also a functional group, or atom
    #each rbnmol contains references to the rbnmols it is 
    #composed of (if applicable) as well as references to the
    #rbnmol it is composing (if applicable)

    #composition is the smaller bRBNs that we are made of
    composition = None
    #composing is the larger bRBN that we are part of
    composing = None
    #bRBN representation
    rbn = None
    
    #this is a class list of all different
    #atomic rbn structures for naming of
    #elementals for string representation
    elements = []
    #and this stores rbn states of previously named structures
    #so new ones can have a new number
    _namecache = {}
    
    @classmethod
    def generate(cls, n, seed=None, rng = None):
        #both seed AND rng being specified makes no sense
        assert seed is None or rng is None
        rbn = RBN.rbn.generate(n, seed, rng, b=2)
        return cls(rbn)
    
    @classmethod
    def from_genome(cls, genome):
        rbn = RBN.rbn.from_genome(n, genome, b=2)
        return cls(rbn)
    
    def __init__(self, rbn, composition = None):
        
        #if we dont have an rbn, we can make one if we are a composite
        if rbn is None:
            assert composition is not None
            #can have compositions of length one temporarilly
            #to extend other ones with
            #assert len(composition) > 1
            for other in composition:
                assert other.rbn.n > 0 
            
            rbn = composition[0].rbn
            for other in composition[1:]:
                rbn = rbn+other.rbn
                            
        elif composition is not None:
            testrbn = composition[0].rbn
            for other in composition[1:]:
                testrbn = testrbn+other.rbn
            #states can be different when extending
            #bonding can be different due to only
            #filling some levels of the composite
            assert testrbn.inputs == rbn.inputs
            assert testrbn.functions == rbn.functions
            
        assert len(rbn.bonding) == 2
        
        #move rbn to be the start of the cycle
        self.rbn = rbn
        self.rbn = self.rbncyclestate()
        
        
        if composition is not None:
            #doesnt have to be this way but for the moment this
            #is a good thing to check stupid bugs havnt crept in
            #print "__init__"
            #print composition
            #print self.rbn.bonding
            #print [x.rbn.bonding for x in composition]
            for component in composition:
                assert component.__class__ is self.__class__
                if component is not composition[0]:
                    assert component.rbn.bonding[min(component.rbn.bonding)] == 1, [component, composition]
                if component is not composition[-1]:
                    assert component.rbn.bonding[max(component.rbn.bonding)] == 1, [component, composition]
                
            #make a new copy of all our composing parts
            self.composition = tuple((self.__class__(x.rbn, x.composition) for x in composition))
            #point the new copies to have self as a parent
            for x in self.composition:
                assert x.composing is None
                x.composing = self
        else:
            #self is an element, add it to the element list for naming
            if (self.rbn.functions, self.rbn.inputs) not in self.elements:
                self.elements.append((self.rbn.functions, self.rbn.inputs))
    
    @property
    def size(self):
        if self.composition is None:
            return 1
        else:
            return sum((x.size for x in self.composition))
        
    def __str__(self):
        if self.composition is not None:
            tostr = "{"
            for i in xrange(len(self.composition)):
                tostr = tostr+str(self.composition[i])
                #if i is not len(self.composition)-1:
                #    tostr = tostr+"-"
            tostr = tostr+"}"
        else:
            i = self.elements.index((self.rbn.functions, self.rbn.inputs))
            name = ""
            while i > 26:
                name += "abcdefghijklmnopqrstuvwxyz"[i%26]
                #make sure it is integer division
                i = int(i/26)
            name += "abcdefghijklmnopqrstuvwxyz"[i%26]
            tostr = name.capitalize()
            
        #get the number of this state
        if tostr not in self._namecache:
            self._namecache[tostr] = []
        if self.rbn not in self._namecache[tostr]:
            self._namecache[tostr].append(self.rbn)
        stateno = self._namecache[tostr].index(self.rbn) + 1
        tostr = tostr+str(stateno)
        
        #add bonding state to the representation
        if self.rbn.bonding[min(self.rbn.bonding)] == 1:
            tostr = "-"+tostr
        if self.rbn.bonding[max(self.rbn.bonding)] == 1:
            tostr = tostr+"-"
        
        return tostr
    
    def __repr__(self):
        #hackily return string representation
        return str(self)
    
    def __hash__(self):
        return hash(self.rbn)+hash(self.composition)
        
    def __eq__(self, other):
        if other is None:
            return False
        if other is self:
            return True
        assert self.rbn is not None
        assert other.rbn is not None
        toreturn = ((self.rbn == other.rbn) and (self.composition == other.composition))
        if toreturn:
            assert hash(self) == hash(other)
        assert toreturn == (repr(self) == repr(other))
        return toreturn
        
    def __getstate__(self):
        return self.composing, self.composition, self.rbn
        
    def __setstate__(self, state):
        self.composing = state[0]
        self.composition = state[1]
        self.rbn = state[2]
        
    def top_steps(self):
        upsteps = 0
        top = self
        while top.composing is not None:
            top = top.composing
            upsteps +=1
        return (top, upsteps)
        
    def drill(self, side, steps):
        assert side in ("r", "l")
        assert steps >= 0
        if steps > 0:
            if side == "r":
                return self.composition[-1].drill(side, steps-1)
            elif side == "l":
                return self.composition[0].drill(side, steps-1)
        return self
            
            
    
    def rbncyclestate(self):
        #this is the first state on the cycle
        #this means that x.cyclestate().cyclestate() is the same as x.cyclestate() in all cases
        #if it was the last state on the cycle, it would move around the cycle backwards!
        if self.rbn.cycle()[0] != self.rbn.states:
            newrbn = self.rbn.__class__(self.rbn.cycle()[0], self.rbn.functions, self.rbn.inputs, self.rbn.bonding)
            assert newrbn.cycle()[0] == newrbn.states
            return newrbn
        else:
            return self.rbn
            
    def fill_all_bonding(self, side):
        return self.set_all_bonding(side, 1)
        
    def empty_all_bonding(self, side):
        return self.set_all_bonding(side, 0)
        
    def set_all_bonding(self, side, state):
        assert side in ("r", "l")
        assert state in (1, 0, -1)
        if self.composing is not None:
            assert self in self.composing.composition
            if side == "r":
                assert self is self.composing.composition[-1]
            elif side == "l":
                assert self is self.composing.composition[0]
        #anything we are composed of should also have its bonding site filled
        #anything we are composing should also have its bonding site filled
        
        #to do it, go up to the top, then fill all the way to the bottom.
        top, upsteps = self.top_steps()

        #create a copy and then flip the relevant rbns in that
        toreturn = self.__class__(top.rbn, top.composition)
        top = toreturn
        
        while top is not None:
            if side == "r" and state == 1:
                top.rbn = top.rbn.fill_r()
            elif side == "r" and state == 0:
                top.rbn = top.rbn.empty_r()
            elif side == "r" and state == -1:
                top.rbn = top.rbn.flip_r()
            elif side == "l" and state == 1:
                top.rbn = top.rbn.fill_l()
            elif side == "l" and state == 0:
                top.rbn = top.rbn.empty_l()
            elif side == "l" and state == -1:
                top.rbn = top.rbn.flip_l()
            else:
                assert False
                
            if top.composition is None:
                top = None
            else:
                if side == "r":
                    top = top.composition[-1]
                elif side == "l":
                    top = top.composition[0]
                    
        downsteps = 1
        while downsteps < upsteps-1:
            if side == "r":
                toreturn = toreturn.composition[-1]
            elif side == "l":
                toreturn = toreturn.composition[0]
            downsteps += 1
                
        return toreturn
        
    def fill_this_bonding(self, side):
        return self.set_this_bonding(side, 1)
    def empty_this_bonding(self, side):
        return self.set_this_bonding(side, 0)
    def flip_this_bonding(self, side):
        return self.set_this_bonding(side, -1)
        
    def set_this_bonding(self, side, state):
        assert side in ("r", "l")
        assert state in (1, 0, -1)
        
        #to do it, go up to the top to make a copy
        top, upsteps = self.top_steps()
            
        #create a copy and then flip the relevant rbn in that
        toreturn = self.__class__(top.rbn, top.composition)
        top = toreturn
                    
        downsteps = 0
        while downsteps < upsteps:
            if side == "r":
                toreturn = toreturn.composition[-1]
            elif side == "l":
                toreturn = toreturn.composition[0]
            downsteps += 1
            
        if side == "r" and state == 1:
            toreturn.rbn = toreturn.rbn.fill_r()
        elif side == "r" and state == 0:
            toreturn.rbn = toreturn.rbn.empty_r()
        elif side == "r" and state == -1:
            toreturn.rbn = toreturn.rbn.flip_r()
        elif side == "l" and state == 1:
            toreturn.rbn = toreturn.rbn.fill_l()
        elif side == "l" and state == 0:
            toreturn.rbn = toreturn.rbn.empty_l()
        elif side == "l" and state == -1:
            toreturn.rbn = toreturn.rbn.flip_l()
        else:
            assert False
                
        return toreturn
        
        
    def extend(self, other):
        cls = self.__class__
        #make them both to be the same top levels
        #need to record how many were added to each side to count back down later
        added = 0
        while not (self.composing is None and other.composing is None):
            if self.composing is not None and other.composing is not None:
                self = self.composing
                other = other.composing
            if self.composing is not None and other.composing is None:
                self = self.composing
                other = cls(other.rbn, (other,))
            elif self.composing is None and other.composing is not None:
                self = cls(self.rbn, (self,))                    
                other = other.composing
            #need to record how many were added to each side to count back down later   
            added += 1
        
        #need to count back down so that this and that point to the new datastructure
        #where both have equal number of layers
        this = self
        that = other
        while added > 0:
            added -= 1
            this = this.composition[-1]
            that = that.composition[0]
        
        #at this point, self and other
        #are both the top-level bRBNs
        #and both have sufficient levels
        if this is self and that is other:
            #if neither of them are composing larger ones
            #can simply create a new larger bRBN
            toreturn =  cls(None, (self, other))
        else:
            assert this.composing is not None
            assert that.composing is not None   
            #zip together from the lowest level upwards
            toreturn = cls(None, this.composing.composition + that.composing.composition)
            newstates = this.composing.rbn.states + that.composing.rbn.states
            assert len(newstates) == len(toreturn.rbn.states)
            toreturn.rbn.states = newstates
            #this should zip up multiple levels of molecule
            while this.composing.composing is not None and that.composing.composing is not None:
                #get the new state to use before constructing the new toreturn
                newstatesa = this.composing.composing.rbn.states[:-len(this.composing.composing.composition[-1].rbn.states)]
                newstatesb = toreturn.rbn.states
                newstatesc = that.composing.composing.rbn.states[len(that.composing.composing.composition[0].rbn.states):]
                newstates = newstatesa + newstatesb + newstatesc 
                assert this.composing is not that.composing
                assert this.composing.composing is not that.composing.composing
                
                toreturn = cls(None, this.composing.composing.composition[:-1] + (toreturn,) + that.composing.composing.composition[1:])
                assert len(newstates) == len(toreturn.rbn.states), [len(newstates), len(toreturn.rbn.states), len(newstatesa), len(newstatesb), len(newstatesc)]
                toreturn.rbn.states = newstates
                
                
                this = this.composing
                that = that.composing
        return toreturn
                
        
    def decomposition(self):
        #no bonds to check, cant decompose
        if self.composition is None:
            return (self,)
            
        newcomp = []
        this = self.composition[0]
        #first component is never a "that"
        #so test it here
        newthis = this.decomposition()
        if len(newthis) > 1:
            for thing in newthis:
                newcomp.append([thing])
        else:
            newcomp.append([this])
        #test each component that is bonded to
        for i in xrange(len(self.composition)-1):
            this = self.composition[i]
            that = self.composition[i+1]
            newthat = that.decomposition()
            if len(newthat) > 1:
                #that decomposed on its own
                #use newthat to test the bonds

                
                #bond is good, add to new composition
                if this.bonding_criterion(that):
                    newcomp[-1].append(newthat[0])
                    for thing in newthat[1:]:
                        newcomp.append([thing])
                #bond is bad, change new composition
                else:
                    for thing in newthat:
                        newcomp.append([thing])
            else:
                #newthat is no different from that
                #therefore use that instead
                
                #bond is good, add to new composition
                if this.bonding_criterion(that):
                    newcomp[-1].append(that)
                #bond is bad, change new composition
                else:
                    newcomp.append([that])
        assert len(newcomp) > 0
        #if we have the same composition afterwards
        #nothing broke and we can use ourselves
        if len(newcomp) == 1:
            assert tuple(newcomp[0]) == self.composition
            toreturn = [self]
        else:
            #one or more of our bonds broke
            #convert each component into a new bRBN
            toreturn = []
            for i in xrange(len(newcomp)):
                part = newcomp[i]
                assert len(part) > 0
                part = [self.__class__(x.rbn, x.composition) for x in part]
                #empty bonding sites
                #between components
                if i != 0:
                    part = [part[0].empty_all_bonding("l")] + part[1:] 
                if i != len(newcomp)-1:
                    part = part[:-1] + [part[-1].empty_all_bonding("r")] 
                    
                newmol = self.__class__(None, part)
                #get old state
                offset = 0
                for mol in toreturn:
                    offset += mol.rbn.n
                partstates = self.rbn.states[offset:offset+newmol.rbn.n]
                assert len(partstates) == len(newmol.rbn.states)
                newmol.rbn.states = partstates
                
                toreturn.append(newmol)
                       
        return tuple(toreturn)
            
    def collapse(self):
        if self.composition is None:
            return self
        elif len(self.composition) == 1:
            #collapse
            self.composition[0].composing = self.composing
            if self.composing is not None:
                parent = self.composing
                newcomposition = []
                for x in parent.composition:
                    if x is self:
                        x = self.composition[0]
                    newcomposition.append(x)
                parent.composition = tuple(newcomposition)
            return self.composition[0].collapse()
                
        elif len(self.composition) > 1:
            newcomposition = tuple((x.collapse() for x in self.composition))
            if newcomposition == self.composition:
                return self
            else:
                return self.__class__(self.rbn, newcomposition).collapse()

    
#alternative AChems can, to an extent, be implemented through these functions

def total(self):
    score = 0
    for step in self.rbn.cycle():
        for state in step:
            if state == 0:
                score -= 1
            elif state == 1:
                score += 1
    return score

def sumzero(self, other):
    return self.bonding_score() + other.bonding_score() == 0.0
    
def sumzero_pm_one(self, other):
    return -1.0 < self.bonding_score() + other.bonding_score() < 1.0

#because custm class picking is a pain, dont do it
#instead create a real copy of the class somewhere in the file system and use that instead

class rbnmol_total_sumzero(rbnmol):
    bonding_score = total
    bonding_criterion = sumzero                    
