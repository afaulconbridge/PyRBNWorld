"""
Some utilities and tools for using RBNWorld with other libraries, e.g. PyAChemKit

"""



def sufficiently_similar(mols, proportion = 0.5):
    """
    Function for determining if a collection of molecules is sufficiently similar.
    """
    def simplify(mol):
        for x in "123456789[]":
            mol = mol.replace(x, "")
        return mol
        
    mols = [simplify(mol) for mol in sorted(set(mols))]
    i = len(long_subseq(mols))
    j = max((len(x) for x in mols))
    #print mols, i
    if i >= proportion*j:
        return True
    else:
        return False
