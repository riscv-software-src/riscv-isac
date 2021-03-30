from riscv_isac.log import logger
import itertools
import struct
import random
import sys
import math
from decimal import *

fzero       = ['0x00000000', '0x80000000']
fminsubnorm = ['0x00000001', '0x80000001']
fsubnorm    = ['0x00000002', '0x80000002', '0x007FFFFE', '0x807FFFFE', '0x00555555', '0x80555555']
fmaxsubnorm = ['0x007FFFFF', '0x807FFFFF']
fminnorm    = ['0x00800000', '0x80800000']
fnorm       = ['0x00800001', '0x80800001', '0x00855555', '0x80855555', '0x008AAAAA', '0x808AAAAA', '0x55000000', '0xD5000000', '0x2A000000', '0xAA000000']
fmaxnorm    = ['0x7F7FFFFF', '0xFF7FFFFF']
finfinity   = ['0x7F800000', '0xFF800000']
fdefaultnan = ['0x7FC00000', '0xFFC00000']
fqnan       = ['0x7FC00001', '0xFFC00001', '0x7FC55555', '0xFFC55555']
fsnan       = ['0x7F800001', '0xFF800001', '0x7FAAAAAA', '0xFFAAAAAA']
fone        = ['0x3F800000', '0xBF800000']

dzero       = ['0x0000000000000000', '0x8000000000000000']
dminsubnorm = ['0x0000000000000001', '0x8000000000000001']
dsubnorm    = ['0x0000000000000002', '0x8000000000000002','0x0008000000000000', '0x0008000000000002', '0x0001000000000000', '0x8001000000000000','0x8001000000000003','0x8001000000000007']
dmaxsubnorm = ['0x000FFFFFFFFFFFFF', '0x800FFFFFFFFFFFFF']
dminnorm    = ['0x0010000000000000', '0x8010000000000000']
dnorm       = ['0x0010000000000002', '0x8010000000000002', '0x0011000000000000', '0x8011000000000000', '0x0018000000000000', '0x8018000000000000','0x8018000000000005','0x8018000000000007']
dmaxnorm    = ['0x7FEFFFFFFFFFFFFF', '0xFFEFFFFFFFFFFFFF']
dinfinity   = ['0x7FF0000000000000', '0xFFF0000000000000']
ddefaultnan = ['0x7FF8000000000000', '0xFFF8000000000000']
dqnan       = ['0x7FF8000000000001', '0xFFF8000000000001']
dsnan       = ['0x7FF0000000000001', '0xFFF0000000000001']
done        = ['0x3FF0000000000000', '0xBF80000000000000']

rounding_modes = ['0','1','2','3','4']

def num_explain(flen,num):
	num_dict = {
		tuple(fzero) 		: 'fzero',
		tuple(fminsubnorm) 	: 'fminsubnorm',
		tuple(fsubnorm) 	: 'fsubnorm',
		tuple(fmaxsubnorm) 	: 'fmaxsubnorm',
		tuple(fminnorm) 	: 'fminnorm',
		tuple(fnorm) 		: 'fnorm',
		tuple(fmaxnorm) 	: 'fmaxnorm',
		tuple(finfinity) 	: 'finfinity',
		tuple(fdefaultnan) 	: 'fdefaultnan',
		tuple(fqnan) 		: 'fqnan',
		tuple(fsnan) 		: 'fsnan',
		tuple(fone) 		: 'fone',
		tuple(dzero) 		: 'dzero',
		tuple(dminsubnorm) 	: 'dminsubnorm',
		tuple(dsubnorm) 	: 'dsubnorm',
		tuple(dmaxsubnorm) 	: 'dmaxsubnorm',
		tuple(dminnorm) 	: 'dminnorm',
		tuple(dnorm) 		: 'dnorm',
		tuple(dmaxnorm) 	: 'dmaxnorm',
		tuple(dinfinity) 	: 'dinfinity',
		tuple(ddefaultnan) 	: 'ddefaultnan',
		tuple(dqnan) 		: 'dqnan',
		tuple(dsnan) 		: 'dsnan',
		tuple(done) 		: 'done'
	}
	num_list = list(num_dict.items())
	for i in range(len(num_list)):
		if(('0x'+num[2:].upper()) in num_list[i][0]):
			return(num_list[i][1])
	
	if flen == 32:
		e_sz = 8
		m_sz = 23
	else:
		e_sz = 11
		m_sz = 52
	bin_val = bin(int('1'+num[2:],16))[3:]
	sgn = bin_val[0]
	exp = bin_val[1:e_sz+1]
	man = bin_val[e_sz+1:]
	
	if(int(exp,2)!=0):
		return('fnorm' if flen==32 else 'dnorm')
	else:
		return('fsubnorm' if flen==32 else 'dsubnorm')
	

def ibm_dataset(flen, instr, operand):
	opcode_dict = {
		'fadd'     : 'b1_dataset + b2_dataset + b3_dataset',
		'fsub'     : 'b1_dataset + b2_dataset + b3_dataset',
		'fmul'     : 'b1_dataset + b2_dataset',
		'fdiv'     : 'b1_dataset + b2_dataset',
		'fmadd'    : {'*+':3},
		'fmsub'    : {'*+':3},
		'fnmadd'   : {'*+':3},
		'fnmsub'   : {'*+':3},
		'fsqrt'    : 'b1_dataset',
		'fmin'     : 'b1_dataset',
		'fmax'     : 'b1_dataset',
		'fcvt.w.s' : {'V':1},
		'fcvt.s.w' : {'V':1},
		'fmv.x.w'  : {'cp':1},
		'fmv.w.x'  : {'cp':1},
		'feq'      : {'+':2},
		'flt'      : {'+':2},
		'fle'      : {'+':2},
		'fcvt.wu.s': {'V':1},
		'fcvt.s.wu': {'V':1},
		'fsgnj'    : 'b1_dataset',
		'fsgnjn'   : 'b1_dataset',
		'fsgnjx'   : 'b1_dataset',
		'flw'      : {'V':1},
		'fsw'      : {'V':1},
		'fclass'   : {'?-':1,'?n':1,'?0':1,'?s':1,'?i':1,'?N':1,'?sN':1},
		'fcvt.l.s' : {'V':1},
		'fcvt.lu.s': {'V':1},
		'fcvt.s.l' : {'V':1},
		'fcvt.s.lu': {'V':1}
	}
	if flen == 32:
		b1_dataset = fzero + fminsubnorm + [fsubnorm[0], fsubnorm[3]] +\
			fmaxsubnorm + fminnorm + [fnorm[0], fnorm[3]] + fmaxnorm + \
			finfinity + fdefaultnan + [fqnan[0], fqnan[3]] + \
			[fsnan[0], fsnan[3]] + fone
		if operand in 'rs1_val':
			b2_dataset = [fzero[0],fone[0]]
			b3_dataset = ['0x00800007','0x00000000']
		elif operand in 'rs2_val':
			b2_dataset = ibm_b2_dataset(32)
			b3_dataset = ['0x02000000', '0x82000000','0x00000000','0x80000000']
	elif flen == 64:
		b1_dataset = dzero + dminsubnorm + [dsubnorm[0], dsubnorm[1]] +\
			dmaxsubnorm + dminnorm + [dnorm[0], dnorm[1]] + dmaxnorm + \
			dinfinity + ddefaultnan + [dqnan[0], dqnan[1]] + \
			[dsnan[0], dsnan[1]] + done
		if operand in 'rs1_val':
			b2_dataset = [dzero[0],done[0]]
		elif operand in 'rs2_val':
			b2_dataset = ibm_b2_dataset(64)
	
	dataset = eval(opcode_dict.get(instr.split('.')[0]))
	for i in range(len(dataset)):
		dataset[i] = int(dataset[i],16)
	
	return(dataset)

def ibm_b2_dataset(flen):
	if flen == 32:
		flip_types = fzero + fone + fminsubnorm + fmaxsubnorm + fminnorm + fmaxnorm
		b = '0x00000001'
	elif flen == 64:
		flip_types = dzero + done + dminsubnorm + dmaxsubnorm + dminnorm + dmaxnorm
		b = '0x0000000000000001'
	
	result = []
	
	for i in range(len(flip_types)):
		result.append('0x' + hex(int('1'+flip_types[i][2:], 16) ^ int(b[2:], 16))[3:])
	
	return(result)

def extract_fields(flen, hexstr, postfix):
    if flen == 32:
        e_sz = 8
        m_sz = 23
    else:
        e_sz = 11
        m_sz = 52
    bin_val = bin(int('1'+hexstr[2:],16))[3:]
    sgn = bin_val[0]
    exp = bin_val[1:e_sz+1]
    man = bin_val[e_sz+1:]
    if flen == 32:
        string = 'fs'+postfix+' == '+str(sgn) +\
                 ' and fe'+postfix+' == '+'0x'+str(hex(int('1'+exp,2))[3:]) +\
                 ' and fm'+postfix+' == '+'0x'+str(hex(int('10'+man,2))[3:])
    elif flen == 64:
        string = 'fs'+postfix+' == '+str(sgn) +\
                 ' and fe'+postfix+' == '+'0x'+str(hex(int('10'+exp,2))[3:]) +\
                 ' and fm'+postfix+' == '+'0x'+str(hex(int('1'+man,2))[3:])

    return string

def fields_dec_converter(flen, hexstr):							# IEEE-754 Hex -> Decimal Converter
	
	if flen == 32:
		e_sz = 8
		m_sz = 23
	elif flen == 64:
		e_sz = 11
		m_sz = 52
	bin_val = bin(int('1'+hexstr[2:],16))[3:]
	sgn = bin_val[0]
	exp = bin_val[1:e_sz+1]
	man = bin_val[e_sz+1:]
	
	num=''
	if(int(sgn)==1):
		sign = '-'
	elif(int(sgn)==0):
		sign = '+'
		
	exp_str = '*pow(2,'
	
	if(flen == 32):
		if((int(exp,2)-127)<-126):
			conv_num = 0.0
			exp_str+= str(-126)+')'
		elif((int(exp,2)-127)>=-126):
			conv_num = 1.0
			exp_str+= str(int(exp,2)-127)+')'
	elif(flen == 64):
		if((int(exp,2)-1023)<-1022):
			conv_num = 0.0
			exp_str+= str(-1022)+')'
		elif((int(exp,2)-1023)>=-1022):
			conv_num = 1.0
			exp_str+= str(int(exp,2)-1023)+')'
	for i in range(len(man)):
		conv_num+= (1/(pow(2,i+1)))*int(man[i])
	
	num = sign + str(conv_num) + exp_str
	if(flen == 32):
		if(eval(num) > 1e-45 or eval(num)<-1e-45):
			return(eval(num))
		else:
			return(eval(sign+'1e-45'))
	elif(flen == 64):
		return(eval(num))

