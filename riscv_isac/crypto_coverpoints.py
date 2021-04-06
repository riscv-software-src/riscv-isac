import random
import math

def test_pattern1():
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
	for i in range(256):
		hex_str = "{:02x}".format(i) + hex_str
		if((i+1)%4 == 0):
			rs2.append('0x'+hex_str)
			hex_str = ""
	
	for i in range(len(rs2)):
		for j in range(4):
			coverpoints.append('rs1 == '+ str(rs1) +' and rs2 == '+ rs2[i] + ' and bs == '+ str(j))
	
	return(coverpoints)
	
def test_pattern2(N=10, seed=10, variables=['rs1','rs2','bs'], size=[32,32,1]):
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
                val = int(random.uniform(0,2**size[v]))
                random_vals.append(variables[v] + \
                        ' == {0:#0{1}x}'.format(val,int(size[v]/4)+2))
            coverpoints.append(" and ".join(random_vals))
            N = N-1
	
	return(coverpoints)

