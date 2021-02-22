from riscv_isac.log import logger

def sem_return(hex_list):
	
	sem_list=[]
	for i in range(len(hex_list)):
		bin_val = bin(int('1'+hex_list[i][2:],16))[3:]
		sgn = bin_val[0]
		exp = bin_val[1:9]
		mant = bin_val[9:]
		sem_list.append('fs1 == '+ sgn +' and fe1 == '+ '0x'+hex(int('1111'+exp,2))[3:] +' and fm1 == '+ '0x'+hex(int('11110'+mant,2))[3:])
	return(sem_list)
	
def b1(flen,ops):
	
	cc_list = ['0x00000000','0x80000000'] #,'0x3F800000','0xBF800000','0x00000001','0x80000001','0x007FFFFF','0x807FFFFF','0x00800000','0x80800000','0x7F7FFFFF','0xFF7FFFFF','0x7F800000','0xFF800000','0xFFFFFFFF','0xFF800001','0xFF8FFFFF']
	sn_list = ['0x00000001','0x00000002'] #,'0x00000003','0x00000004','0x00000005','0x80000001','0x80000002','0x80000003','0x80000004','0x80000005']
	nn_list = ['0x00800001','0x00800002'] #,'0x00800003','0x00800004','0x00800005','0x80800001','0x80800002','0x80800003','0x80800004','0x80800005']
	rm_list = ['0'] #,'1','2','3','4']
	
	f_list = sem_return(cc_list + sn_list + nn_list)
	
	if(ops == 2):
		coverpoints = [i +' and '+ j.replace('fs1','fs2').replace('fe1','fe2').replace('fm1','fm2') +' and rm == '+ k for i in f_list for j in f_list for k in rm_list]
	elif(ops == 1):
		coverpoints = [i +' and rm == '+ j for i in f_list for j in rm_list]
	elif(ops == 3):
		coverpoints = [i +' and '+ j.replace('fs1','fs2').replace('fe1','fe2').replace('fm1','fm2') +' and '+j.replace('fs1','fs3').replace('fe1','fe3').replace('fm1','fm3') +' and rm == '+ l for i in f_list for j in f_list for k in f_list for l in rm_list]
	mess='Generating ' + str(len(coverpoints)) + ' coverpoints using Model B1!'
	logger.info(mess)
	
	return coverpoints
	