def floatingPoint_tohex(flen,float_no):							# Decimal -> IEEE-754 Hex Converter
	
	if(flen==32):
		if(str(float_no)=='-inf'):
			return(finfinity[1])
		elif(str(float_no)=='inf'):
			return(finfinity[0])
	elif(flen==64):
		if(str(float_no)=='-inf'):
			return(dinfinity[1])
		elif(str(float_no)=='inf'):
			return(dinfinity[0])
	
	float_no=float.hex(float_no)
	num="N"
	
	a=float.fromhex(float_no)
	
	sign=0
	if(a<0 or str(a)[0]=='-'):
		sign=1
	nor=float.hex(a)									# Normalized Number
	
	if(flen==32):
		if(int(nor.split("p")[1])<-126):						# Checking Underflow of Exponent
			exp_bin=('0'*8)							# Exponent of Subnormal numbers
			exp_sn=int(nor.split("p")[1])
			num="SN"
		elif(int(nor.split("p")[1])>127):						# Checking Overflow of Exponent
			if(sign==0):
				return "0x7f7fffff"						# Most Positive Value
			else:
				return "0xff7fffff"						# Most Negative Value
		else:										# Converting Exponent to 8-Bit Binary
			exp=int(nor.split("p")[1])+127
			exp_bin=('0'*(8-(len(bin(exp))-2)))+bin(exp)[2:]
	elif(flen==64):
		check_sn = nor.split("p")[0].split(".")[0]
		if(int(check_sn[len(check_sn)-1])==0):					# Checking Underflow of Exponent
			exp_bin=('0'*11)							# Exponent of Subnormal numbers
			exp_sn=int(nor.split("p")[1])
			num="SN"
		elif(int(nor.split("p")[1])>1023):						# Checking Overflow of Exponent
			if(sign==0):
				return "0x7FEFFFFFFFFFFFFF"					# Most Positive Value
			else:
				return "0x0xFFEFFFFFFFFFFFFF"					# Most Negative Value
		else:										# Converting Exponent to 8-Bit Binary
			exp=int(nor.split("p")[1])+1023
			exp_bin=('0'*(11-(len(bin(exp))-2)))+bin(exp)[2:]
	
	if(num=="SN"):
		if(sign==0):
			mant="0x"+float_no.split("p")[0][4:]
		else:
			mant="0x"+float_no.split("p")[0][5:]
	else:
		if(sign==0):
			mant="0x"+nor.split("p")[0][4:]
		else:
			mant="0x"+nor.split("p")[0][5:]
	
	if(flen==32):
		mant_bin=bin(int('1'+mant[2:],16))[3:]
		if(num == "SN"):
			mant_bin='1'+bin(int('1'+mant[2:],16))[3:]
			while(exp_sn!=-127):
				exp_sn+=1
				mant_bin = '0'+mant_bin
		binary="0b"
		binary=binary+str(sign)+exp_bin+mant_bin[0:23]
		hex_tp=hex(int(binary,2))
		hex_tp=hex_tp.replace('0x','0x'+'0'*(8-(len(hex_tp)-2)))
	elif(flen==64):
		mant_bin=bin(int('1'+mant[2:],16))[3:]
		if(num == "SN"):
			mant_bin=bin(int('1'+mant[2:],16))[3:]
		binary="0b"
		binary=binary+str(sign)+exp_bin+mant_bin[0:52]
		hex_tp=hex(int(binary,2))
		hex_tp=hex_tp.replace('0x','0x'+'0'*(16-(len(hex_tp)-2)))
	
	return(hex_tp)

def ibm_b1(flen, opcode, ops):
	'''
	Test all combinations of floating-point basic types, positive and negative, for
	each of the inputs. The basic types are Zero, One, MinSubNorm, SubNorm,
	MaxSubNorm, MinNorm, Norm, MaxNorm, Infinity, DefaultNaN, QNaN, and
	SNaN.
	'''
	if flen == 32:
		basic_types = fzero + fminsubnorm + [fsubnorm[0], fsubnorm[3]] +\
			fmaxsubnorm + fminnorm + [fnorm[0], fnorm[3]] + fmaxnorm + \
			finfinity + fdefaultnan + [fqnan[0], fqnan[3]] + \
			[fsnan[0], fsnan[3]] + fone
	elif flen == 64:
		basic_types = dzero + dminsubnorm + [dsubnorm[0], dsubnorm[1]] +\
			dmaxsubnorm + dminnorm + [dnorm[0], dnorm[1]] + dmaxnorm + \
			dinfinity + ddefaultnan + [dqnan[0], dqnan[1]] + \
			[dsnan[0], dsnan[1]] + done
	else:
		logger.error('Invalid flen value!')
		sys.exit(1)
    
    # the following creates a cross product for ops number of variables
	b1_comb = list(itertools.product(*ops*[basic_types]))
	coverpoints = []
	for c in b1_comb:
		cvpt = ""
		for x in range(1, ops+1):
#            cvpt += 'rs'+str(x)+'_val=='+str(c[x-1]) # uncomment this if you want rs1_val instead of individual fields
			cvpt += (extract_fields(flen,c[x-1],str(x)))
			cvpt += " and "
		if opcode.split('.')[0] in ["fadd","fsub","fmul","fdiv","fsqrt","fmadd","fnmadd","fmsub","fnmsub","fcvt","fmv","fle","fmv","fmin","fsgnj"]:
			cvpt += 'rm == 0'
		elif opcode.split('.')[0] in ["fclass","flt","fmax","fsgnjn"]:
			cvpt += 'rm == 1'
		elif opcode.split('.')[0] in ["feq","flw","fsw","fsgnjx"]:
			cvpt += 'rm == 2'
		cvpt += ' # '
		for y in range(1, ops+1):
			cvpt += 'rs'+str(y)+'_val=='
			cvpt += num_explain(flen, c[y-1]) + '(' + str(c[y-1]) + ')'
			if(y != ops):
				cvpt += " and "
		coverpoints.append(cvpt)
    
	mess='Generated'+ (' '*(5-len(str(len(coverpoints)))))+ str(len(coverpoints)) +' '+ (str(32) if flen == 32 else str(64)) + '-bit coverpoints using Model B1 for '+opcode+' !'
	logger.info(mess)
	return coverpoints

def ibm_b2(flen, opcode, ops, int_val = 100, seed = -1):
	'''
	This model tests final results that are very close, measured in Hamming distance,
	to the specified boundary values. Each boundary value is taken as a base value, 
	and the model enumerates over small deviations from the base, by flipping one bit 
	of the significand.
	'''
	if flen == 32:
		flip_types = fzero + fone + fminsubnorm + fmaxsubnorm + fminnorm + fmaxnorm
		b = '0x00000010'
		e_sz=8
		m_sz = 23
	elif flen == 64:
		flip_types = dzero + done + dminsubnorm + dmaxsubnorm + dminnorm + dmaxnorm
		b = '0x0000000000000010'
		e_sz=11
		m_sz = 52
		
	result = []
	b2_comb = []
	opcode = opcode.split('.')[0]
	
	if seed == -1:
		if opcode in 'fadd':
			random.seed(0)
		elif opcode in 'fsub':
			random.seed(1)
		elif opcode in 'fmul':
			random.seed(2)
		elif opcode in 'fdiv':
			random.seed(3)
		elif opcode in 'fsqrt':
			random.seed(4)
		elif opcode in 'fmadd':
			random.seed(5)
		elif opcode in 'fnmadd':
			random.seed(6)
		elif opcode in 'fmsub':
			random.seed(7)
		elif opcode in 'fnmsub':
			random.seed(8)
	else:
		random.seed(seed)
			
	for i in range(len(flip_types)):
		result.append('0x' + hex(int('1'+flip_types[i][2:], 16) ^ int(b[2:], 16))[3:])
	
	for i in range(len(result)):
		bin_val = bin(int('1'+result[i][2:],16))[3:]
		rsgn = bin_val[0]
		rexp = bin_val[1:e_sz+1]
		rman = bin_val[e_sz+1:]
		rs1_exp = rs3_exp = rexp
		rs1_bin = bin(random.randrange(1,int_val))
		rs3_bin = bin(random.randrange(1,int_val))
		rs1_bin = ('0b0'+rexp+('0'*(m_sz-(len(rs1_bin)-2)))+rs1_bin[2:])
		rs3_bin = ('0b0'+rexp+('0'*(m_sz-(len(rs3_bin)-2)))+rs3_bin[2:])
		rs1 = fields_dec_converter(flen,'0x'+hex(int('1'+rs1_bin[2:],2))[3:])
		rs3 = fields_dec_converter(flen,'0x'+hex(int('1'+rs3_bin[2:],2))[3:])
		if opcode in 'fadd':
			rs2 = fields_dec_converter(flen,result[i]) - rs1
		elif opcode in 'fsub':
			rs2 = rs1 - fields_dec_converter(flen,result[i])
		elif opcode in 'fmul':
			rs2 = fields_dec_converter(flen,result[i])/rs1
		elif opcode in 'fdiv':
			rs2 = rs1/fields_dec_converter(flen,result[i])
		elif opcode in 'fsqrt':
			rs2 = fields_dec_converter(flen,result[i])*fields_dec_converter(flen,result[i])
		elif opcode in 'fmadd':
			rs2 = (fields_dec_converter(flen,result[i]) - rs3)/rs1
		elif opcode in 'fnmadd':
			rs2 = (rs3 - fields_dec_converter(flen,result[i]))/rs1
		elif opcode in 'fmsub':
			rs2 = (fields_dec_converter(flen,result[i]) + rs3)/rs1
		elif opcode in 'fnmsub':
			rs2 = -1*(rs3 + fields_dec_converter(flen,result[i]))/rs1
		
		if(flen==32):
			m = struct.unpack('f', struct.pack('f', rs2))[0]
		elif(flen==64):
			m = rs2
		
		if opcode in ['fadd','fsub','fmul','fdiv']:
			b2_comb.append((floatingPoint_tohex(flen,rs1),floatingPoint_tohex(flen,m)))
		elif opcode in 'fsqrt':
			b2_comb.append((floatingPoint_tohex(flen,m),))
		elif opcode in ['fmadd','fnmadd','fmsub','fnmsub']:
			b2_comb.append((floatingPoint_tohex(flen,rs1),floatingPoint_tohex(flen,m),floatingPoint_tohex(flen,rs3)))
	#print("b2_comb",b2_comb)
	coverpoints = []
	for c in b2_comb:
		cvpt = ""
		for x in range(1, ops+1):
