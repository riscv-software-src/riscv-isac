# See LICENSE.incore for details
from math import *
import riscv_isac.utils as utils
import itertools
import random
import copy
from riscv_isac.fp_dataset import *

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

def sp_vals(bit_width,signed):
    if signed:
        conv_func = lambda x: twos(x,bit_width)
        sqrt_min = int(-sqrt(2**(bit_width-1)))
        sqrt_max = int(sqrt((2**(bit_width-1)-1)))
    else:
        sqrt_min = 0
        sqrt_max = int(sqrt((2**bit_width)-1))
        conv_func = lambda x: (int(x,16) if '0x' in x else int(x,2)) if isinstance(x,str) else x

    dataset = [3, "0x"+"".join(["5"]*int(bit_width/4)), "0x"+"".join(["a"]*int(bit_width/4)), 5, "0x"+"".join(["3"]*int(bit_width/4)), "0x"+"".join(["6"]*int(bit_width/4))]
    dataset = list(map(conv_func,dataset)) + [int(sqrt(abs(conv_func("0x8"+"".join(["0"]*int((bit_width/4)-1)))))*(-1 if signed else 1))] + [sqrt_min,sqrt_max]
    return dataset + [x - 1 if x>0 else 0 for x in dataset] + [x+1 for x in dataset]

def sp_dataset(bit_width,var_lst=["rs1_val","rs2_val"],signed=True):
    coverpoints = []
    datasets = []
    var_names = []
    for var in var_lst:
        if isinstance(var,tuple) or isinstance(var,list):
            if len(var) == 3:
                var_sgn = var[2]
            else:
                var_sgn = signed
            var_names.append(var[0])
            datasets.append(sp_vals(int(var[1]),var_sgn))
        else:
            var_names.append(var)
            datasets.append(sp_vals(bit_width,signed))
    dataset = itertools.product(*datasets)
    for entry in dataset:
        coverpoints.append(' and '.join([var_names[i]+"=="+str(entry[i]) for i in range(len(var_names))]))
    return [(coverpoint,"Special Dataset") for coverpoint in coverpoints]

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
    coverpoints =[]
    for d in dataset:
        coverpoints.append((var + ' == ' + str(d),'Walking Ones: '+str(hex(d))))
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
    coverpoints =[]
    for d in dataset:
        coverpoints.append((var + ' == ' + str(d),'Walking Zeros: '+str(hex(d))))
    return coverpoints

def byte_count(xlen, variables=['rs1_val','rs2_val','imm_val'], overlap = "N"):
    '''
    Test pattern 1: SBox Testing
    This uses the byte-count pattern described above.
    Generate a 256-byte sequence 0..255 and pack the sequence into 32-bit words.
    Each word in the sequence is the rs2 input. The rs1 input is set to zero so we do not alter the SBox output value.
    For each input word, generate 4 instructions, with bs=0..3.
    This will mean that every possible SBox input pattern is tested.

    :param xlen: size of the bit-vector to generate byte-count pattern
    :param variables: list of string variables indicating the operands
    :param overlap: Set "Y" to test byte-count pattern on lower word of the xlen-bit vector, else set "N".

    :type xlen: int
    :type variables: List[str]
    :type overlap: str

    '''
    rs1 = 0
    rs2 = []
    coverpoints = []
    hex_str = ""
    i=0
    cvpt = ""
    max = 255
    if overlap == "Y":
    	max += xlen/16
    while(i<=max):
    	hex_str = "{:02x}".format(i % 256) + hex_str
    	if((len(hex_str)/2)%(xlen/8) == 0):
    		rs2.append('0x'+hex_str)
    		hex_str = ""
    		if(overlap == "Y"):
    			i=int(i-(xlen/16))
    	i=i+1

    if xlen == 32:
    	for i in range(len(rs2)):
    		for j in range(4):
    			coverpoints.append(variables[0] +' == '+ str(rs1) +' and '+ variables[1] +' == '+ rs2[i] + ' and '+ variables[2] +' == '+ str(j) + ' #nosat')
    else:
    	if variables[1] == "rs2_val":
    		for i in range(len(rs2)):
    			if((i+1)%2==0):
    				y = rs2[i-1]
    				x = rs2[i]
    			else:
    				x = rs2[i]
    				y = rs2[i+1]
    			cvpt = variables[0] +' == '+ x +' and '+ variables[1] +' == '+ y
    			if len(variables)==3:
    				if variables[2] == "imm_val":
    					for j in range(4):
    						coverpoints.append(cvpt+' and imm_val == '+ str(j) + ' #nosat')
    			else:
    				coverpoints.append(cvpt + ' #nosat')
    			cvpt = ""
    	elif variables[1] == "imm_val":
    		for i in range(len(rs2)):
    			coverpoints.append(variables[0] +' == '+ rs2[i] +' and '+ variables[1] +' == 0xA' + ' #nosat')
    return [(coverpoint,"Byte Count") for coverpoint in coverpoints]

