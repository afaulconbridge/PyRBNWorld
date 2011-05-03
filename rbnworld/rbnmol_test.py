import rbnworld

def some_tests():
    atoms = [rbnworld.rbnmol.rbnmol_total_sumzero.generate(i) for i in xrange(100)]
    for atom in atoms:
        atom.bonding_score()
        atom.bonding_criterion(atom)