#            cvpt += 'rs'+str(x)+'_val=='+str(c[x-1]) # uncomment this if you want rs1_val instead of individual fields
			cvpt += (extract_fields(flen,c[x-1],str(x)))
			cvpt += " and "
		cvpt += 'rm == 0'
		cvpt += ' # '
		for y in range(1, ops+1):
			cvpt += 'rs'+str(y)+'_val=='
			cvpt += num_explain(flen, c[y-1]) + '(' + str(c[y-1]) + ')'
			if(y != ops):
				cvpt += " and "
		coverpoints.append(cvpt)
	
	mess='Generated'+ (' '*(5-len(str(len(coverpoints)))))+ str(len(coverpoints)) +' '+ (str(32) if flen == 32 else str(64)) + '-bit coverpoints using Model B2 for '+opcode+' !'
	logger.info(mess)
	return coverpoints
	
def ibm_b3(flen, opcode, ops, seed=-1):
	'''
	This model tests all combinations of the sign, significand's LSB,
	guard bit & sticky bit of the intermediate result
	'''
	opcode = opcode.split('.')[0]
	getcontext().prec = 40
	
	if seed == -1:
		if opcode in 'fadd':
			random.seed(0)
		elif opcode in 'fsub':
			random.seed(1)
		elif opcode in 'fmul':
			random.seed(2)
		elif opcode in 'fdiv':
			random.seed(3)
		elif opcode in 'fsqrt':
			random.seed(4)
		elif opcode in 'fmadd':
			random.seed(5)
		elif opcode in 'fnmadd':
			random.seed(6)
		elif opcode in 'fmsub':
			random.seed(7)
		elif opcode in 'fnmsub':
			random.seed(8)
	else:
		random.seed(seed)
	
	if flen == 32:
		ieee754_maxnorm = '0x1.7fffffp+127'
		maxnum = float.fromhex(ieee754_maxnorm)
		ieee754_num = []
		lsb = []
		for i in fsubnorm+fnorm:
			if int(i[-1],16)%2 == 1: 
				lsb.append('1')
				lsb.append('1')
			else:
				lsb.append('0')
				lsb.append('0')
			float_val = float.hex(fields_dec_converter(32,i))
			if float_val[0] != '-':
				ieee754_num.append(float_val.split('p')[0][0:10]+'p'+float_val.split('p')[1])
				ieee754_num.append('-'+float_val.split('p')[0][0:10]+'p'+float_val.split('p')[1])
			else:
				ieee754_num.append(float_val.split('p')[0][0:11]+'p'+float_val.split('p')[1])
				ieee754_num.append(float_val.split('p')[0][1:11]+'p'+float_val.split('p')[1])
				
		ir_dataset = []
		for k in range(len(ieee754_num)):
			for i in range(2,16,2):
				grs = '{:04b}'.format(i)
				if ieee754_num[k][0] == '-': sign = '1'
				else: sign = '0'
				ir_dataset.append([ieee754_num[k].split('p')[0]+str(i)+'p'+ieee754_num[k].split('p')[1],' | Guard = '+grs[0]+' Sticky = '+grs[2]+' Sign = '+sign+' LSB = '+lsb[k]])
			
		for i in range(len(ir_dataset)):
			ir_dataset[i][0] = float.fromhex(ir_dataset[i][0])
			
	elif flen == 64:
		maxdec = '1.7976931348623157e+308'
		maxnum = float.fromhex('0x1.fffffffffffffp+1023')
		ieee754_num = []
		lsb = []
		for i in dsubnorm+dnorm:
			if int(i[-1],16)%2 == 1:
				lsb.append('1')
				lsb.append('1')
			else:
				lsb.append('0')
				lsb.append('0')
			float_val = str(fields_dec_converter(64,i))
			if float_val[0] != '-':
				ieee754_num.append(float_val)
				ieee754_num.append('-'+float_val)
			else:
				ieee754_num.append(float_val)
				ieee754_num.append(float_val[1:])
				
		ir_dataset = []
		for k in range(len(ieee754_num)):
			for i in range(2,16,2):
				grs = '{:04b}'.format(i)
				if ieee754_num[k][0] == '-': sign = '1'
				else: sign = '0'
				ir_dataset.append([str(Decimal(ieee754_num[k].split('e')[0])+Decimal(pow(i*16,-14)))+'e'+ieee754_num[k].split('e')[1],' | Guard = '+grs[0]+' Sticky = '+grs[2]+' Sign = '+sign+' LSB = '+lsb[k]])
				
	b4_comb = []
	
	for i in range(len(ir_dataset)):
		rs1 = random.uniform(1,maxnum)
		rs3 = random.uniform(1,maxnum)
		if opcode in 'fadd':
			if flen == 32:
				rs2 = ir_dataset[i][0] - rs1
			elif flen == 64:
				rs2 = Decimal(ir_dataset[i][0]) - Decimal(rs1)
		elif opcode in 'fsub':
			if flen == 32:
				rs2 = rs1 - ir_dataset[i][0]
			elif flen == 64:
				rs2 = Decimal(rs1) - Decimal(ir_dataset[i][0])
		elif opcode in 'fmul':
			if flen == 32:
				rs2 = ir_dataset[i][0]/rs1
			elif flen == 64:
				rs2 = Decimal(ir_dataset[i][0])/Decimal(rs1)
		elif opcode in 'fdiv':
			if flen == 32:
				rs2 = rs1/ir_dataset[i][0]
			elif flen == 64:
				rs2 = Decimal(rs1)/Decimal(ir_dataset[i][0])
		elif opcode in 'fsqrt':
			if flen == 32:
				rs2 = ir_dataset[i][0]*ir_dataset[i][0]
			elif flen == 64:
				rs2 = Decimal(ir_dataset[i][0])*Decimal(ir_dataset[i][0])
		elif opcode in 'fmadd':
			if flen == 32:
				rs2 = (ir_dataset[i][0] - rs3)/rs1
			elif flen == 64:
				rs2 = (Decimal(ir_dataset[i][0]) - Decimal(rs3))/Decimal(rs1)
		elif opcode in 'fnmadd':
			if flen == 32:
				rs2 = (rs3 - ir_dataset[i][0])/rs1
			elif flen == 64:
				rs2 = (Decimal(rs3) - Decimal(ir_dataset[i][0]))/Decimal(rs1)
		elif opcode in 'fmsub':
			if flen == 32:
				rs2 = (ir_dataset[i][0] + rs3)/rs1
			elif flen == 64:
				rs2 = (Decimal(ir_dataset[i][0]) + Decimal(rs3))/Decimal(rs1)
		elif opcode in 'fnmsub':
			if flen == 32:
				rs2 = -1*(rs3 + ir_dataset[i][0])/rs1
			elif flen == 64:
				rs2 = -1*(Decimal(rs3) + Decimal(ir_dataset[i][0]))/Decimal(rs1)
			
		if(flen==32):
			x1 = struct.unpack('f', struct.pack('f', rs1))[0]
			x2 = struct.unpack('f', struct.pack('f', rs2))[0]
			x3 = struct.unpack('f', struct.pack('f', rs3))[0]
		elif(flen==64):
			x1 = rs1
			x2 = rs2
			x3 = rs3
		
		if opcode in ['fadd','fsub','fmul','fdiv']:
			b4_comb.append((floatingPoint_tohex(flen,float(rs1)),floatingPoint_tohex(flen,float(rs2))))
		elif opcode in 'fsqrt':
			b4_comb.append((floatingPoint_tohex(flen,float(rs2)),))
		elif opcode in ['fmadd','fnmadd','fmsub','fnmsub']:
			b4_comb.append((floatingPoint_tohex(flen,float(rs1)),floatingPoint_tohex(flen,float(rs2)),floatingPoint_tohex(flen,float(rs3))))
		
	coverpoints = []
	k = 0	
	for c in b4_comb:
		for rm in range(5):
			cvpt = ""
			for x in range(1, ops+1):
#            			cvpt += 'rs'+str(x)+'_val=='+str(c[x-1]) # uncomment this if you want rs1_val instead of individual fields
				cvpt += (extract_fields(flen,c[x-1],str(x)))
				cvpt += " and "
			cvpt += 'rm == '+str(rm)
			cvpt += ' # '
			for y in range(1, ops+1):
				cvpt += 'rs'+str(y)+'_val=='
				cvpt += num_explain(flen, c[y-1]) + '(' + str(c[y-1]) + ')'
				if(y != ops):
					cvpt += " and "
			cvpt += ir_dataset[k][1]
			coverpoints.append(cvpt)
		k=k+1
	
	mess='Generated'+ (' '*(5-len(str(len(coverpoints)))))+ str(len(coverpoints)) +' '+ (str(32) if flen == 32 else str(64)) + '-bit coverpoints using Model B4 for '+opcode+' !'
	logger.info(mess)
	return coverpoints
	