def uniform_random(N=10, seed=9, variables=['rs1_val','rs2_val','imm_val'], size=[32,32,2]):
    '''
    Test pattern 2: Uniform Random
    Generate uniform random values for rs1, rs2 and bs.
    Let register values be un-constrained: 0..31.
    Repeat N times for each instruction until sufficient coverage is reached.

    :param N: Number of random combinations to be generated
    :param seed: intial seed value of the random library
    :param variables: list of string variables indicating the operands
    :param size: list of bit-sizes of each variable defined in variables.

    :type N: int
    :type seed: int
    :type variables: List[str]
    :type size: List[int]

    '''
    random.seed(seed)

    coverpoints = []
    while N!= 0:
    	random_vals = []
    	for v in range(len(variables)):
    		val = random.randint(0,2**int(size[v])-1)
    		random_vals.append(variables[v] + \
    		' == {0:#0{1}x}'.format(val,int(size[v]/4)+2))
    	coverpoints.append((" and ".join(random_vals) + " #nosat",\
                "Uniform Random "+str(N)))
    	N = N-1

    return coverpoints

def leading_ones(xlen, var = ['rs1_val','rs2_val'], sizes = [32,32], seed = 10):
    '''
    For each variable in var, generate a random input value, and set the most-significant i bits.
    See the other rs input and set a random value.

    :param xlen: size of the bit-vector to generate leading-1s
    :param var: list of string variables indicating the operands
    :param sizes: list of sizes of the variables in var
    :param seed: intial seed value of the random library

    :type xlen: int
    :type var: List[str]
    :type sizes: List[int]
    :type seed: int
    '''
    random.seed(seed)
    coverpoints = []
    for i in range(0,len(var)):
        curr_var = var[i]
        curr_sz = sizes[i]
        default = 2**curr_sz-1
        for sz in range(0,curr_sz+1):
           cvpt = ''
           val = (default << sz) & default
           setval = (1 << sz-1) ^ default if sz!=0 else default
           val = (val | random.randrange(1,2**curr_sz)) & default & setval
           cvpt += curr_var + ' == 0x{0:0{1}X}'.format(val,int(ceil(curr_sz/4)))
           cmnt = '{1} Leading ones for {0}. Other operands are random'.\
                   format(curr_var, curr_sz-sz)
           for othervars in range(0,len(var)):
               if othervars != i:
                   otherval = random.randrange(0,2**sizes[othervars])
                   cvpt += ' and ' + var[othervars] + ' == 0x{0:0{1}X}'.format(otherval,int(ceil(sizes[othervars]/4)))
           coverpoints.append((cvpt+ " #nosat", cmnt))
    return coverpoints

def leading_zeros(xlen, var = ['rs1_val','rs2_val'], sizes = [32,32], seed = 11):
    '''
    For each rs register input, generate a random XLEN input value, and clear the most-significant i bits.
    See the other rs input, pick a random value.

    :param xlen: size of the bit-vector to generate leading-0s
    :param var: list of string variables indicating the operands
    :param sizes: list of sizes of the variables in var
    :param seed: intial seed value of the random library

    :type xlen: int
    :type var: List[str]
    :type sizes: List[int]
    :type seed: int

    '''
    random.seed(seed)
    coverpoints = []
    for i in range(0,len(var)):
        curr_var = var[i]
        curr_sz = sizes[i]
        default = 2**curr_sz-1
        for sz in range(0,curr_sz+1):
           cvpt = ''
           val = (1 << sz)-1 & default
           setval = 1 << (sz-1) if sz!=0 else 0
           val = (val & random.randrange(1,2**curr_sz)) & default | setval
           cvpt += curr_var + ' == 0x{0:0{1}X}'.format(val,int(ceil(curr_sz/4)))
           cmnt = '{1} Leading zeros for {0}. Other operands are random'.\
                   format(curr_var, curr_sz-sz)
           for othervars in range(0,len(var)):
               if othervars != i:
                   otherval = random.randrange(0,2**sizes[othervars])
                   cvpt += ' and ' + var[othervars] + ' == 0x{0:0{1}X}'.format(otherval,int(ceil(sizes[othervars]/4)))
           coverpoints.append((cvpt+ " #nosat",cmnt))
    return coverpoints


