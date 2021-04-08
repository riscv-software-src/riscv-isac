# See LICENSE.incore for details
from math import *
import riscv_isac.utils as utils
import itertools
import random

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
    return coverpoints

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

def byte_count(xlen, variables=['rs1','rs2','imm_val'], overlap = "N"):
	'''
	Test pattern 1: SBox Testing
	This uses the byte-count pattern described above.
	Generate a 256-byte sequence 0..255 and pack the sequence into 32-bit words.
	Each word in the sequence is the rs2 input. The rs1 input is set to zero so we do not alter the SBox output value.
	For each input word, generate 4 instructions, with bs=0..3. 
	This will mean that every possible SBox input pattern is tested.
	'''
	rs1 = 0
	rs2 = []
	coverpoints = []
	hex_str = ""
	i=0
	
	while(i<=256):
		hex_str = "{:02x}".format(i) + hex_str
		if((len(hex_str)/2)%(xlen/8) == 0):
			rs2.append('0x'+hex_str)
			hex_str = ""
			if(overlap == "Y"):
				i=int(i-(xlen/16))
		i=i+1
	
	if xlen == 32:
		for i in range(len(rs2)):
			for j in range(4):
				coverpoints.append(variables[0] +' == '+ str(rs1) +' and '+ variables[1] +' == '+ rs2[i] + ' and '+ variables[2] +' == '+ str(j))
	else:
		if variables[1] == "rs2":
			for i in range(len(rs2)):
				if((i+1)%2==0):
					y = rs2[i-1]
					x = rs2[i]
				else:
					x = rs2[i]
					y = rs2[i+1]
				coverpoints.append(variables[0] +' == '+ x +' and '+ variables[1] +' == '+ y)
		elif variables[1] == "rcon":
			for i in range(len(rs2)):
				coverpoints.append(variables[0] +' == '+ rs2[i] +' and '+ variables[1] +' == 0xA')
	return(coverpoints)
	
def uniform_random(N=10, seed=10, variables=['rs1','rs2','imm_val'], size=[32,32,1]):
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
			val = int(random.uniform(0,2**int(size[v])))
			random_vals.append(variables[v] + \
			' == {0:#0{1}x}'.format(val,int(size[v]/4)+2))
		coverpoints.append(" and ".join(random_vals))
		N = N-1
	
	return(coverpoints)

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
                        temp = cgf[labels][label]['abstract_comb']
                        del cgf[labels][label]['abstract_comb']
                        for coverpoints, coverage in temp.items():
                                if 'walking' in coverpoints or 'alternate' in coverpoints or 'sp_dataset' in coverpoints or 'byte_count' in coverpoints or 'uniform_random' in coverpoints:
                                    exp_cp = eval(coverpoints)
                                    for e in exp_cp:
                                        cgf[labels][label][e] = coverage
    return cgf