def ibm_b4(flen, opcode, ops, seed=-1):
	'''
	This model creates a test-case for each of the following constraints on the intermediate results:
	i. All the numbers in the range [+MaxNorm – 3 ulp, +MaxNorm + 3 ulp]
	ii. All the numbers in the range [-MaxNorm - 3 ulp, -MaxNorm + 3 ulp]
	iii. A random number that is larger than +MaxNorm + 3 ulp
	iv. A random number that is smaller than -MaxNorm – 3 ulp
	v. One number for every exponent in the range [MaxNorm.exp - 3, MaxNorm.exp + 3] for positive and negative numbers
	'''
	opcode = opcode.split('.')[0]
	getcontext().prec = 40
	
	if seed == -1:
		if opcode in 'fadd':
			random.seed(0)
		elif opcode in 'fsub':
			random.seed(1)
		elif opcode in 'fmul':
			random.seed(2)
		elif opcode in 'fdiv':
			random.seed(3)
		elif opcode in 'fsqrt':
			random.seed(4)
		elif opcode in 'fmadd':
			random.seed(5)
		elif opcode in 'fnmadd':
			random.seed(6)
		elif opcode in 'fmsub':
			random.seed(7)
		elif opcode in 'fnmsub':
			random.seed(8)
	else:
		random.seed(seed)
	
	if flen == 32:
		ieee754_maxnorm_p = '0x1.7fffffp+127'
		ieee754_maxnorm_n = '0x1.7ffffep+127'
		maxnum = float.fromhex(ieee754_maxnorm_p)
		ir_dataset = []
		for i in range(2,16,2):
			grs = '{:04b}'.format(i)
			ir_dataset.append([ieee754_maxnorm_p.split('p')[0]+str(i)+'p'+ieee754_maxnorm_p.split('p')[1],' | Guard = '+grs[0]+' Round = '+grs[1]+' Sticky = '+grs[2]+' --> Maxnorm + '+str(int(grs[0:3],2))+' ulp'])
			ir_dataset.append([ieee754_maxnorm_n.split('p')[0]+str(i)+'p'+ieee754_maxnorm_n.split('p')[1],' | Guard = '+grs[0]+' Round = '+grs[1]+' Sticky = '+grs[2]+' --> Maxnorm - '+str(int(grs[0:3],2))+' ulp'])
		for i in range(-3,4):
			ir_dataset.append([ieee754_maxnorm_p.split('p')[0]+'p'+str(127+i),' | Exponent = '+str(127+i)+' Number = +ve'])
			ir_dataset.append(['-'+ieee754_maxnorm_n.split('p')[0]+'p'+str(127+i),' | Exponent = '+str(127+i)+' Number = -ve'])
		for i in range(len(ir_dataset)):
			ir_dataset[i][0] = float.fromhex(ir_dataset[i][0])
	elif flen == 64:
		maxnum = float.fromhex('0x1.fffffffffffffp+1023')
		maxdec_p = str(maxnum)
		maxdec_n = str(float.fromhex('0x1.ffffffffffffep+1023'))
		ir_dataset = []
		for i in range(2,16,2):
			grs = '{:04b}'.format(i)
			ir_dataset.append([str(Decimal(maxdec_p.split('e')[0])+Decimal(pow(i*16,-14)))+'e'+maxdec_p.split('e')[1],' | Guard = '+grs[0]+' Round = '+grs[1]+' Sticky = '+grs[2]+' --> Maxnorm + '+str(int(grs[0:3],2))+' ulp'])
			ir_dataset.append([str(Decimal(maxdec_n.split('e')[0])+Decimal(pow(i*16,-14)))+'e'+maxdec_n.split('e')[1],' | Guard = '+grs[0]+' Round = '+grs[1]+' Sticky = '+grs[2]+' --> Maxnorm - '+str(int(grs[0:3],2))+' ulp'])
		for i in range(-3,4):
			ir_dataset.append([str(random.uniform(1,maxnum)).split('e')[0]+'e'+str(int(math.log(pow(2,1023+i),10))),' | Exponent = '+str(1023+i)+' Number = +ve'])
			ir_dataset.append([str(-1*random.uniform(1,maxnum)).split('e')[0]+'e'+str(int(math.log(pow(2,1023+i),10))),' | Exponent = '+str(1023+i)+' Number = -ve'])
	
	b4_comb = []
	
	for i in range(len(ir_dataset)):
		rs1 = random.uniform(1,maxnum)
		rs3 = random.uniform(1,maxnum)
		if opcode in 'fadd':
			if flen == 32:
				rs2 = ir_dataset[i][0] - rs1
			elif flen == 64:
				rs2 = Decimal(ir_dataset[i][0]) - Decimal(rs1)
		elif opcode in 'fsub':
			if flen == 32:
				rs2 = rs1 - ir_dataset[i][0]
			elif flen == 64:
				rs2 = Decimal(rs1) - Decimal(ir_dataset[i][0])
		elif opcode in 'fmul':
			if flen == 32:
				rs2 = ir_dataset[i][0]/rs1
			elif flen == 64:
				rs2 = Decimal(ir_dataset[i][0])/Decimal(rs1)
		elif opcode in 'fdiv':
			if flen == 32:
				rs2 = rs1/ir_dataset[i][0]
			elif flen == 64:
				rs2 = Decimal(rs1)/Decimal(ir_dataset[i][0])
		elif opcode in 'fsqrt':
			if flen == 32:
				rs2 = ir_dataset[i][0]*ir_dataset[i][0]
			elif flen == 64:
				rs2 = Decimal(ir_dataset[i][0])*Decimal(ir_dataset[i][0])
		elif opcode in 'fmadd':
			if flen == 32:
				rs2 = (ir_dataset[i][0] - rs3)/rs1
			elif flen == 64:
				rs2 = (Decimal(ir_dataset[i][0]) - Decimal(rs3))/Decimal(rs1)
		elif opcode in 'fnmadd':
			if flen == 32:
				rs2 = (rs3 - ir_dataset[i][0])/rs1
			elif flen == 64:
				rs2 = (Decimal(rs3) - Decimal(ir_dataset[i][0]))/Decimal(rs1)
		elif opcode in 'fmsub':
			if flen == 32:
				rs2 = (ir_dataset[i][0] + rs3)/rs1
			elif flen == 64:
				rs2 = (Decimal(ir_dataset[i][0]) + Decimal(rs3))/Decimal(rs1)
		elif opcode in 'fnmsub':
			if flen == 32:
				rs2 = -1*(rs3 + ir_dataset[i][0])/rs1
			elif flen == 64:
				rs2 = -1*(Decimal(rs3) + Decimal(ir_dataset[i][0]))/Decimal(rs1)
			
		if(flen==32):
			x1 = struct.unpack('f', struct.pack('f', rs1))[0]
			x2 = struct.unpack('f', struct.pack('f', rs2))[0]
			x3 = struct.unpack('f', struct.pack('f', rs3))[0]
		elif(flen==64):
			x1 = rs1
			x2 = rs2
			x3 = rs3
		
		if opcode in ['fadd','fsub','fmul','fdiv']:
			b4_comb.append((floatingPoint_tohex(flen,float(rs1)),floatingPoint_tohex(flen,float(rs2))))
		elif opcode in 'fsqrt':
			b4_comb.append((floatingPoint_tohex(flen,float(rs2)),))
		elif opcode in ['fmadd','fnmadd','fmsub','fnmsub']:
			b4_comb.append((floatingPoint_tohex(flen,float(rs1)),floatingPoint_tohex(flen,float(rs2)),floatingPoint_tohex(flen,float(rs3))))
		
	coverpoints = []
	k = 0	
	for c in b4_comb:
		for rm in range(5):
			cvpt = ""
			for x in range(1, ops+1):
#            			cvpt += 'rs'+str(x)+'_val=='+str(c[x-1]) # uncomment this if you want rs1_val instead of individual fields
				cvpt += (extract_fields(flen,c[x-1],str(x)))
				cvpt += " and "
			cvpt += 'rm == '+str(rm)
			cvpt += ' # '
			for y in range(1, ops+1):
				cvpt += 'rs'+str(y)+'_val=='
				cvpt += num_explain(flen, c[y-1]) + '(' + str(c[y-1]) + ')'
				if(y != ops):
					cvpt += " and "
			cvpt += ir_dataset[k][1]
			coverpoints.append(cvpt)
		k=k+1
	
	mess='Generated'+ (' '*(5-len(str(len(coverpoints)))))+ str(len(coverpoints)) +' '+ (str(32) if flen == 32 else str(64)) + '-bit coverpoints using Model B4 for '+opcode+' !'
	logger.info(mess)
	return coverpoints
	
