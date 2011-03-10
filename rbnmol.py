import rbn as RBN

class rbnmol(object):
    #this isnt so much a molecule as a moleucle, functional group, or atom
    #each rbnmol contains references to the rbnmols it is composed of (if applicable)

    #defined here so __new__ and __init__ know which has been called
    #composition is the smaller bRBNs that we are made of
    composition = None
    #composing is the larger bRBN that we are part of
    composing = None
    rbn = None
    
    #this is a class list of all different
    #atomic rbn structures for naming of
    #elementals for string representation
    elements = []
    #and this stores rbn states of previously named structured
    #so new ones can have a new number
    _namecache = {}
    
    
    def test(self):
        assert self.rbn is not None
        if self.composing is not None:
            assert self in self.composing.composition
            #check equivalence of bonding sites

    @classmethod
    def generate(cls, n, seed=None, rng = None):
        #both seed AND rng being specified makes no sense
        assert seed is None or rng is None
        rbn = RBN.rbn.generate(n, seed, rng, b=2)
        return cls(rbn)
    
    @classmethod
    def from_genome(cls, b=0):
        rbn = RBN.rbn.from_genome(n, genome, b=2)
        return cls(rbn)
    
    def __init__(self, rbn, composition = None):
        #if we dont have an rbn, we can make one if we are a composite
        if rbn is None:
            assert composition is not None
            assert self not in composition
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
                
        self.rbn = rbn
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
        return self.rbn == other.rbn and self.composition == other.composition
        
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
                
        
    def decomposition(self, test_bonding):
        #no bonds to check, cant decompose
        if self.composition is None:
            return (self,)
            
        newcomp = [[self.composition[0]]]
        for i in xrange(len(self.composition)-1):
            this = self.composition[i]
            that = self.composition[i+1]
            #bond is good, add to new composition
            if test_bonding(this, that):
                newcomp[-1].append(that)
            #bond is bad, change new composition
            else:
                newcomp.append([that])
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
                if i != 0:
                    part = [part[0].empty_all_bonding("l")] + part[1:] 
                if i != len(newcomp)-1:
                    part = part[:-1] + [part[-1].empty_all_bonding("r")] 
                #get old state
                #TODO
                    
                newmol = self.__class__(None, part)
                
                toreturn.append(newmol)
                
            #empty bonding sites
            #between components
                
        #need to repeat check for decomposition of those newly formed things
        complete = []
        for mol in toreturn:
            if mol is self:
                complete.append(mol)
            else:
                for thing in mol.decomposition(test_bonding):
                    complete.append(thing)
        
        return tuple(complete)
            
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
            
       
    def __deepcopy__(self, memo={}):
        if self.composition is None:
            newcomposition = None
        else:
            newcomposition = []
            for x in self.composition:
                if x not in memo:
                    memo[x] = copy.deepcopy(x)
                newcomposition.append(memo[x])
                    
        copy = self.__class__(self.rbn, newcomposition)
        return copy
                
            
if __name__=="__main__":
    #some temporary test stuff
    A = rbnmol.generate(10, 1)
    B = rbnmol.generate(10, 2)
    C = rbnmol.generate(10, 3)
    AB = A.extend(B)
    print "===", AB
    AB_C = AB.extend(C)
    print "===", AB_C
    ABC = AB.composition[1].extend(C)
    print "===", ABC
    D = rbnmol.generate(10,4)
    D_AB_C = D.extend(AB_C.composition[0])
    print "===", D_AB_C
    E = rbnmol.generate(10, 5)
    DE = D.extend(E)
    DE_AB_C = DE.composition[-1].extend(AB_C.composition[0])
    print "===", DE_AB_C
    DE_AB__C = DE.composition[-1].extend(AB_C.composition[0].composition[0])
    print "===", DE_AB__C
    F = rbnmol.generate(10, 6)
    F_DE = F.extend(DE)
    F__DE_AB__C = F_DE.composition[-1].composition[-1].extend(AB_C.composition[0].composition[0])
    print "===", F__DE_AB__C
    G = rbnmol.generate(10, 7)
    H = rbnmol.generate(10, 8)
    AB_C__G = AB_C.extend(G)
    H__F_DE = H.extend(F_DE)
    print H__F_DE.composition[-1].composition[-1].composition[-1]
    print AB_C__G.composition[0].composition[0].composition[0]
    H__F_DEAB_C__G = H__F_DE.composition[-1].composition[-1].composition[-1].extend(AB_C__G.composition[0].composition[0].composition[0])
    print H__F_DE.composition[-1].composition[-1].extend(AB_C__G.composition[0].composition[0])
    print "===", H__F_DEAB_C__G
    
