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
    
    #def __init__(self, rbn, composition=None):
    #    return super(self, rbnmol_cached).__init__(self, rbn, composition)
    
    _instances = {}
    
    def __new__(cls, rbn, composition=None):
        key = (rbn, composition)
        if key not in cls._instances:
            new = rbnmol.rbnmol.__new__(cls, rbn, composition)
            cls._instances[key] = new
        return cls._instances[key] 
        #This has problems when instances are created and then changed. 
        #That happens a few times, for flipping and extending and such
        #Need to fix the underlying code so that doesnt happn, not
        #sure how though - it was fiddly enough the first time...
    
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


class rbnmol_cached_total_sumzero(rbnmol_cached):
    bonding_score = rbnmol.total
    bonding_criterion = rbnmol.sumzero                    