def ibm_b5(flen, opcode, ops, seed=-1):
	'''
	This model creates a test-case for each of the following constraints on the
	intermediate results:
	i. All the numbers in the range [+MinSubNorm – 3 ulp, +MinSubNorm + 3ulp]
	ii. All the numbers in the range [-MinSubNorm - 3 ulp, -MinSubNorm + 3ulp]
	iii. All the numbers in the range [MinNorm – 3 ulp, MinNorm + 3 ulp]
	iv. All the numbers in the range [-MinNorm - 3 ulp, -MinNorm + 3 ulp]
	v. A random number in the range (0, MinSubNorm)
	vi.A random number in the range (-MinSubNorm, -0)
	vii. One number for every exponent in the range [MinNorm.exp, MinNorm.exp+ 5]'''
	
	opcode = opcode.split('.')[0]
	getcontext().prec = 40
	if flen == 32:
		ieee754_maxnorm = '0x1.7fffffp+127'
		maxnum = float.fromhex(ieee754_maxnorm)
		ieee754_minsubnorm = '0x0.000001p-126'
		ir_dataset = []
		for i in range(0,16,2):
			grs = '{:04b}'.format(i)
			ir_dataset.append([ieee754_minsubnorm.split('p')[0]+str(i)+'p'+ieee754_minsubnorm.split('p')[1],' | Guard = '+grs[0]+' Round = '+grs[1]+' Sticky = '+grs[2]+' --> Minsubnorm + '+str(int(grs[0:3],2))+' ulp'])
		ieee754_minnorm = '0x1.000000p-126'
		for i in range(0,16,2):
			grs = '{:04b}'.format(i)
			ir_dataset.append([ieee754_minnorm.split('p')[0]+str(i)+'p'+ieee754_minnorm.split('p')[1],' | Guard = '+grs[0]+' Round = '+grs[1]+' Sticky = '+grs[2]+' --> Minnorm + '+str(int(grs[0:3],2))+' ulp'])
		minnorm_Exp = ['0x1.000000p-126','0x1.000000p-125','0x1.000000p-124','0x1.000000p-123','0x1.000000p-122','0x1.000000p-121']
		for i in minnorm_Exp:
			ir_dataset.append([i,' | Exponent = MinNorm.exp + '+str(126+int(i.split('p')[1]))])
		n = len(ir_dataset)
		for i in range(n):
			ir_dataset[i][0] = float.fromhex(ir_dataset[i][0])
			ir_dataset.append([-1*ir_dataset[i][0],ir_dataset[i][1]])
		
	elif flen == 64:
		maxdec = '1.7976931348623157e+308'
		maxnum = float.fromhex('0x1.fffffffffffffp+1023')
		minsubdec = '5e-324'
		ir_dataset = []
		for i in range(2,16,2):
			grs = '{:04b}'.format(i)
			ir_dataset.append([str(Decimal(minsubdec.split('e')[0])+Decimal(pow(i*16,-14)))+'e'+minsubdec.split('e')[1],' | Guard = '+grs[0]+' Round = '+grs[1]+' Sticky = '+grs[2]+' --> Minsubnorm + '+str(int(grs[0:3],2))+' ulp'])
		minnormdec = '2.2250738585072014e-308'
		ir_dataset.append([minsubdec, ' | Guard = 0 Round = 0 Sticky = 0 --> Minsubnorm + 0 ulp'])
		ir_dataset.append([minnormdec,' | Guard = 0 Round = 0 Sticky = 0 --> Minnorm + 0 ulp'])
		for i in range(2,16,2):
			grs = '{:04b}'.format(i)
			ir_dataset.append([str(Decimal(minnormdec.split('e')[0])+Decimal(pow(i*16,-14)))+'e'+minnormdec.split('e')[1],' | Guard = '+grs[0]+' Round = '+grs[1]+' Sticky = '+grs[2]+' --> Minnorm + '+str(int(grs[0:3],2))+' ulp'])
		minnorm_Exp = ['4.450147717014403e-308','8.900295434028806e-308','1.780059086805761e-307','3.560118173611522e-307','7.120236347223044e-307']
		
		k = 1
		for i in minnorm_Exp:
			ir_dataset.append([i,' | Exponent = MinNorm.exp + '+str(k)])
			k += 1
		n = len(ir_dataset)
		for i in range(n):
			ir_dataset.append(['-'+ir_dataset[i][0],ir_dataset[i][1]])
		
	if seed == -1:
		if opcode in 'fadd':
			random.seed(0)
		elif opcode in 'fsub':
			random.seed(1)
		elif opcode in 'fmul':
			random.seed(2)
		elif opcode in 'fdiv':
			random.seed(3)
		elif opcode in 'fsqrt':
			random.seed(4)
		elif opcode in 'fmadd':
			random.seed(5)
		elif opcode in 'fnmadd':
			random.seed(6)
		elif opcode in 'fmsub':
			random.seed(7)
		elif opcode in 'fnmsub':
			random.seed(8)
	else:
		random.seed(seed)
	
	b5_comb = []
			
	for i in range(len(ir_dataset)):
		rs1 = random.uniform(1,maxnum)
		rs3 = random.uniform(1,maxnum)
		if opcode in 'fadd':
			if flen == 32:
				rs2 = ir_dataset[i][0] - rs1
			elif flen == 64:
				rs2 = Decimal(ir_dataset[i][0]) - Decimal(rs1)
		elif opcode in 'fsub':
			if flen == 32:
				rs2 = rs1 - ir_dataset[i][0]
			elif flen == 64:
				rs2 = Decimal(rs1) - Decimal(ir_dataset[i][0])
		elif opcode in 'fmul':
			if flen == 32:
				rs2 = ir_dataset[i][0]/rs1
			elif flen == 64:
				rs2 = Decimal(ir_dataset[i][0])/Decimal(rs1)
		elif opcode in 'fdiv':
			if flen == 32:
				rs2 = rs1/ir_dataset[i][0]
			elif flen == 64:
				rs2 = Decimal(rs1)/Decimal(ir_dataset[i][0])
		elif opcode in 'fsqrt':
			if flen == 32:
				rs2 = ir_dataset[i][0]*ir_dataset[i][0]
			elif flen == 64:
				rs2 = Decimal(ir_dataset[i][0])*Decimal(ir_dataset[i][0])
		elif opcode in 'fmadd':
			if flen == 32:
				rs2 = (ir_dataset[i][0] - rs3)/rs1
			elif flen == 64:
				rs2 = (Decimal(ir_dataset[i][0]) - Decimal(rs3))/Decimal(rs1)
		elif opcode in 'fnmadd':
			if flen == 32:
				rs2 = (rs3 - ir_dataset[i][0])/rs1
			elif flen == 64:
				rs2 = (Decimal(rs3) - Decimal(ir_dataset[i][0]))/Decimal(rs1)
		elif opcode in 'fmsub':
			if flen == 32:
				rs2 = (ir_dataset[i][0] + rs3)/rs1
			elif flen == 64:
				rs2 = (Decimal(ir_dataset[i][0]) + Decimal(rs3))/Decimal(rs1)
		elif opcode in 'fnmsub':
			if flen == 32:
				rs2 = -1*(rs3 + ir_dataset[i][0])/rs1
			elif flen == 64:
				rs2 = -1*(Decimal(rs3) + Decimal(ir_dataset[i][0]))/Decimal(rs1)
			
		if(flen==32):
			x1 = struct.unpack('f', struct.pack('f', rs1))[0]
			x2 = struct.unpack('f', struct.pack('f', rs2))[0]
			x3 = struct.unpack('f', struct.pack('f', rs3))[0]
		elif(flen==64):
			x1 = rs1
			x2 = rs2
			x3 = rs3
		
		if opcode in ['fadd','fsub','fmul','fdiv']:
			b5_comb.append((floatingPoint_tohex(flen,float(rs1)),floatingPoint_tohex(flen,float(rs2))))
		elif opcode in 'fsqrt':
			b5_comb.append((floatingPoint_tohex(flen,float(rs2)),))
		elif opcode in ['fmadd','fnmadd','fmsub','fnmsub']:
			b5_comb.append((floatingPoint_tohex(flen,float(rs1)),floatingPoint_tohex(flen,float(rs2)),floatingPoint_tohex(flen,float(rs3))))
		
	coverpoints = []
	k = 0	
	for c in b5_comb:
		for rm in range(5):
			cvpt = ""
			for x in range(1, ops+1):
#            			cvpt += 'rs'+str(x)+'_val=='+str(c[x-1]) # uncomment this if you want rs1_val instead of individual fields
				cvpt += (extract_fields(flen,c[x-1],str(x)))
				cvpt += " and "
			cvpt += 'rm == '+str(rm)
			cvpt += ' # '
			for y in range(1, ops+1):
				cvpt += 'rs'+str(y)+'_val=='
				cvpt += num_explain(flen, c[y-1]) + '(' + str(c[y-1]) + ')'
				if(y != ops):
					cvpt += " and "
			cvpt += ir_dataset[k][1]
			coverpoints.append(cvpt)
		k=k+1
	
	mess='Generated'+ (' '*(5-len(str(len(coverpoints)))))+ str(len(coverpoints)) +' '+ (str(32) if flen == 32 else str(64)) + '-bit coverpoints using Model B5 for '+opcode+' !'
	logger.info(mess)
	return coverpoints

def ibm_b6(flen, opcode, ops, seed=-1):
	'''
	This model tests intermediate results in the space between –MinSubNorm and +MinSubNorm. 
	For each of the following ranges, we select 8 random test cases, one for every combination 
	of the LSB, guard bit, and sticky bit.
	i. -MinSubNorm < intermediate < -MinSubNorm / 2
	ii. -MinSubNorm / 2 <= intermediate < 0
	iii. 0 < intermediate <= +MinSubNorm / 2
	iv. +MinSubNorm / 2 < intermediate < +MinSubNorm
	'''
	opcode = opcode.split('.')[0]
	getcontext().prec = 40
	
	if seed == -1:
		if opcode in 'fmul':
			random.seed(0)
		elif opcode in 'fdiv':
			random.seed(1)
		elif opcode in 'fmadd':
			random.seed(2)
		elif opcode in 'fnmadd':
			random.seed(3)
		elif opcode in 'fmsub':
			random.seed(4)
		elif opcode in 'fnmsub':
			random.seed(5)
	else:
		random.seed(seed)
	
	if flen == 32:
		ir_dataset = []
		ieee754_minsubnorm_n = '-0x0.000001p-127'
		minnum = float.fromhex(ieee754_minsubnorm_n)
		r=str(random.uniform(minnum,minnum/2))
		for i in range(2,16,2):
			grs = '{:04b}'.format(i)
			ir_dataset.append([str(Decimal(r.split('e')[0])+Decimal(pow(i*16,-7)))+'e'+r.split('e')[1],' | Guard = '+grs[0]+' Round = '+grs[1]+' Sticky = '+grs[2]+' --> IR ∈ (-MinSubNorm, -MinSubNorm / 2)'])
		r=str(random.uniform(minnum/2,0))
		for i in range(2,16,2):
			grs = '{:04b}'.format(i)
			ir_dataset.append([str(Decimal(r.split('e')[0])+Decimal(pow(i*16,-7)))+'e'+r.split('e')[1],' | Guard = '+grs[0]+' Round = '+grs[1]+' Sticky = '+grs[2]+' --> IR ∈ (-MinSubNorm / 2, 0)'])
		r=str(random.uniform(0,abs(minnum/2)))
		for i in range(2,16,2):
			grs = '{:04b}'.format(i)
			ir_dataset.append([str(Decimal(r.split('e')[0])+Decimal(pow(i*16,-7)))+'e'+r.split('e')[1],' | Guard = '+grs[0]+' Round = '+grs[1]+' Sticky = '+grs[2]+' --> IR ∈ (0, +MinSubNorm / 2)'])
		r=str(random.uniform(abs(minnum/2),abs(minnum)))
		for i in range(2,16,2):
			grs = '{:04b}'.format(i)
			ir_dataset.append([str(Decimal(r.split('e')[0])+Decimal(pow(i*16,-7)))+'e'+r.split('e')[1],' | Guard = '+grs[0]+' Round = '+grs[1]+' Sticky = '+grs[2]+' --> IR ∈ (+MinSubNorm / 2, +MinSubNorm)'])
	elif flen == 64:
		ir_dataset = []
		ieee754_minsubnorm_n = '-0x0.0000000000001p-1022'
		minnum = float.fromhex(ieee754_minsubnorm_n)
		r=str("{:.2e}".format(random.uniform(minnum,minnum/2)))
		for i in range(2,16,2):
			grs = '{:04b}'.format(i)
			ir_dataset.append([str(Decimal(r.split('e')[0])+Decimal(pow(i*16,-14))),' | Guard = '+grs[0]+' Round = '+grs[1]+' Sticky = '+grs[2]+' --> IR ∈ (-MinSubNorm, -MinSubNorm / 2)'])
		r=str("{:.2e}".format(random.uniform(minnum/2,0)))
		for i in range(2,16,2):
			grs = '{:04b}'.format(i)
			ir_dataset.append([str(Decimal(r.split('e')[0])+Decimal(pow(i*16,-14))),' | Guard = '+grs[0]+' Round = '+grs[1]+' Sticky = '+grs[2]+' --> IR ∈ (-MinSubNorm / 2, 0)'])
		r=str("{:.2e}".format(random.uniform(0,abs(minnum/2))))
		for i in range(2,16,2):
			grs = '{:04b}'.format(i)
			ir_dataset.append([str(Decimal(r.split('e')[0])+Decimal(pow(i*16,-14))),' | Guard = '+grs[0]+' Round = '+grs[1]+' Sticky = '+grs[2]+' --> IR ∈ (0, +MinSubNorm / 2)'])
		r=str("{:.2e}".format(random.uniform(abs(minnum/2),abs(minnum))))
		for i in range(2,16,2):
			grs = '{:04b}'.format(i)
			ir_dataset.append([str(Decimal(r.split('e')[0])+Decimal(pow(i*16,-14))),' | Guard = '+grs[0]+' Round = '+grs[1]+' Sticky = '+grs[2]+' --> IR ∈ (+MinSubNorm / 2, +MinSubNorm)'])
	
	b6_comb = []
	
	for i in range(len(ir_dataset)):
		rs1 = random.uniform(0,1e-30)
		rs3 = random.uniform(0,1e-30)
		
		if opcode in 'fmul':
				rs2 = Decimal(ir_dataset[i][0])/Decimal(rs1)
		elif opcode in 'fdiv':
				rs2 = Decimal(rs1)/Decimal(ir_dataset[i][0])
		elif opcode in 'fmadd':
				rs2 = (Decimal(ir_dataset[i][0]) - Decimal(rs3))/Decimal(rs1)
		elif opcode in 'fnmadd':
				rs2 = (Decimal(rs3) - Decimal(ir_dataset[i][0]))/Decimal(rs1)
		elif opcode in 'fmsub':
				rs2 = (Decimal(ir_dataset[i][0]) + Decimal(rs3))/Decimal(rs1)
		elif opcode in 'fnmsub':
				rs2 = -1*(Decimal(rs3) + Decimal(ir_dataset[i][0]))/Decimal(rs1)
		
		if(flen==32):
			x1 = struct.unpack('f', struct.pack('f', rs1))[0]
			x2 = struct.unpack('f', struct.pack('f', rs2))[0]
			x3 = struct.unpack('f', struct.pack('f', rs3))[0]
		elif(flen==64):
			x1 = rs1
			x2 = rs2
			x3 = rs3
		
		if opcode in ['fmul','fdiv']:
			b6_comb.append((floatingPoint_tohex(flen,float(rs1)),floatingPoint_tohex(flen,float(rs2))))
		elif opcode in ['fmadd','fnmadd','fmsub','fnmsub']:
			b6_comb.append((floatingPoint_tohex(flen,float(rs1)),floatingPoint_tohex(flen,float(rs2)),floatingPoint_tohex(flen,float(rs3))))
	
	#print(*b6_comb,sep='\n')	
	coverpoints = []	
	k=0
	
	for c in b6_comb:
		for rm in range(5):
			cvpt = ""
			for x in range(1, ops+1):
