from riscv_isac.log import logger
import itertools
import random
import sys

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
rounding_modes = ['0','1','2','3','4']

def num_explain(num):
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
		tuple(fone) 		: 'fone'
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
        basic_types = fzero + fminsubnorm + [fsubnorm[0], fsubnorm[3]] +\
            fmaxsubnorm + fminnorm + [fnorm[0], fnorm[3]] + fmaxnorm + \
            finfinity + fdefaultnan + [fqnan[0], fqnan[3]] + \
            [fsnan[0], fsnan[3]] + fone
    else:
        logger.error('D part is missing')
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
    
    mess='Generating ' + str(len(coverpoints)) + ' coverpoints using Model B1!'
    logger.info(mess)
    return coverpoints

def b2(flen,ops):
	
	md_list = ['0x00000001','0x80000001','0x3F800001','0xBF800001','0x00000000','0x80000000','0x007FFFFE','0x807FFFFE','0x00800001','0x80800001','0x7F7FFFFE','0xFF7FFFFE','0x7F800001','0xFF800001']
	rm_list = ['0','1','2','3','4']
	
	f_list = sem_return(md_list)
	
	if(ops == 2):
		coverpoints = [i +' and '+ j.replace('fs1','fs2').replace('fe1','fe2').replace('fm1','fm2') +' and rm == '+ k for i in f_list for j in f_list for k in rm_list]
	elif(ops == 1):
		coverpoints = [i +' and rm == '+ j for i in f_list for j in rm_list]
	elif(ops == 3):
		coverpoints = [i +' and '+ j.replace('fs1','fs2').replace('fe1','fe2').replace('fm1','fm2') +' and '+j.replace('fs1','fs3').replace('fe1','fe3').replace('fm1','fm3') +' and rm == '+ l for i in f_list for j in f_list for k in f_list for l in rm_list]
	mess='Generating ' + str(len(coverpoints)) + ' coverpoints using Model B2!'
	logger.info(mess)
	return coverpoints
	
