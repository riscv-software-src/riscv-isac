# See LICENSE.incore for details
from math import *

def twos(val,bits):
    '''
    Finds the twos complement of the number
    :param val: input to be complemented
    :param bits: size of the input

    :type val: str or int
    :type bits: int

    :result: two's complement version of the input

    '''
    if isinstance(val,str):
        if '0x' in val:
            val = int(val,16)
        else:
            val = int(val,2)
    if (val & (1 << (bits - 1))) != 0:
        val = val - (1 << bits)
    return val

def walking_ones(var, size, signed=True, fltr_func=None, scale_func=None):
    '''
    This function converts an abstract walking-ones function into individual
    coverpoints that can be used by ISAC. The unrolling of the function accounts
    of the size, sign-bit, filters and scales. The unrolled coverpoints will
    contain a pattern a single one trickling down from LSB to MSB. The final
    coverpoints can vary depending on the filtering and scaling functions

    :param var: input variable that needs to be assigned the coverpoints
    :param size: size of the bit-vector to generate walking-1s
    :param signed: when true indicates that the unrolled points be treated as signed integers.
    :param fltr_func: a lambda function which defines a filtering routine to keep only a certain values from the unrolled coverpoints
    :param scale_func: a lambda function which defines the scaling that should be applied to the unrolled coverpoints that have been generated.

    :type var: str
    :type size: int
    :type signed: bool
    :type fltr_func: function
    :type scale_func: function
    :result: dictionary of unrolled filtered and scaled coverpoints
    '''
    if not signed:
        dataset = [1 << exp for exp in range(size)]
    else:
        dataset = [twos(1 << exp,size) for exp in range(size)]
    if scale_func:
        dataset = [scale_func(x) for x in dataset]
    if fltr_func:
        dataset = filter(fltr_func,dataset)
    coverpoints = [var + ' == ' + str(d) for d in dataset]
    return coverpoints

def walking_zeros(var, size,signed=True, fltr_func=None, scale_func=None):
    '''
    This function converts an abstract walking-zeros function into individual
    coverpoints that can be used by ISAC. The unrolling of the function accounts
    of the size, sign-bit, filters and scales. The unrolled coverpoints will
    contain a pattern a single zero trickling down from LSB to MSB. The final
    coverpoints can vary depending on the filtering and scaling functions

    :param var: input variable that needs to be assigned the coverpoints
    :param size: size of the bit-vector to generate walking-1s
    :param signed: when true indicates that the unrolled points be treated as signed integers.
    :param fltr_func: a lambda function which defines a filtering routine to keep only a certain values from the unrolled coverpoints
    :param scale_func: a lambda function which defines the scaling that should be applied to the unrolled coverpoints that have been generated.

    :type var: str
    :type size: int
    :type signed: bool
    :type fltr_func: function
    :type scale_func: function
    :result: dictionary of unrolled filtered and scaled coverpoints
    '''
    mask = 2**size -1
    if not signed:
        dataset = [(1 << exp)^mask for exp in range(size)]
    else:
        dataset = [twos((1 << exp)^mask,size) for exp in range(size)]
    if scale_func:
        dataset = [scale_func(x) for x in dataset]
    if fltr_func:
        dataset = filter(fltr_func,dataset)
    coverpoints = [var + ' == ' + str(d) for d in dataset]
    return coverpoints

def alternate(var, size, signed=True, fltr_func=None,scale_func=None):
    '''
    This function converts an abstract alternate function into individual
    coverpoints that can be used by ISAC. The unrolling of the function accounts
    of the size, sign-bit, filters and scales. The unrolled coverpoints will
    contain a pattern of alternating 1s and 0s. The final
    coverpoints can vary depending on the filtering and scaling functions

    :param var: input variable that needs to be assigned the coverpoints
    :param size: size of the bit-vector to generate walking-1s
    :param signed: when true indicates that the unrolled points be treated as signed integers.
    :param fltr_func: a lambda function which defines a filtering routine to keep only a certain values from the unrolled coverpoints
    :param scale_func: a lambda function which defines the scaling that should be applied to the unrolled coverpoints that have been generated.

    :type var: str
    :type size: int
    :type signed: bool
    :type fltr_func: function
    :type scale_func: function

    :result: dictionary of unrolled filtered and scaled coverpoints
    '''
    t1 =( '' if size%2 == 0 else '1') + ''.join(['01']*int(size/2))
    t2 =( '' if size%2 == 0 else '0') + ''.join(['10']*int(size/2))
    if not signed:
        dataset = [int(t1,2),int(t2,2)]
    else:
        dataset = [twos(t1,size),twos(t2,size)]
    if scale_func:
        dataset = [scale_func(x) for x in dataset]
    if fltr_func:
        dataset = filter(fltr_func,dataset)
    coverpoints = [var + ' == ' + str(d) for d in dataset]
    return coverpoints

def expand_cgf(cgf, xlen):
    '''
    This function will replace all the abstract functions with their unrolled
    coverpoints

    :param cgf: input cgf yaml
    :param xlen: XLEN of the riscv-trace

    :type cgf: dict
    :type xlen: int
    '''
    for labels, cats in cgf.items():
        if labels != 'datasets':
            for label,node in cats.items():
                if isinstance(node,dict):
                    if 'abstract_comb' in node:
                        temp = cgf[labels][label]['abstract_comb']
                        del cgf[labels][label]['abstract_comb']
                        for coverpoints, coverage in temp.items():
                                if 'walking' in coverpoints or 'alternate' in coverpoints:
                                    exp_cp = eval(coverpoints)
                                    for e in exp_cp:
                                        cgf[labels][label][e] = coverage
    return cgf


