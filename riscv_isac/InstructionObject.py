''' Instruction Object '''
class instructionObject():
    '''
        Instruction object class
    '''
    def __init__(
        self,
        instr_name,
        instr_addr,
        rd = None,
        rs1 = None,
        rs2 = None,
        rs3 = None,
        imm = None,
        csr = None,
        shamt = None):

        '''
            Constructor.
            :param instr_name: name of instruction as accepted by a standard RISC-V assembler
            :param instr_addr: pc value of the instruction
            :param rd: tuple containing the register index and registerfile (x or f) that will be updated by this instruction
            :param rs1: typle containing the register index and registerfilr ( x or f) that will be used as the first source operand.
            :param rs2: typle containing the register index and registerfilr ( x or f) that will be used as the second source operand.
            :param rs3: typle containing the register index and registerfilr ( x or f) that will be used as the third source operand.
            :param imm: immediate value, if any, used by the instruction
            :param csr: csr index, if any, used by the instruction
            :param shamt: shift amount, if any, used by the instruction
        '''
        self.instr_name = instr_name
        self.instr_addr = instr_addr
        self.rd = rd
        self.rs1 = rs1
        self.rs2 = rs2
        self.rs3 = rs3
        self.imm = imm
        self.csr = csr
        self.shamt = shamt

    def __str__(self):
        line = 'addr: '+ str(hex(self.instr_addr)) +' instr: '+ str(self.instr_name)
        if self.rd:
            line+= ' rd: '+ str(self.rd)
        if self.rs1:
            line+= ' rs1: '+ str(self.rs1)
        if self.rs2:
            line+= ' rs2: '+ str(self.rs2)
        if self.rs3:
            line+= ' rs3: '+ str(self.rs3)
        if self.csr:
            line+= ' csr: '+ str(self.csr)
        if self.imm:
            line+= ' imm: '+ str(self.imm)
        if self.shamt:
            line+= ' shamt: '+ str(self.shamt)
        return line