def trailing_zeros(xlen, var = ['rs1_val','rs2_val'], sizes = [32,32], seed = 12):
    '''
    For each rs register input, generate a random XLEN input value, and clear the least-significant i bits.
    See the other rs input, pick a random value.

    :param xlen: size of the bit-vector to generate trailing-0s
    :param var: list of string variables indicating the operands
    :param sizes: list of sizes of the variables in var
    :param seed: intial seed value of the random library

    :type xlen: int
    :type var: List[str]
    :type sizes: List[int]
    :type seed: int

    '''
    random.seed(seed)
    coverpoints = []
    for i in range(0,len(var)):
        curr_var = var[i]
        curr_sz = sizes[i]
        default = 2**curr_sz-1
        for sz in range(0,curr_sz+1):
           cvpt = ''
           val = (default << sz) & default
           setval = (1 << sz) & default
           val = (val & (random.randrange(1,2**curr_sz)<<sz)) & default
           val = val | setval
           cvpt += curr_var + ' == 0x{0:0{1}X}'.format(val,int(ceil(curr_sz/4)))
           cmnt = '{1} Trailing zeros for {0}. Other operands are random'.\
                   format(curr_var, sz)
           for othervars in range(0,len(var)):
               if othervars != i:
                   otherval = random.randrange(0,2**sizes[othervars])
                   cvpt += ' and ' + var[othervars] + ' == 0x{0:0{1}X}'.format(otherval,int(ceil(sizes[othervars]/4)))
           coverpoints.append((cvpt+ " #nosat",cmnt))
    return coverpoints

def trailing_ones(xlen, var = ['rs1_val','rs2_val'], sizes = [32,32], seed = 13):
    '''
    For each rs register input, generate a random XLEN input value, and set the least-significant i bits.
    See the other rs input, pick a random value.

    :param xlen: size of the bit-vector to generate trailing-1s
    :param var: list of string variables indicating the operands
    :param sizes: list of sizes of the variables in var
    :param seed: intial seed value of the random library

    :type xlen: int
    :type var: List[str]
    :type sizes: List[int]
    :type seed: int

    '''
    random.seed(seed)
    coverpoints = []
    for i in range(0,len(var)):
        curr_var = var[i]
        curr_sz = sizes[i]
        default = (2**curr_sz)-1
        for sz in range(0,curr_sz+1):
           cvpt = ''
           val = random.randrange(1,(2**curr_sz))
           setval = (1<<(curr_sz-sz)) ^ (default)
           val = val | (default>> sz)
           val = val & setval
           cvpt += curr_var + ' == 0x{0:0{1}X}'.format(val,int(ceil(curr_sz/4)))
           cmnt = '{1} Trailing ones for {0}. Other operands are random'.\
                   format(curr_var, curr_sz-sz)
           for othervars in range(0,len(var)):
               if othervars != i:
                   otherval = random.randrange(0,2**sizes[othervars])
                   cvpt += ' and ' + var[othervars] + ' == 0x{0:0{1}X}'.format(otherval,int(ceil(sizes[othervars]/4)))
           coverpoints.append((cvpt+ " #nosat",cmnt))
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
    coverpoints =[]
    for d in dataset:
        coverpoints.append((var + ' == ' + str(d),'Alternate: '+str(hex(d))))
    return coverpoints
    #coverpoints = [var + ' == ' + str(d) for d in dataset]
    #return [(coverpoint,"Alternate") for coverpoint in coverpoints]


def expand_cgf(cgf_files, xlen):
    '''
    This function will replace all the abstract functions with their unrolled
    coverpoints

    :param cgf_files: list of yaml file paths which together define the coverpoints
    :param xlen: XLEN of the riscv-trace

    :type cgf: list
    :type xlen: int
    '''

    cgf = utils.load_cgf(cgf_files)
    for labels, cats in cgf.items():
        if labels != 'datasets':
            for label,node in cats.items():
                if isinstance(node,dict):
                    if 'abstract_comb' in node:
                        temp = node['abstract_comb']
                        del node['abstract_comb']
                        for coverpoints, coverage in temp.items():
                            i = 0
                            try:
                                exp_cp = eval(coverpoints)
                            except Exception as e:
                                pass
                            else:
                                for cp,comment in exp_cp:
                                    cgf[labels][label].insert(1,cp,coverage,comment=comment)
    return dict(cgf)

