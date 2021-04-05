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
	
def test_pattern2(N=1, seed=-1, l_rs1=-1, u_rs1=-1, l_rs2=-1, u_rs2=-1):
	'''
	Test pattern 2: Uniform Random
	Generate uniform random values for rs1, rs2 and bs.
	Let register values be un-constrained: 0..31.
	Repeat N times for each instruction until sufficient coverage is reached.
	'''
	if seed == -1:
		random.seed(0)
	else:
		random.seed(seed)
	
	if l_rs1 == -1:
		l_rs1 = 0
	if u_rs1 == -1:
		u_rs1 = pow(2,32)
	if l_rs2 == -1:
		l_rs2 = 0
	if u_rs2 == -1:
		u_rs2 = pow(2,32)
	
	coverpoints = []
	while N!= 0:
		rs1 = int(random.uniform(l_rs1, u_rs1))
		rs2 = int(random.uniform(l_rs2, u_rs2))
		bs = random.randrange(5)
		coverpoints.append('rs1 == '+ "0x{:08x}".format(rs1) + ' and rs2 == '+ "0x{:08x}".format(rs2) + ' and bs == '+ str(bs))
		N = N-1
	
	return(coverpoints)

