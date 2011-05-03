import weakref
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
    
    __slots__ = rbnmol.rbnmol.__slots__+["_collapse", "_decomposition", "_set_all_bonding", "_set_this_bonding", "_extend", "_rbntree"]
    
    _generate = {}
    _seen = {}
    _from_genome = {}
    
    
    def __new__(cls, rbn = None, composition = None, collapse = False):
        return rbnmol.rbnmol.__new__(cls, rbn, composition, collapse)
    
    def __init__(self, rbn = None, composition = None, collapse = False):
        super(rbnmol_cached, self).__init__(rbn, composition, collapse)
        self._collapse = None
        self._decomposition = None
        self._set_all_bonding = None
        self._set_this_bonding = None
        self._extend = None
        self._rbntree = None
    
    @classmethod
    def seen(cls, mol):
        return mol
        if mol.composing is not None:
            return mol
        if mol in cls._seen:
            return cls._seen[mol]
        else:
            cls._seen[mol] = mol
            return mol
    
    @classmethod
    def generate(cls, n, seed = None, rng = None):
        if rng is not None:
            return super(rbnmol_cached, cls).generate(n, seed, rng)
            
        key = (n, seed)
        if key not in cls._generate:
            cls._generate[key] = super(rbnmol_cached, cls).generate(n, seed)
            
        return cls._generate[key]
    
    @classmethod
    def from_genome(cls, genome):
        if genome not in cls._from_genome:
            cls._from_genome[genome] = super(rbnmol_cached, cls).from_genome(genome)
        return cls._from_genome[genome]
        
    def collapse(self):
        if self._collapse is None:
            mol = super(rbnmol_cached, self).collapse()
            self._collapse = mol
        assert self._collapse.atomstr() == self.atomstr()
        return self._collapse
        
    def decomposition(self):
        if self._decomposition is None:
            mols = super(rbnmol_cached, self).decomposition()
            mols = [self.seen(x) for x in mols]
            self._decomposition = mols
            
        assert "".join((x.atomstr() for x in self._decomposition)) == self.atomstr()
        return self._decomposition
    """
        
    def set_all_bonding(self, side, state):
        if self._set_all_bonding is None:
            self._set_all_bonding = {}#weakref.WeakKeyDictionary()
        key = (side, state)
        if key not in self._set_all_bonding:
            mol = super(rbnmol_cached, self).set_all_bonding(side, state)
            mol = self.seen(mol)
            self._set_all_bonding[key] = mol
        assert self._set_all_bonding[key].atomstr() == self.atomstr(), [self._set_all_bonding[key].atomstr(), self.atomstr()]
        return self._set_all_bonding[key]
        
    def set_this_bonding(self, side, state):
        if self._set_this_bonding is None:
            self._set_this_bonding = {}#weakref.WeakKeyDictionary()
        key = (side, state)
        if key not in self._set_this_bonding:
            mol = super(rbnmol_cached, self).set_this_bonding(side, state)
            mol = self.seen(mol)
            self._set_this_bonding[key] = mol
        assert self._set_this_bonding[key].atomstr() == self.atomstr()
        return self._set_this_bonding[key]
        
    def extend(self, other):
        if self._extend is None:
            self._extend = {}#weakref.WeakKeyDictionary()
        key = other
        if key not in self._extend:
            mol = super(rbnmol_cached, self).extend(other)
            mol = self.seen(mol)
            self._extend[key] = mol
        return self._extend[key]
    """
    
        
    @property
    def rbntree(self):
        if self._rbntree is None:
            self._rbntree = super(rbnmol_cached, self).rbntree
        return self._rbntree

class rbnmol_cached_total_sumzero(rbnmol_cached):
    __slots__ = rbnmol_cached.__slots__
    bonding_score = rbnmol.total
    bonding_criterion = rbnmol.sumzero                  
