from fp_dataset import *

# Model B1
opcode_32_b1 = [('fadd.s',2), ('fsub.s',2), ('fmul.s',2), ('fdiv.s',2), ('fsqrt.s',1), ('fmadd.s',3), ('fnmadd.s',3), ('fmsub.s',3), ('fnmsub.s',3)]
opcode_64_b1 = [('fadd.d',2), ('fsub.d',2), ('fmul.d',2), ('fdiv.d',2), ('fsqrt.d',1), ('fmadd.d',3), ('fnmadd.d',3), ('fmsub.d',3), ('fnmsub.d',3)]

# Model B2
opcode_32_b2 = [('fadd.s',2), ('fsub.s',2), ('fmul.s',2), ('fdiv.s',2), ('fsqrt.s',1), ('fmadd.s',3), ('fnmadd.s',3), ('fmsub.s',3), ('fnmsub.s',3)]
opcode_64_b2 = [('fadd.d',2), ('fsub.d',2), ('fmul.d',2), ('fdiv.d',2), ('fsqrt.d',1), ('fmadd.d',3), ('fnmadd.d',3), ('fmsub.d',3), ('fnmsub.d',3)]

# Model B3
opcode_32_b3 = [('fadd.s',2), ('fsub.s',2), ('fmul.s',2), ('fdiv.s',2), ('fsqrt.s',1), ('fmadd.s',3), ('fnmadd.s',3), ('fmsub.s',3), ('fnmsub.s',3)]
opcode_64_b3 = [('fadd.d',2), ('fsub.d',2), ('fmul.d',2), ('fdiv.d',2), ('fsqrt.d',1), ('fmadd.d',3), ('fnmadd.d',3), ('fmsub.d',3), ('fnmsub.d',3)]

# Model B4
opcode_32_b4 = [('fadd.s',2), ('fsub.s',2), ('fmul.s',2), ('fdiv.s',2), ('fsqrt.s',1), ('fmadd.s',3), ('fnmadd.s',3), ('fmsub.s',3), ('fnmsub.s',3)]
opcode_64_b4 = [('fadd.d',2), ('fsub.d',2), ('fmul.d',2), ('fdiv.d',2), ('fsqrt.d',1), ('fmadd.d',3), ('fnmadd.d',3), ('fmsub.d',3), ('fnmsub.d',3)]

# Model B5
opcode_32_b5 = [('fadd.s',2), ('fsub.s',2), ('fmul.s',2), ('fdiv.s',2), ('fsqrt.s',1), ('fmadd.s',3), ('fnmadd.s',3), ('fmsub.s',3), ('fnmsub.s',3)]
opcode_64_b5 = [('fadd.d',2), ('fsub.d',2), ('fmul.d',2), ('fdiv.d',2), ('fsqrt.d',1), ('fmadd.d',3), ('fnmadd.d',3), ('fmsub.d',3), ('fnmsub.d',3)]

# Model B6
opcode_32_b6 = [('fmul.s',2), ('fdiv.s',2), ('fmadd.s',3), ('fnmadd.s',3), ('fmsub.s',3), ('fnmsub.s',3)]
opcode_64_b6 = [('fmul.d',2), ('fdiv.d',2), ('fmadd.d',3), ('fnmadd.d',3), ('fmsub.d',3), ('fnmsub.d',3)]

# Model B7
opcode_32_b7 = [('fadd.s',2), ('fsub.s',2), ('fmul.s',2), ('fmadd.s',3), ('fnmadd.s',3), ('fmsub.s',3), ('fnmsub.s',3)]
opcode_64_b7 = [('fadd.d',2), ('fsub.d',2), ('fmul.d',2), ('fmadd.d',3), ('fnmadd.d',3), ('fmsub.d',3), ('fnmsub.d',3)]

# Model B8
opcode_32_b8 = [('fadd.s',2), ('fsub.s',2), ('fmul.s',2), ('fdiv.s',2), ('fmadd.s',3), ('fnmadd.s',3), ('fmsub.s',3), ('fnmsub.s',3)]
opcode_64_b8 = [('fadd.d',2), ('fsub.d',2), ('fmul.d',2), ('fdiv.d',2), ('fmadd.d',3), ('fnmadd.d',3), ('fmsub.d',3), ('fnmsub.d',3)]

# Model B9
opcode_32_b9 = [('fmul.s',2), ('fdiv.s',2), ('fsqrt.s',1)]
opcode_64_b9 = [('fmul.d',2), ('fdiv.d',2), ('fsqrt.d',1)]

# Model B10
opcode_32_b10 = [('fadd.s',2), ('fsub.s',2)]
opcode_64_b10 = [('fadd.d',2), ('fsub.d',2)]

# Model B11
opcode_32_b11 = [('fadd.s',2), ('fsub.s',2)]
opcode_64_b11 = [('fadd.d',2), ('fsub.d',2)]

# Model B12
opcode_32_b12 = [('fadd.s',2), ('fsub.s',2)]
opcode_64_b12 = [('fadd.d',2), ('fsub.d',2)]

# Model B13
opcode_32_b13 = [('fadd.s',2), ('fsub.s',2)]
opcode_64_b13 = [('fadd.d',2), ('fsub.d',2)]

# Model B14
opcode_32_b14 = [('fmadd.s',3), ('fnmadd.s',3), ('fmsub.s',3), ('fnmsub.s',3)]
opcode_64_b14 = [('fmadd.d',3), ('fnmadd.d',3), ('fmsub.d',3), ('fnmsub.d',3)]

