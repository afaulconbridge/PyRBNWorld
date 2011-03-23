import rbnmol

class rbnmol_cached(rbnmol.rbnmol):
    """
    Subclass of rbnmol but one where all returned objects are stored
    
    This may lead to huge memory requirements, but might offer speed 
    increases. Only way to find out is implement both...
    
    It might be woth putting some sort of weak-referncing system in place
    so things that can be regenerated can be disposed of when memory
    gets low. However, AFAIK the python weak-reference system does
    not do this.
    
    This caching will only work for deterministic molecules, or deterministic
    classes of non-determinisitc molecules.
    """
    
    _generate = {}
    
    @classmethod
    def generate(cls, n, seed = None, rng = None):
        if rng is not None:
            return super(rbnmol_cached, cls).generate(n, seed, rng)
            
        key = (n, seed)
        if key not in cls._generate:
            cls._generate[key] = super(rbnmol_cached, cls).generate(n, seed)
        return cls._generate[key]
    
    _from_genome = {}
    
    @classmethod
    def from_genome(cls, genome):
        if genome not in cls._from_genome:
            cls._from_genome[genome] = super(rbnmol_cached, cls).from_genome(genome)
        return cls._from_genome[genome]
    
    _collapse = None
    
    def collapse(self):
        if self._collapse is None:
            self._collapse = super(rbnmol_cached, self).collapse()
        return self._collapse
    
    _decomposition = None
    
    def decomposition(self):
        if self._decomposition is None:
            self._decomposition = super(rbnmol_cached, self).decomposition()
        return self._decomposition

    _set_all_bonding = {}
    
    def set_all_bonding(self, side, state):
        key = (self, side, state)
        if key not in self._set_all_bonding:
            self._set_all_bonding[key] = super(rbnmol_cached, self).set_all_bonding(side, state)
        return self._set_all_bonding[key]
        
    _set_this_bonding = {}
    
    def set_this_bonding(self, side, state):
        key = (self, side, state)
        if key not in self._set_this_bonding:
            self._set_this_bonding[key] = super(rbnmol_cached, self).set_this_bonding(side, state)
        return self._set_this_bonding[key]
        
        
    _extend = {}
    
    def extend(self, other):
        key = (self, other)
        if key not in self._extend:
            self._extend[key] = super(rbnmol_cached, self).extend(other)
        return self._extend[key]
        
        


class rbnmol_cached_total_sumzero(rbnmol_cached):
    bonding_score = rbnmol.total
    bonding_criterion = rbnmol.sumzero                    
