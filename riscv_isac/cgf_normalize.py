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
            for label,node in cats.items():
                if 'abstract_comb' in node:
                    del new_cgf[labels][label]['abstract_comb']
                    for coverpoints, coverage in cats[label]['abstract_comb'].items():
                            if 'walking' in coverpoints:
                                exp_cp = eval(coverpoints)
                                for e in exp_cp:
                                    new_cgf[labels][label][e] = coverage
    return new_cgf