# Model B15
opcode_32_b15 = [('fmadd.s',3), ('fnmadd.s',3), ('fmsub.s',3), ('fnmsub.s',3)]
opcode_64_b15 = [('fmadd.d',3), ('fnmadd.d',3), ('fmsub.d',3), ('fnmsub.d',3)]

# Model B16
opcode_32_b16 = [('fmadd.s',3), ('fnmadd.s',3), ('fmsub.s',3), ('fnmsub.s',3)]
opcode_64_b16 = [('fmadd.d',3), ('fnmadd.d',3), ('fmsub.d',3), ('fnmsub.d',3)]

# Model B17
opcode_32_b17 = [('fmadd.s',3), ('fnmadd.s',3), ('fmsub.s',3), ('fnmsub.s',3)]
opcode_64_b17 = [('fmadd.d',3), ('fnmadd.d',3), ('fmsub.d',3), ('fnmsub.d',3)]

# Model B18
opcode_32_b18 = [('fmadd.s',3), ('fnmadd.s',3), ('fmsub.s',3), ('fnmsub.s',3)]
opcode_64_b18 = [('fmadd.d',3), ('fnmadd.d',3), ('fmsub.d',3), ('fnmsub.d',3)]

# Model B19
opcode_32_b19 = [('fmin.s',2), ('fmax.s',2), ('fle.s',2), ('flt.s',2), ('feq.s' ,2)]
opcode_64_b19 = [('fmin.d',2), ('fmax.d',2), ('fle.d',2), ('flt.d',2), ('feq.d' ,2)]

# Model B20
opcode_32_b20 = [('fsqrt.s',1), ('fdiv.s',2)]
opcode_64_b20 = [('fsqrt.d',1), ('fdiv.d',2)]

# Model B21
opcode_32_b21 = [('fsqrt.s',1), ('fdiv.s',2)]
opcode_64_b21 = [('fsqrt.d',1), ('fdiv.d',2)]

# Model B22
opcode_32_b22 = [('fcvt.w.s',1), ('fcvt.wu.s',1), ('fcvt.l.s',1), ('fcvt.lu.s',1)]
opcode_64_b22 = [('fcvt.w.d',1), ('fcvt.wu.d',1), ('fcvt.l.d',1), ('fcvt.lu.d',1)]

# Model B23
opcode_32_b23 = [('fcvt.w.s',1), ('fcvt.wu.s',1), ('fcvt.l.s',1), ('fcvt.lu.s',1)]
opcode_64_b23 = [('fcvt.w.d',1), ('fcvt.wu.d',1), ('fcvt.l.d',1), ('fcvt.lu.d',1)]

# Model B24
opcode_32_b24 = [('fcvt.w.s',1), ('fcvt.wu.s',1), ('fcvt.l.s',1), ('fcvt.lu.s',1)]
opcode_64_b24 = [('fcvt.w.d',1), ('fcvt.wu.d',1), ('fcvt.l.d',1), ('fcvt.lu.d',1)]

# Model B25
opcode_32_b25 = [('fcvt.s.w',1), ('fcvt.s.wu',1)]
opcode_64_b25 = [('fcvt.d.w',1), ('fcvt.d.wu',1), ('fcvt.d.l',1), ('fcvt.d.lu',1)]

# Model B26
opcode_32_b26 = [('fcvt.s.w',1), ('fcvt.s.wu',1)]
opcode_64_b26 = [('fcvt.d.w',1), ('fcvt.d.wu',1), ('fcvt.d.l',1), ('fcvt.d.lu',1)]

# Model B28
opcode_32_b28 = [('fcvt.w.s',1), ('fcvt.wu.s',1), ('fcvt.l.s',1), ('fcvt.lu.s',1)]
opcode_64_b28 = [('fcvt.w.d',1), ('fcvt.wu.d',1), ('fcvt.l.d',1), ('fcvt.lu.d',1)]

# Model B29
opcode_32_b29 = [('fcvt.w.s',1), ('fcvt.wu.s',1), ('fcvt.l.s',1), ('fcvt.lu.s',1)]
opcode_64_b29 = [('fcvt.w.d',1), ('fcvt.wu.d',1), ('fcvt.l.d',1), ('fcvt.lu.d',1)]

for i in range(23,30):
	if i != 27:
		file1 = open("model_b"+str(i)+".txt","w")
		print("Writing File model_b"+str(i)+".txt")
		for j in range(len(eval("opcode_32_b"+str(i)))):
			x=eval("ibm_b"+str(i)+"(32, opcode_32_b"+str(i)+"[j][0], opcode_32_b"+str(i)+"[j][1])")
			print("No of 32-Bit Coverpoints generated for "+eval("opcode_32_b"+str(i)+"[j][0]")+" = "+str(len(x)))
			file1.write("Opcode: "+eval("opcode_32_b"+str(i)+"[j][0]")+"\n")
			file1.write("\n")
			for k in range(len(x)):
				file1.write(x[k]+'\n')
			file1.write("\n")
		for j in range(len(eval("opcode_64_b"+str(i)))):
			x=eval("ibm_b"+str(i)+"(64, opcode_64_b"+str(i)+"[j][0], opcode_64_b"+str(i)+"[j][1])")
			print("No of 64-Bit Coverpoints generated for "+eval("opcode_64_b"+str(i)+"[j][0]")+" = "+str(len(x)))
			file1.write("Opcode: "+eval("opcode_64_b"+str(i)+"[j][0]")+"\n")
			file1.write("\n")
			for k in range(len(x)):
				file1.write(x[k]+'\n')
			file1.write("\n")
		print()
