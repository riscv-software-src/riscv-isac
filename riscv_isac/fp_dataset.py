from riscv_isac.log import logger
import itertools
import random
import sys

fzero_32       = ['0x00000000', '0x80000000']
fminsubnorm_32 = ['0x00000001', '0x80000001']
fsubnorm_32    = ['0x00000002', '0x80000002', '0x007FFFFE', '0x807FFFFE', '0x00555555', '0x80555555']
fmaxsubnorm_32 = ['0x007FFFFF', '0x807FFFFF']
fminnorm_32    = ['0x00800000', '0x80800000']
fnorm_32       = ['0x00800001', '0x80800001', '0x00855555', '0x80855555', '0x008AAAAA', '0x808AAAAA', '0x55000000', '0xD5000000', '0x2A000000', '0xAA000000']
fmaxnorm_32    = ['0x7F7FFFFF', '0xFF7FFFFF']
finfinity_32   = ['0x7F800000', '0xFF800000']
fdefaultnan_32 = ['0x7FC00000', '0xFFC00000']
fqnan_32       = ['0x7FC00001', '0xFFC00001', '0x7FC55555', '0xFFC55555']
fsnan_32       = ['0x7F800001', '0xFF800001', '0x7FAAAAAA', '0xFFAAAAAA']
fone_32        = ['0x3F800000', '0xBF800000']

fzero_64       = ['0x0000000000000000', '0x8000000000000000']
fminsubnorm_64 = ['0x0000000000000001', '0x8000000000000001']
fsubnorm_64    = ['0x0000000000000002', '0x8000000000000002']
fmaxsubnorm_64 = ['0x000FFFFFFFFFFFFF', '0x800FFFFFFFFFFFFF']
fminnorm_64    = ['0x0010000000000000', '0x8010000000000000']
fnorm_64       = ['0x0010000000000002', '0x8010000000000002']
fmaxnorm_64    = ['0x7FEFFFFFFFFFFFFF', '0xFFEFFFFFFFFFFFFF']
finfinity_64   = ['0x7FF0000000000000', '0xFFF0000000000000']
fdefaultnan_64 = ['0x7FF8000000000000', '0xFFF8000000000000']
fqnan_64       = ['0x7FF8000000000001', '0xFFF8000000000001']
fsnan_64       = ['0x7FF0000000000001', '0xFFF0000000000001']
fone_64        = ['0x3FF0000000000000', '0xBF80000000000000']

rounding_modes = ['0','1','2','3','4']

def num_explain(num):
	num_dict = {
		tuple(fzero_32) 	: 'fzero_32',
		tuple(fminsubnorm_32) 	: 'fminsubnorm_32',
		tuple(fsubnorm_32) 	: 'fsubnorm_32',
		tuple(fmaxsubnorm_32) 	: 'fmaxsubnorm_32',
		tuple(fminnorm_32) 	: 'fminnorm_32',
		tuple(fnorm_32) 	: 'fnorm_32',
		tuple(fmaxnorm_32) 	: 'fmaxnorm_32',
		tuple(finfinity_32) 	: 'finfinity_32',
		tuple(fdefaultnan_32) 	: 'fdefaultnan_32',
		tuple(fqnan_32) 	: 'fqnan_32',
		tuple(fsnan_32) 	: 'fsnan_32',
		tuple(fone_32) 	: 'fone_32',
		tuple(fzero_64) 	: 'fzero_64',
		tuple(fminsubnorm_64) 	: 'fminsubnorm_64',
		tuple(fsubnorm_64) 	: 'fsubnorm_64',
		tuple(fmaxsubnorm_64) 	: 'fmaxsubnorm_64',
		tuple(fminnorm_64) 	: 'fminnorm_64',
		tuple(fnorm_64) 	: 'fnorm_64',
		tuple(fmaxnorm_64) 	: 'fmaxnorm_64',
		tuple(finfinity_64) 	: 'finfinity_64',
		tuple(fdefaultnan_64) 	: 'fdefaultnan_64',
		tuple(fqnan_64) 	: 'fqnan_64',
		tuple(fsnan_64) 	: 'fsnan_64',
		tuple(fone_64) 	: 'fone_64',
	}
	num_list = list(num_dict.items())
	for i in range(len(num_list)):
		if(num in num_list[i][0]):
			return(num_list[i][1])

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

    string = 'fs'+postfix+' == '+str(sgn) +\
            ' and fe'+postfix+' == '+str(hex(int(exp,2))) +\
            ' and fm'+postfix+' == '+str(hex(int(man,2)))

    return string

