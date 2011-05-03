import rbnworld

def some_tests():
    rbns = [rbnworld.rbn.rbn.generate(10, i, b=2) for i in xrange(100)]
    for rbn in rbns:
        rbn.states
        rbn.functions
        rbn.inputs
        rbn.bonding
        rbn.n
        
        rbn.basin()
        
        run, cycle = rbn.run_and_cycle()
        
        hash(rbn)
        assert rbn == rbn
        assert hash(rbn) == hash(rbn)
        assert not rbn != rbn
        assert rbn <= rbn
        assert rbn >= rbn
        assert not rbn < rbn
        assert not rbn > rbn
        
        rbn = rbn.fill_r()
        rbn = rbn.fill_l()
        rbn = rbn.flip_r()
        rbn = rbn.flip_l()
        rbn = rbn.flip_r()
        rbn = rbn.flip_l()
        rbn = rbn.empty_r()
        rbn = rbn.empty_l()
        
    for i in xrange(len(rbns)-1):
        rbna = rbns[i]
        rbnb = rbns[i+1]
        rbnc = rbna + rbnb
        
