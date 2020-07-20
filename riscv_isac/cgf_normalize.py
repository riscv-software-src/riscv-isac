import copy
def walking_ones(var, size):
    dataset = [1 << exp for exp in range(size)]
    coverpoints = [var + ' == ' + str(hex(d)) for d in dataset]
    return coverpoints

def walking_zeros(var, size):
    mask = hex(2**size -1)
    dataset = [(1 << exp)^(2**size -1) for exp in range(size)]
    coverpoints = [var + ' == ' + str(hex(d)) for d in dataset]
    return coverpoints

def expand_cgf(cgf, xlen):
    new_cgf = copy.deepcopy(cgf)
    for labels, cats in cgf.items():
        if labels != 'datasets':
            if 'abstract_comb' in cats:
                for coverpoints, coverage in cats['abstract_comb'].items():
                        if 'walking' in coverpoints:
                            del new_cgf[labels]['abstract_comb'][coverpoints]
                            exp_cp = eval(coverpoints)
                            for e in exp_cp:
                                new_cgf[labels]['abstract_comb'][e] = coverage
    return new_cgf 


