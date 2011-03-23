import rbnmol

def decompose(*mols):
    assert len(mols) > 0
    if len(mols) == 1:
        newmols = mols[0].decomposition()
    else:
        newmols = []
        for mol in mols:
            for outmol in decompose(mol):
                newmols.append(outmol)
    assert len(newmols) > 0
    newmols = tuple(newmols)
    if newmols != mols:
        return decompose(*newmols)
    else:
        return mols
        
def validate(mol):
    if mol.composing is None:
        #top level, can drill through it checking bonding sites
        assert 1 not in mol.rbn.bonding.values(), product
        drill = mol
        while drill.composition is not None:
            drill = drill.composition[0]
            assert drill.rbn.bonding[0] == 0, drill
        drill = mol
        while drill.composition is not None:
            drill = drill.composition[-1]
            assert drill.rbn.bonding[max(drill.rbn.bonding)] == 0, drill
    else:
        assert mol.composing.composition is not None
        assert mol in mol.composing.composition
    if mol.composition is None:
        return
    else:
        assert len(mol.composition) > 1
        for test in mol.composition:
            validate(test)
    

def reaction(A00, B00):
    #dont do complicated flipping-ness
    #reactions are either A+B or B+A. Assume this has
    #been done before this function.
    
    #This determines the outcome of one reaction between A and B
    #An alternative would be to determine all outcomes
    #and then pick one.

    reactants = (A00, B00)
    
    #go down to the smallest components in each one
    while A00.composition is not None:
        A00 = A00.composition[-1]
    while B00.composition is not None:
        B00 = B00.composition[0]
        
    reacting = False
    while reacting is False:
        #if these can react, react
        if A00.bonding_criterion(B00):
            reacting = True
        else:
            if A00.composing is None and B00.composing is None:
                #nothing has reacted
                #nothing is composing larger things
                #end reaction
                return reactants
            elif A00.composing is not None and B00.composing is None:
                #only one has a larger structure
                #go to the larger structure
                A00 = A00.composing
            elif A00.composing is None and B00.composing is not None:
                B00 = B00.composing
                #only one has a larger structure
                #go to the larger structure
            elif A00.composing is not None and B00.composing is not None:
                #both of them have a larger structure
                #which one do we use?
                #go for the smaller one
                if A00.composing.rbn.n < B00.composing.rbn.n:
                    #As composing structure is smaller
                    #use it
                    A00 = A00.composing
                elif A00.composing.rbn.n > B00.composing.rbn.n:
                    #Bs composing structure is smaller
                    #use it
                    B00 = B00.composing
                elif A00.composing.rbn.n == B00.composing.rbn.n:
                    #both the composing stuctures are the same size
                    #use both of them
                    A00 = A00.composing
                    B00 = B00.composing
                
    assert reacting is True
    
    #fill in bonding sites in only these bRBNs
    A01 = A00.fill_this_bonding("r")
    B10 = B00.fill_this_bonding("l")

    A01_top, upstepsA = A01.top_steps()
    B10_top, upstepsB = B10.top_steps()
    products = ((A01_top,), (B10_top,))
    
    #check nothing breaks
    products = (decompose(A01_top), decompose(B10_top))
    A01_top = products[0][-1]
    B10_top = products[-1][0]
    A01 = A01_top.drill("r", upstepsA)
    B10 = B10_top.drill("l", upstepsB)
    
    #see if bonding can continue
    if A01.bonding_criterion(B10):
        #if this is the top-most, then create a new composite and return it
        #have to do complicated extensions stuff if it is not
        #but this function will deal with that...
        A01 = A01.fill_all_bonding("r")
        B10 = B10.fill_all_bonding("l")
        C00 = A01.extend(B10)
        C00_top, upsteps = C00.top_steps()
        products = products[0][:-1]+(C00_top,)+products[1][1:]
    else:
        #need to revert the bonding process
        A00_2 = A01.empty_all_bonding("r")
        B00_2 = B10.empty_all_bonding("l")
        #get the top so it is easier to make products
        #upsteps is a consequence of this, but not needed here
        A00_top, upsteps = A00_2.top_steps()
        B00_top, upsteps = B00_2.top_steps()
        products = products[0][:-1]+(A00_top, B00_top)+products[1][1:]
        
    #check nothing breaks again
    products = decompose(*products)
    
    #collapse single compositions
    newproducts = []
    for mol in products:
        newproducts.append(mol.collapse())
    products = newproducts
        
    for product in products:
        validate(product)
            
    return tuple(products)