def ibm_b1(flen, ops):
    '''
    Test all combinations of floating-point basic types, positive and negative, for
    each of the inputs. The basic types are Zero, One, MinSubNorm, SubNorm,
    MaxSubNorm, MinNorm, Norm, MaxNorm, Infinity, DefaultNaN, QNaN, and
    SNaN.
    '''
    if flen == 32:
        basic_types = fzero_32 + fminsubnorm_32 + [fsubnorm_32[0], fsubnorm_32[3]] +\
            fmaxsubnorm_32 + fminnorm_32 + [fnorm_32[0], fnorm_32[3]] + fmaxnorm_32 + \
            finfinity_32 + fdefaultnan_32 + [fqnan_32[0], fqnan_32[3]] + \
            [fsnan_32[0], fsnan_32[3]] + fone_32
    elif flen == 64:
    	basic_types = fzero_64 + fminsubnorm_64 + [fsubnorm_64[0], fsubnorm_64[1]] +\
            fmaxsubnorm_64 + fminnorm_64 + [fnorm_64[0], fnorm_64[1]] + fmaxnorm_64 + \
            finfinity_64 + fdefaultnan_64 + [fqnan_64[0], fqnan_64[1]] + \
            [fsnan_64[0], fsnan_64[1]] + fone_64
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
        cvpt += "rm == 0 #"
        for y in range(1, ops+1):
            cvpt += 'rs'+str(y)+'_val=='
            cvpt += num_explain(c[y-1]) + '(' + str(c[y-1]) + ')'
            if(y != ops):
            	cvpt += " and "
        coverpoints.append(cvpt)
    
    mess='Generated '+ str(len(coverpoints)) +' '+ (str(32) if flen == 32 else str(64)) + '-bit coverpoints using Model B1!'
    logger.info(mess)
    
    return coverpoints
    
def ibm_b2(flen, ops):
	'''
	This model tests final results that are very close, measured in Hamming distance,
	to the specified boundary values. Each boundary value is taken as a base value, 
	and the model enumerates over small deviations from the base, by flipping one bit 
	of the significand.
	'''
	if flen == 32:
		flip_types = fzero_32 + fone_32 + fminsubnorm_32 + fmaxsubnorm_32 + fminnorm_32 + fmaxnorm_32
		b = '0x00000001'
	elif flen == 64:
		flip_types = fzero_64 + fone_64 + fminsubnorm_64 + fmaxsubnorm_64 + fminnorm_64 + fmaxnorm_64
		b = '0x0000000000000001'
		
	result = []
	for i in range(len(flip_types)):
		result.append('0x' + hex(int('1'+flip_types[i][2:], 16) ^ int(b[2:], 16))[3:])
		
	# the following creates a cross product for ops number of variables
	b2_comm = list(itertools.product(*ops*[flip_types]))
	b2_comb = list(itertools.product(*ops*[result]))
	coverpoints = []
	for c,d in zip(b2_comb,b2_comm):
		cvpt = ""
		for x in range(1, ops+1):
#            cvpt += 'rs'+str(x)+'_val=='+str(c[x-1]) # uncomment this if you want rs1_val instead of individual fields
			cvpt += (extract_fields(flen,c[x-1],str(x)))
			cvpt += " and "
		cvpt += "rm == 0 #"
		for y in range(1, ops+1):
			cvpt += 'rs'+str(y)+'_val=='
			cvpt += 'Flipped Last Bit of '+ num_explain(d[y-1]) + '(' + str(c[y-1]) + ')'
			if(y != ops):
				cvpt += " and "
		coverpoints.append(cvpt)
		
	mess='Generated '+ str(len(coverpoints)) +' '+ (str(32) if flen == 32 else str(64)) + '-bit coverpoints using Model B2!'
	logger.info(mess)

	return coverpoints
	
