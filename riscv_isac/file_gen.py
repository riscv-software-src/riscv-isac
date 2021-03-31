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

for i in range(1,10):
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