#            			cvpt += 'rs'+str(x)+'_val=='+str(c[x-1]) # uncomment this if you want rs1_val instead of individual fields
				cvpt += (extract_fields(flen,c[x-1],str(x)))
				cvpt += " and "
			cvpt += 'rm == '+str(rm)
			cvpt += ' # '
			for y in range(1, ops+1):
				cvpt += 'rs'+str(y)+'_val=='
				cvpt += num_explain(flen, c[y-1]) + '(' + str(c[y-1]) + ')'
				if(y != ops):
					cvpt += " and "
			cvpt += ir_dataset[k][1]
			coverpoints.append(cvpt)
		k=k+1
	
	mess='Generated'+ (' '*(5-len(str(len(coverpoints)))))+ str(len(coverpoints)) +' '+ (str(32) if flen == 32 else str(64)) + '-bit coverpoints using Model B6 for '+opcode+' !'
	logger.info(mess)
	return coverpoints
	
def ibm_b7(flen, opcode, ops, seed=-1):
	'''
	This model checks that the sticky bit is calculated correctly in each of the
	following cases (for every possible combination in the table). The Guard bit
	should be always 0, and the sign positive, so that miscalculation of the sticky bit
	will alter the final result.
	Mask on Extra Bits
	1000...000
	0100...000
	...
	0000...010
	0000...001
	0000000000
	'''
	opcode = opcode.split('.')[0]
	getcontext().prec = 60
	if flen == 32:
		ieee754_maxnorm = '0x1.7fffffp+127'
		maxnum = float.fromhex(ieee754_maxnorm)
		ieee754_num = []
		for i in fsubnorm+fnorm:
			float_val = float.hex(fields_dec_converter(32,i))
			if float_val[0] != '-':
				ieee754_num.append(float_val.split('p')[0][0:10]+'p'+float_val.split('p')[1])
		ir_dataset = []
		for k in range(len(ieee754_num)):
			for i in range(0,20):
				comment = (20-i)*'0' + '1' + i*'0'
				ir_dataset.append([ieee754_num[k].split('p')[0]+hex(int('010'+'{:021b}'.format(pow(2,i)),2))[2:]+'p'+ieee754_num[k].split('p')[1],' | Mask on extra bits ---> ' + comment])
		n = len(ir_dataset)
		for i in range(n):
			ir_dataset[i][0] = float.fromhex(ir_dataset[i][0])
		
	elif flen == 64:
		maxdec = '1.7976931348623157e+308'
		maxnum = float.fromhex('0x1.fffffffffffffp+1023')
		ieee754_num = []
		for i in dsubnorm+dnorm:
			float_val = fields_dec_converter(64,i)
			if float_val > 0:
				ieee754_num.append(str(float_val))
			
		ir_dataset = []
		for l in range(len(ieee754_num)):
			for k in range(1,13):
				for i in range(4):
					comment = (k*(i+1))*'0' + '1' + (51-(k*(i+1)))*'0'
					ir_dataset.append([str(Decimal(ieee754_num[l].split('e')[0])+Decimal(pow(16,-14))+Decimal(pow(pow(2,3-i)*16,-14-k)))+'e'+ieee754_num[l].split('e')[1],' | Mask on extra bits ---> ' + comment])
	
	if seed == -1:
		if opcode in 'fadd':
			random.seed(0)
		elif opcode in 'fsub':
			random.seed(1)
		elif opcode in 'fmul':
			random.seed(2)
		elif opcode in 'fdiv':
			random.seed(3)
		elif opcode in 'fsqrt':
			random.seed(4)
		elif opcode in 'fmadd':
			random.seed(5)
		elif opcode in 'fnmadd':
			random.seed(6)
		elif opcode in 'fmsub':
			random.seed(7)
		elif opcode in 'fnmsub':
			random.seed(8)
	else:
		random.seed(seed)
	
	b7_comb = []
			
	for i in range(len(ir_dataset)):
		rs1 = random.uniform(1,maxnum)
		rs3 = random.uniform(1,maxnum)
		if opcode in 'fadd':
			if flen == 32:
				rs2 = ir_dataset[i][0] - rs1
			elif flen == 64:
				rs2 = Decimal(ir_dataset[i][0]) - Decimal(rs1)
		elif opcode in 'fsub':
			if flen == 32:
				rs2 = rs1 - ir_dataset[i][0]
			elif flen == 64:
				rs2 = Decimal(rs1) - Decimal(ir_dataset[i][0])
		elif opcode in 'fmul':
			if flen == 32:
				rs2 = ir_dataset[i][0]/rs1
			elif flen == 64:
				rs2 = Decimal(ir_dataset[i][0])/Decimal(rs1)
		elif opcode in 'fdiv':
			if flen == 32:
				rs2 = rs1/ir_dataset[i][0]
			elif flen == 64:
				rs2 = Decimal(rs1)/Decimal(ir_dataset[i][0])
		elif opcode in 'fsqrt':
			if flen == 32:
				rs2 = ir_dataset[i][0]*ir_dataset[i][0]
			elif flen == 64:
				rs2 = Decimal(ir_dataset[i][0])*Decimal(ir_dataset[i][0])
		elif opcode in 'fmadd':
			if flen == 32:
				rs2 = (ir_dataset[i][0] - rs3)/rs1
			elif flen == 64:
				rs2 = (Decimal(ir_dataset[i][0]) - Decimal(rs3))/Decimal(rs1)
		elif opcode in 'fnmadd':
			if flen == 32:
				rs2 = (rs3 - ir_dataset[i][0])/rs1
			elif flen == 64:
				rs2 = (Decimal(rs3) - Decimal(ir_dataset[i][0]))/Decimal(rs1)
		elif opcode in 'fmsub':
			if flen == 32:
				rs2 = (ir_dataset[i][0] + rs3)/rs1
			elif flen == 64:
				rs2 = (Decimal(ir_dataset[i][0]) + Decimal(rs3))/Decimal(rs1)
		elif opcode in 'fnmsub':
			if flen == 32:
				rs2 = -1*(rs3 + ir_dataset[i][0])/rs1
			elif flen == 64:
				rs2 = -1*(Decimal(rs3) + Decimal(ir_dataset[i][0]))/Decimal(rs1)
			
		if(flen==32):
			x1 = struct.unpack('f', struct.pack('f', rs1))[0]
			x2 = struct.unpack('f', struct.pack('f', rs2))[0]
			x3 = struct.unpack('f', struct.pack('f', rs3))[0]
		elif(flen==64):
			x1 = rs1
			x2 = rs2
			x3 = rs3
		
		if opcode in ['fadd','fsub','fmul','fdiv']:
			b7_comb.append((floatingPoint_tohex(flen,float(rs1)),floatingPoint_tohex(flen,float(rs2))))
		elif opcode in 'fsqrt':
			b7_comb.append((floatingPoint_tohex(flen,float(rs2)),))
		elif opcode in ['fmadd','fnmadd','fmsub','fnmsub']:
			b7_comb.append((floatingPoint_tohex(flen,float(rs1)),floatingPoint_tohex(flen,float(rs2)),floatingPoint_tohex(flen,float(rs3))))
		
	coverpoints = []
	k = 0	
	for c in b7_comb:
		cvpt = ""
		for x in range(1, ops+1):
#           			cvpt += 'rs'+str(x)+'_val=='+str(c[x-1]) # uncomment this if you want rs1_val instead of individual fields
			cvpt += (extract_fields(flen,c[x-1],str(x)))
			cvpt += " and "
		cvpt += 'rm == 3'
		cvpt += ' # '
		for y in range(1, ops+1):
			cvpt += 'rs'+str(y)+'_val=='
			cvpt += num_explain(flen, c[y-1]) + '(' + str(c[y-1]) + ')'
			if(y != ops):
				cvpt += " and "
		cvpt += ir_dataset[k][1]
		coverpoints.append(cvpt)
		k=k+1
	
	mess='Generated'+ (' '*(5-len(str(len(coverpoints)))))+ str(len(coverpoints)) +' '+ (str(32) if flen == 32 else str(64)) + '-bit coverpoints using Model B7 for '+opcode+' !'
	logger.info(mess)
	return coverpoints
	
