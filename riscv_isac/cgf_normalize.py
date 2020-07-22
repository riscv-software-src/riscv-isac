def twos(val,bits):
    if isinstance(val,str):
        if '0x' in val:
            val = int(val,16)
        else:
            val = int(val,2)
    if (val & (1 << (bits - 1))) != 0:
        val = val - (1 << bits)
    return val

def walking_ones(var, size,signed=True):
    if not signed:
        dataset = [1 << exp for exp in range(size)]
    else:
        dataset = [twos(1 << exp,size) for exp in range(size)]
    coverpoints = [var + ' == ' + str(d) for d in dataset]
    return coverpoints

def walking_zeros(var, size,signed=True):
    mask = 2**size -1
    if not signed:
        dataset = [(1 << exp)^mask for exp in range(size)]
    else:
        dataset = [twos((1 << exp)^mask,size) for exp in range(size)]
    coverpoints = [var + ' == ' + str(d) for d in dataset]
    return coverpoints

def expand_cgf(cgf, xlen):
    for labels, cats in cgf.items():
        if labels != 'datasets':
            for label,node in cats.items():
                if 'abstract_comb' in node:
                    temp = cgf[labels][label]['abstract_comb']
                    del cgf[labels][label]['abstract_comb']
                    for coverpoints, coverage in temp.items():
                            if 'walking' in coverpoints:
                                exp_cp = eval(coverpoints)
                                for e in exp_cp:
                                    cgf[labels][label][e] = coverage
    return cgf