def ibm_b8(flen, opcode, ops, seed=-1):
	'''
	This model targets numbers that are on the edge of a rounding boundary. These
	boundaries may vary depending on the rounding mode. These numbers include
	floating-point numbers and mid-points between floating-point numbers. In order
	to target the vicinity of these numbers, we test the following constraints on the
	extra bits of the intermediate result:
	i. All values of extra-bits in the range [000...00001, 000...00011]
	ii. All values of extra-bits in the range [111...11100, 111...11111]
	For each value selected above, test all the combinations on the LSB of the
	significand, the guard bit, and the sticky bit (if the number of extra bits is not
	finite).
	'''
	opcode = opcode.split('.')[0]
	getcontext().prec = 60
	if flen == 32:
		ieee754_maxnorm = '0x1.7fffffp+127'
		maxnum = float.fromhex(ieee754_maxnorm)
		ieee754_num = []
		for i in fsubnorm+fnorm:
			float_val = float.hex(fields_dec_converter(32,i))
			if float_val[0] != '-':
				ieee754_num.append(float_val.split('p')[0][0:10]+'p'+float_val.split('p')[1])
		ir_dataset = []
		for k in range(len(ieee754_num)):
			for i in range(1,4):
				for j in range(1,8):
					grs = '{:03b}'.format(j)
					ir_dataset.append([ieee754_num[k].split('p')[0]+hex(int('{:03b}'.format(j)+19*'0'+'{:02b}'.format(i),2))[2:]+'p'+ieee754_num[k].split('p')[1],' | Guard = '+grs[0]+' Round = '+grs[1]+' Sticky = '+grs[2]+' --> Mask On Extra Bits: '+19*'0'+'{:02b}'.format(i)])
					ir_dataset.append([ieee754_num[k].split('p')[0]+hex(int('{:03b}'.format(j)+19*'1'+'{:02b}'.format(i),2))[2:]+'p'+ieee754_num[k].split('p')[1],' | Guard = '+grs[0]+' Round = '+grs[1]+' Sticky = '+grs[2]+' --> Mask On Extra Bits: '+19*'1'+'{:02b}'.format(i)])
		n = len(ir_dataset)
		for i in range(n):
			ir_dataset[i][0] = float.fromhex(ir_dataset[i][0])
			
	elif flen == 64:
		maxdec = '1.7976931348623157e+308'
		maxnum = float.fromhex('0x1.fffffffffffffp+1023')
		ieee754_num = []
		for i in dsubnorm+dnorm:
			float_val = float.hex(fields_dec_converter(64,i))
			if float_val[0] != '-':
				ieee754_num.append(float_val.split('p')[0][0:17]+'p'+float_val.split('p')[1])
		ir_dataset = []
		for k in range(len(ieee754_num)):
			for i in range(1,4):
				for j in range(1,8):
					grs = '{:03b}'.format(j)
					ir_dataset.append([ieee754_num[k].split('p')[0]+hex(int('010'+19*'0'+'{:02b}'.format(i),2))[2:]+'p'+ieee754_num[k].split('p')[1],' | Guard = '+grs[0]+' Round = '+grs[1]+' Sticky = '+grs[2]+' --> Mask On Extra Bits: '+19*'0'+'{:02b}'.format(i)])
					ir_dataset.append([ieee754_num[k].split('p')[0]+hex(int('010'+19*'1'+'{:02b}'.format(i),2))[2:]+'p'+ieee754_num[k].split('p')[1],' | Guard = '+grs[0]+' Round = '+grs[1]+' Sticky = '+grs[2]+' --> Mask On Extra Bits: '+19*'1'+'{:02b}'.format(i)])
		n = len(ir_dataset)
		for i in range(n):
			ir_dataset[i][0] = float.fromhex(ir_dataset[i][0])

	if seed == -1:
		if opcode in 'fadd':
			random.seed(0)
		elif opcode in 'fsub':
			random.seed(1)
		elif opcode in 'fmul':
			random.seed(2)
		elif opcode in 'fdiv':
			random.seed(3)
		elif opcode in 'fsqrt':
			random.seed(4)
		elif opcode in 'fmadd':
			random.seed(5)
		elif opcode in 'fnmadd':
			random.seed(6)
		elif opcode in 'fmsub':
			random.seed(7)
		elif opcode in 'fnmsub':
			random.seed(8)
	else:
		random.seed(seed)
	
	b8_comb = []
			
	for i in range(len(ir_dataset)):
		rs1 = random.uniform(1,ir_dataset[i][0])
		rs3 = random.uniform(1,ir_dataset[i][0])
		if opcode in 'fadd':
			if flen == 32:
				rs2 = ir_dataset[i][0] - rs1
			elif flen == 64:
				rs2 = Decimal(ir_dataset[i][0]) - Decimal(rs1)
		elif opcode in 'fsub':
			if flen == 32:
				rs2 = rs1 - ir_dataset[i][0]
			elif flen == 64:
				rs2 = Decimal(rs1) - Decimal(ir_dataset[i][0])
		elif opcode in 'fmul':
			if flen == 32:
				rs2 = ir_dataset[i][0]/rs1
			elif flen == 64:
				rs2 = Decimal(ir_dataset[i][0])/Decimal(rs1)
		elif opcode in 'fdiv':
			if flen == 32:
				rs2 = rs1/ir_dataset[i][0]
			elif flen == 64:
				rs2 = Decimal(rs1)/Decimal(ir_dataset[i][0])
		elif opcode in 'fsqrt':
			if flen == 32:
				rs2 = ir_dataset[i][0]*ir_dataset[i][0]
			elif flen == 64:
				rs2 = Decimal(ir_dataset[i][0])*Decimal(ir_dataset[i][0])
		elif opcode in 'fmadd':
			if flen == 32:
				rs2 = (ir_dataset[i][0] - rs3)/rs1
			elif flen == 64:
				rs2 = (Decimal(ir_dataset[i][0]) - Decimal(rs3))/Decimal(rs1)
		elif opcode in 'fnmadd':
			if flen == 32:
				rs2 = (rs3 - ir_dataset[i][0])/rs1
			elif flen == 64:
				rs2 = (Decimal(rs3) - Decimal(ir_dataset[i][0]))/Decimal(rs1)
		elif opcode in 'fmsub':
			if flen == 32:
				rs2 = (ir_dataset[i][0] + rs3)/rs1
			elif flen == 64:
				rs2 = (Decimal(ir_dataset[i][0]) + Decimal(rs3))/Decimal(rs1)
		elif opcode in 'fnmsub':
			if flen == 32:
				rs2 = -1*(rs3 + ir_dataset[i][0])/rs1
			elif flen == 64:
				rs2 = -1*(Decimal(rs3) + Decimal(ir_dataset[i][0]))/Decimal(rs1)
			
		if(flen==32):
			x1 = struct.unpack('f', struct.pack('f', rs1))[0]
			x2 = struct.unpack('f', struct.pack('f', rs2))[0]
			x3 = struct.unpack('f', struct.pack('f', rs3))[0]
		elif(flen==64):
			x1 = rs1
			x2 = rs2
			x3 = rs3
		
		if opcode in ['fadd','fsub','fmul','fdiv']:
			b8_comb.append((floatingPoint_tohex(flen,float(rs1)),floatingPoint_tohex(flen,float(rs2))))
		elif opcode in 'fsqrt':
			b8_comb.append((floatingPoint_tohex(flen,float(rs2)),))
		elif opcode in ['fmadd','fnmadd','fmsub','fnmsub']:
			b8_comb.append((floatingPoint_tohex(flen,float(rs1)),floatingPoint_tohex(flen,float(rs2)),floatingPoint_tohex(flen,float(rs3))))
		
	coverpoints = []
	k=0
	for c in b8_comb:
		for rm in range(5):
			cvpt = ""
			for x in range(1, ops+1):
#            			cvpt += 'rs'+str(x)+'_val=='+str(c[x-1]) # uncomment this if you want rs1_val instead of individual fields
				cvpt += (extract_fields(flen,c[x-1],str(x)))
				cvpt += " and "
			cvpt += 'rm == '+str(rm)
			cvpt += ' # '
			for y in range(1, ops+1):
				cvpt += 'rs'+str(y)+'_val=='
				cvpt += num_explain(flen, c[y-1]) + '(' + str(c[y-1]) + ')'
				if(y != ops):
					cvpt += " and "
			cvpt += ir_dataset[k][1]
			coverpoints.append(cvpt)
		k=k+1
	
	mess='Generated'+ (' '*(5-len(str(len(coverpoints)))))+ str(len(coverpoints)) +' '+ (str(32) if flen == 32 else str(64)) + '-bit coverpoints using Model B8 for '+opcode+' !'
	logger.info(mess)
	return coverpoints

def ibm_b9(flen, opcode, ops):
	'''
	This model tests special patterns in the significands of the input operands. Each
	of the input operands should contain one of the following patterns (each
	sequence can be of length 0 up to the number of bits in the significand – the
	more interesting cases will be chosen).
	i. A sequence of leading zeroes
	ii. A sequence of leading ones
	iii. A sequence of trailing zeroes
	iv. A sequence of trailing ones
	v. A small number of 1s as compared to 0s
	vi. A small number of 0s as compared to 1s
	vii. A "checkerboard" pattern (for example 00110011… or 011011011…)
	viii.Long sequences of 1s
	ix. Long sequences of 0s
	'''
	opcode = opcode.split('.')[0]
	
	if flen == 32:
		flip_types = fzero + fone + fminsubnorm + fmaxsubnorm + fminnorm + fmaxnorm
		e_sz=8
	elif flen == 64:
		flip_types = dzero + done + dminsubnorm + dmaxsubnorm + dminnorm + dmaxnorm
		e_sz=11
		
	rs1 = []
	b9_comb = []
	comment = []
	if ops == 2:
		for i in range(len(flip_types)):
			rs1.append(flip_types[i])
		for i in range(len(rs1)):
			bin_val = bin(int('1'+rs1[i][2:],16))[3:]
			rs1_sgn = bin_val[0]
			rs1_exp = bin_val[1:e_sz+1]
			rs1_man = bin_val[e_sz+1:]
			
			for j in range(len(rs1_man)):
				rs2_sgn = rs1_sgn                 
				rs2_exp = rs1_exp
				rs2_man = '0'*j + rs1_man[j:]                        # Leading 0s
				rs2 = fields_dec_converter(32,'0x'+hex(int('1'+rs2_sgn+rs2_exp+rs2_man,2))[3:])
				b9_comb.append((rs1[i],floatingPoint_tohex(flen,rs2)))
				comment.append(' | Leading zeroes ---> rs2_man = '+rs2_man)
				b9_comb.append((floatingPoint_tohex(flen,rs2),rs1[i]))
				comment.append(' | Leading zeroes ---> rs1_man = '+rs2_man)
					
				rs2_man = '1'*j + '0'*(len(rs1_man)-j)                        # Leading 1s
				rs2 = fields_dec_converter(32,'0x'+hex(int('1'+rs2_sgn+rs2_exp+rs2_man,2))[3:])
				b9_comb.append((rs1[i],floatingPoint_tohex(flen,rs2)))
				comment.append(' | Leading ones ---> rs2_man = '+rs2_man)
				b9_comb.append((floatingPoint_tohex(flen,rs2),rs1[i]))
				comment.append(' | Leading ones ---> rs1_man = '+rs2_man)
				
				rs2_man = rs1_man[0:j] + '0'*(len(rs1_man)-j)        # Trailing 0s
				rs2 = fields_dec_converter(32,'0x'+hex(int('1'+rs2_sgn+rs2_exp+rs2_man,2))[3:])
				b9_comb.append((rs1[i],floatingPoint_tohex(flen,rs2)))
				comment.append(' | Trailing zeroes ---> rs2_man = '+rs2_man)
				b9_comb.append((floatingPoint_tohex(flen,rs2),rs1[i]))
				comment.append(' | Trailing zeroes ---> rs1_man = '+rs2_man)
				
				rs2_man = '0'*j + '1'*(len(rs1_man)-j)        # Trailing 1s
				rs2 = fields_dec_converter(32,'0x'+hex(int('1'+rs2_sgn+rs2_exp+rs2_man,2))[3:])
				b9_comb.append((rs1[i],floatingPoint_tohex(flen,rs2)))
				comment.append(' | Trailing ones ---> rs2_man = '+rs2_man)
				b9_comb.append((floatingPoint_tohex(flen,rs2),rs1[i]))
				comment.append(' | Trailing ones ---> rs1_man = '+rs2_man)
				
			for j in range(len(rs1_man)-math.ceil(0.1*len(rs1_man)),len(rs1_man)):
				rs2_sgn = rs1_sgn
				rs2_exp = rs1_exp
				rs2_man = '1'*j + '0'*(len(rs1_man)-j)                        # Long sequence of 1s
				rs2 = fields_dec_converter(32,'0x'+hex(int('1'+rs2_sgn+rs2_exp+rs2_man,2))[3:])
				b9_comb.append((rs1[i],floatingPoint_tohex(flen,rs2)))
				comment.append(' | Long sequence of ones ---> rs2_man = '+rs2_man)
				b9_comb.append((floatingPoint_tohex(flen,rs2),rs1[i]))
				comment.append(' | Long sequence of ones ---> rs1_man = '+rs2_man)
				
				rs2_man = '0'*j + '1'*(len(rs1_man)-j)                        # Long sequence of 0s
				rs2 = fields_dec_converter(32,'0x'+hex(int('1'+rs2_sgn+rs2_exp+rs2_man,2))[3:])
				b9_comb.append((rs1[i],floatingPoint_tohex(flen,rs2)))
				comment.append(' | Long sequence of zeroes ---> rs2_man = '+rs2_man)
				b9_comb.append((floatingPoint_tohex(flen,rs2),rs1[i]))
				comment.append(' | Long sequence of zeroes ---> rs1_man = '+rs2_man)
			
			chkrbrd = ['011','110','0011','1100','0111','1000','010','101','0110','1001']
			for j in chkrbrd:
				rs2_sgn = rs1_sgn
				rs2_exp = rs1_exp
				rs2_man = j
				for k in range(math.ceil(len(rs1_man)/len(j))):
					rs2_man += j
				rs2_man = rs2_man[0:flen-e_sz-1]
				rs2 = fields_dec_converter(32,'0x'+hex(int('1'+rs2_sgn+rs2_exp+rs2_man,2))[3:])
				b9_comb.append((rs1[i],floatingPoint_tohex(flen,rs2)))
				comment.append(' | Checkerboard pattern ---> rs2_man = '+rs2_man)
				b9_comb.append((floatingPoint_tohex(flen,rs2),rs1[i]))
				comment.append(' | Checkerboard pattern ---> rs1_man = '+rs2_man)
					
	else:
		for i in range(len(flip_types)):
			rs1.append(flip_types[i])
		for i in range(len(rs1)):
			bin_val = bin(int('1'+rs1[i][2:],16))[3:]
			rs1_sgn = bin_val[0]
			rs1_exp = bin_val[1:e_sz+1]
			rs1_man = bin_val[e_sz+1:]
			
			if rs1_sgn != '1':
				for j in range(len(rs1_man)):
					rs2_sgn = rs1_sgn                 
					rs2_exp = rs1_exp
					rs2_man = '0'*j + rs1_man[j:]                        # Leading 0s
					rs2 = fields_dec_converter(32,'0x'+hex(int('1'+rs2_sgn+rs2_exp+rs2_man,2))[3:])
					b9_comb.append((floatingPoint_tohex(flen,rs2),))
					comment.append(' | Leading zeroes ---> rs1_man = '+rs2_man)
				
					rs2_man = '1'*j + '0'*(len(rs1_man)-j)                        # Leading 1s
					rs2 = fields_dec_converter(32,'0x'+hex(int('1'+rs2_sgn+rs2_exp+rs2_man,2))[3:])
					b9_comb.append((floatingPoint_tohex(flen,rs2),))
					comment.append(' | Leading ones ---> rs1_man = '+rs2_man)
					
					rs2_man = rs1_man[0:j] + '0'*(len(rs1_man)-j)        # Trailing 0s
					rs2 = fields_dec_converter(32,'0x'+hex(int('1'+rs2_sgn+rs2_exp+rs2_man,2))[3:])
					b9_comb.append((floatingPoint_tohex(flen,rs2),))
					comment.append(' | Trailing zeroes ---> rs1_man = '+rs2_man)
					
					rs2_man = '0'*j + '1'*(len(rs1_man)-j)        # Trailing 1s
					rs2 = fields_dec_converter(32,'0x'+hex(int('1'+rs2_sgn+rs2_exp+rs2_man,2))[3:])
					b9_comb.append((floatingPoint_tohex(flen,rs2),))
					comment.append(' | Trailing ones ---> rs1_man = '+rs2_man)
		rs1_sgn = '0'	
		for j in range(flen-e_sz-1-math.ceil(0.1*(flen-e_sz-1)), flen-e_sz-1):
			rs2_sgn = rs1_sgn
			rs2_exp = rs1_exp
			rs2_man = '1'*j + '0'*(len(rs1_man)-j)                        # Long sequence of 1s
			rs2 = fields_dec_converter(32,'0x'+hex(int('1'+rs2_sgn+rs2_exp+rs2_man,2))[3:])
			b9_comb.append((floatingPoint_tohex(flen,rs2),))
			comment.append(' | Long sequence of ones ---> rs1_man = '+rs2_man)
			
			rs2_man = '0'*j + '1'*(len(rs1_man)-j)                        # Long sequence of 0s
			rs2 = fields_dec_converter(32,'0x'+hex(int('1'+rs2_sgn+rs2_exp+rs2_man,2))[3:])
			b9_comb.append((floatingPoint_tohex(flen,rs2),))
			comment.append(' | Long sequence of zeroes ---> rs1_man = '+rs2_man)
		
		chkrbrd = ['011','110','0011','1100','0111','1000','010','101','0110','1001']
		for j in chkrbrd:
			rs2_sgn = rs1_sgn
			rs2_exp = rs1_exp
			rs2_man = j
			for k in range(math.ceil(len(rs1_man)/len(j))):
				rs2_man += j
			rs2_man = rs2_man[0:flen-e_sz-1]
			rs2 = fields_dec_converter(32,'0x'+hex(int('1'+rs2_sgn+rs2_exp+rs2_man,2))[3:])
			b9_comb.append((floatingPoint_tohex(flen,rs2),))
			comment.append(' | Checkerboard pattern ---> rs1_man = '+rs2_man)
			
	coverpoints = []
	k = 0
	for c in b9_comb:
		cvpt = ""
		for x in range(1, ops+1):
#            		cvpt += 'rs'+str(x)+'_val=='+str(c[x-1]) # uncomment this if you want rs1_val instead of individual fields
			cvpt += (extract_fields(flen,c[x-1],str(x)))
			cvpt += " and "
		cvpt += 'rm == 0'
		cvpt += ' # '
		for y in range(1, ops+1):
			cvpt += 'rs'+str(y)+'_val=='
			cvpt += num_explain(flen, c[y-1]) + '(' + str(c[y-1]) + ')'
			if(y != ops):
				cvpt += " and "
		cvpt += comment[k]
		coverpoints.append(cvpt)
		k += 1
	
	mess='Generated'+ (' '*(5-len(str(len(coverpoints)))))+ str(len(coverpoints)) +' '+ (str(32) if flen == 32 else str(64)) + '-bit coverpoints using Model B9 for '+opcode+' !'
	logger.info(mess)
	return coverpoints

#x=ibm_b9(32, 'fsqrt.s', 1)
#print(*x, sep='\n')
	
'''
opcode_32 = [('fadd.s',2), ('fsub.s',2), ('fmul.s',2), ('fdiv.s',2), ('fsqrt.s',1), ('fmadd.s',3), ('fnmadd.s',3), ('fmsub.s',3), ('fnmsub.s',3)]
opcode_64 = [('fadd.d',2), ('fsub.d',2), ('fmul.d',2), ('fdiv.d',2), ('fsqrt.d',1), ('fmadd.d',3), ('fnmadd.d',3), ('fmsub.d',3), ('fnmsub.d',3)]

x=ibm_b3(32, 'fadd.s', 2)
print(*x, sep='\n')

for i in range(1,7):
	file1 = open("model_b"+str(i)+".txt","w")
	print("Writing File model_b"+str(i)+".txt")
	for j in range(len(opcode_32)):
		x=eval("ibm_b"+str(i)+"(32, opcode_32[j][0], opcode_32[j][1])")
		file1.write("Opcode: "+opcode_32[j][0]+"\n")
		file1.write("\n")
		for k in range(len(x)):
			file1.write(x[k]+'\n')
		file1.write("\n")
	for j in range(len(opcode_64)):
		x=eval("ibm_b"+str(i)+"(64, opcode_64[j][0], opcode_64[j][1])")
		file1.write("Opcode: "+opcode_64[j][0]+"\n")
		file1.write("\n")
		for k in range(len(x)):
			file1.write(x[k]+'\n')
		file1.write("\n")'''
	
