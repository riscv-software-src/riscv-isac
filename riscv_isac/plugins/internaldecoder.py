import riscv_isac.plugins as plugins

class disassembler():

    def __init__(self):
        OPCODES = {
            0b0110111: self.lui,
            0b0010111: self.auipc,
            0b1101111: self.jal,
            0b1100111: self.jalr,
            0b1100011: self.branch_ops,
            0b0000011: self.load_ops,
            0b0100011: self.store_ops,
            0b0010011: self.arithi_ops,
            0b0110011: self.arith_ops,
            0b0001111: self.fence_ops,
            0b1110011: self.priviledged_ops,
            0b0011011: self.rv64i_arithi_ops,
            0b0111011: self.rv64i_arith_ops,
            0b0101111: self.rv64_rv32_atomic_ops,
            0b0000111: self.flw_fld,
            0b0100111: self.fsw_fsd,
            0b1000011: self.fmadd,
            0b1000111: self.fmsub,
            0b1001011: self.fnmsub,
            0b1001111: self.fnmadd,
            0b1010011: self.rv32_rv64_float_ops
        }
        """ Instruction Op-Codes dict for 32-bit instructions """

        C_OPCODES = {
            0b00: self.quad0,
            0b01: self.quad1,
            0b10: self.quad2
        }
        """ Instruction OP-CODES dict for 16-bit instructions """
        self.C_OPCODES = C_OPCODES
        self.OPCODES = OPCODES

    @plugins.decoderHookImpl
    def setup(self, arch):
        self.arch = arch

    FIRST2_MASK = 0x00000003
    OPCODE_MASK = 0x0000007f
    FUNCT3_MASK = 0x00007000
    FUNCT6_MASK = 0x3F000000
    FUNCT4_MASK = 0x3e000000

    RD_MASK = 0x00000f80
    RS1_MASK = 0x000f8000
    RS2_MASK = 0x01f00000
    RS3_MASK = 0xf8000000
    BS_MASK = 0xc0000000

    def extractOpcode(self, instr):
        return self.OPCODE_MASK & instr

    ''' Processing Instr from OPCODES '''
    def twos_comp(self, val, bits):
        if (val & (1 << (bits - 1))) != 0:
            val = val - (1 << bits)
        return val

    def lui(self, instrObj):
        instr = instrObj.instr
        imm = instr >> 12
        rd = ((instr & self.RD_MASK) >> 7, 'x')
        instrObj.rd = rd
        instrObj.imm = imm
        instrObj.instr_name = "lui"
        return instrObj

    def auipc(self, instrObj):
        instr = instrObj.instr
        imm = instr >> 12
        rd = ((instr & self.RD_MASK) >> 7, 'x')
        instrObj.rd = rd
        instrObj.imm = imm
        instrObj.instr_name = "auipc"
        return instrObj

    def jal(self, instrObj):
        instr = instrObj.instr
        imm_10_1 = (instr >> 21) & 0x000003ff
        imm_11 = (instr >> 10) & 0x00000400
        imm_19_12 = (instr & 0x000ff000) >> 1
        imm_20 = (instr >> 31) << 19
        imm = imm_20 + imm_19_12 + imm_11 + imm_10_1
        imm = self.twos_comp(imm, 20)
        rd = ((instr & self.RD_MASK) >> 7, 'x')
        instrObj.imm = imm
        instrObj.rd = rd
        instrObj.instr_name = "jal"
        return instrObj

    def jalr(self, instrObj):
        instr = instrObj.instr
        rd = ((instr & self.RD_MASK) >> 7, 'x')
        rs1 = ((instr & self.RS1_MASK) >> 15, 'x')
        imm_11_0 = instr >> 20
        imm = self.twos_comp(imm_11_0, 12)
        instrObj.rd = rd
        instrObj.rs1 = rs1
        instrObj.imm = imm
        instrObj.instr_name = "jalr"
        return instrObj

    def branch_ops(self, instrObj):
        instr = instrObj.instr
        funct3 = (instr & self.FUNCT3_MASK) >> 12
        rs1 = ((instr & self.RS1_MASK) >> 15, 'x')
        rs2 = ((instr & self.RS2_MASK) >> 20, 'x')
        imm_4_1 = (instr >> 8) & 0x0000000F
        imm_10_5 = (instr >> 21) & 0x000003f0
        imm_11 = (instr << 3) & 0x00000400
        imm_12 = (instr & 0x80000000) >> 20
        imm = imm_4_1 + imm_10_5 + imm_11 + imm_12
        imm = self.twos_comp(imm, 12)
        instrObj.rs1 = rs1
        instrObj.rs2 = rs2
        instrObj.imm = imm

        if funct3 == 0b000:
            instrObj.instr_name = 'beq'
        if funct3 == 0b001:
            instrObj.instr_name = 'bne'
        if funct3 == 0b100:
            instrObj.instr_name = 'blt'
        if funct3 == 0b101:
            instrObj.instr_name = 'bge'
        if funct3 == 0b110:
            instrObj.instr_name = 'bltu'
        if funct3 == 0b111:
            instrObj.instr_name = 'bgeu'

        return instrObj

    def load_ops(self, instrObj):
        instr = instrObj.instr
        funct3 = (instr & self.FUNCT3_MASK) >> 12
        rd = ((instr & self.RD_MASK) >> 7, 'x')
        rs1 = ((instr & self.RS1_MASK) >> 15, 'x')
        imm = self.twos_comp(instr >> 20, 12)

        instrObj.rd = rd
        instrObj.rs1 = rs1
        instrObj.imm = imm

        if funct3 == 0b000:
            instrObj.instr_name = 'lb'
        if funct3 == 0b001:
            instrObj.instr_name = 'lh'
        if funct3 == 0b010:
            instrObj.instr_name = 'lw'
        if funct3 == 0b100:
            instrObj.instr_name = 'lbu'
        if funct3 == 0b101:
            instrObj.instr_name = 'lhu'
        if funct3 == 0b110:
            instrObj.instr_name = 'lwu'
        if funct3 == 0b011:
            instrObj.instr_name = 'ld'

        return instrObj

    def store_ops(self, instrObj):
        instr = instrObj.instr
        funct3 = (instr & self.FUNCT3_MASK) >> 12
        rs1 = ((instr & self.RS1_MASK) >> 15, 'x')
        rs2 = ((instr & self.RS2_MASK) >> 20, 'x')
        imm_4_0 = (instr >> 7) & 0x0000001f
        imm_11_5 = (instr >> 20) & 0x00000fe0
        imm = self.twos_comp(imm_4_0 + imm_11_5, 12)

        instrObj.rs1 = rs1
        instrObj.rs2 = rs2
        instrObj.imm = imm

        if funct3 == 0b000:
            instrObj.instr_name = 'sb'
        if funct3 == 0b001:
            instrObj.instr_name = 'sh'
        if funct3 == 0b010:
            instrObj.instr_name = 'sw'
        if funct3 == 0b011:
            instrObj.instr_name = 'sd'

        return instrObj

    def arithi_ops(self, instrObj):

        instr = instrObj.instr

        funct3 = (instr & self.FUNCT3_MASK) >> 12
        funct4 = (instr & self.FUNCT4_MASK) >> 25
        funct6 = (instr & self.FUNCT6_MASK) >> 26
        rd = ((instr & self.RD_MASK) >> 7, 'x')
        rs1 = ((instr & self.RS1_MASK) >> 15, 'x')
        rs2 = ((instr & self.RS2_MASK) >> 20, 'x')
        rs3 = ((instr & self.RS3_MASK) >> 27, 'x')
        imm = (instr >> 20)
        imm_val = self.twos_comp(imm, 12)
        bs = (instr & self.BS_MASK) >> 30

        instrObj.rd = rd
        instrObj.rs1 = rs1
        instrObj.imm = imm_val

        if funct3 == 0b000:
            instrObj.instr_name = 'addi'
        if funct3 == 0b010:
            instrObj.instr_name = 'slti'
        if funct3 == 0b011:
            instrObj.instr_name = 'sltiu'
            instrObj.imm = imm
        if funct3 == 0b100:
            instrObj.instr_name = 'xori'
        if funct3 == 0b110:
            instrObj.instr_name = 'ori'
        if funct3 == 0b111:
            instrObj.instr_name = 'andi'

        if funct3 == 0b001:
            if funct6 == 0b000010:
                imm = (instr & 0x03F00000)>>20
                instrObj.rs1 = rs1
                instrObj.rd = rd
                instrObj.imm = imm
                instrObj.instr_name = 'shfli'
            elif funct4 == 0b01000:
                if rs2[0] == 0b01000:
                    instrObj.instr_name = 'sm3p0'
                    instrObj.rs1 = rs1
                    instrObj.rd = rd
                    instrObj.imm = bs
                elif rs2[0] == 0b01001:
                    instrObj.instr_name = 'sm3p1'
                    instrObj.rs1 = rs1
                    instrObj.rd = rd
                    instrObj.imm = bs
                elif rs2[0] == 0b00000:
                    instrObj.instr_name = 'sha256sum0'
                    instrObj.rs1 = rs1
                    instrObj.rd = rd
                    instrObj.imm = bs
                elif rs2[0] == 0b00001:
                    instrObj.instr_name = 'sha256sum1'
                    instrObj.rs1 = rs1
                    instrObj.rd = rd
                    instrObj.imm = bs
                elif rs2[0] == 0b00010:
                    instrObj.instr_name = 'sha256sig0'
                    instrObj.rs1 = rs1
                    instrObj.rd = rd
                    instrObj.imm = bs
                elif rs2[0] == 0b00011:
                    instrObj.instr_name = 'sha256sig1'
                    instrObj.rs1 = rs1
                    instrObj.rd = rd
                    instrObj.imm = bs
                elif rs2[0] == 0b00100:
                    instrObj.instr_name = 'sha512sum0'
                    instrObj.rs1 = rs1
                    instrObj.rd = rd
                    instrObj.imm = bs
                elif rs2[0] == 0b00101:
                    instrObj.instr_name = 'sha512sum1'
                    instrObj.rs1 = rs1
                    instrObj.rd = rd
                    instrObj.imm = bs
                elif rs2[0] == 0b00110:
                    instrObj.instr_name = 'sha512sig0'
                    instrObj.rs1 = rs1
                    instrObj.rd = rd
                    instrObj.imm = bs
                elif rs2[0] == 0b00111:
                    instrObj.instr_name = 'sha512sig1'
                    instrObj.rs1 = rs1
                    instrObj.rd = rd
                    instrObj.imm = bs
            elif funct4 == 0b11000:
                rs2_bit24 = (instr & 0x01000000) >> 24
                if rs2_bit24 == 0b1:
                    imm = (instr & 0x00f00000) >> 20
                    instrObj.instr_name = 'aes64ks1i'
                    instrObj.rs1 = rs1
                    instrObj.rd = rd
                    instrObj.imm = imm
                else:
                    instrObj.instr_name = 'aes64im'
                    instrObj.rs1 = rs1
                    instrObj.rd = rd
                    instrObj.imm = bs
            else:
                instrObj.instr_name = 'slli'
                instrObj.imm = None
                if self.arch == 'rv32':
                        shamt = imm & 0x01f
                elif self.arch == 'rv64':
                        shamt = imm & 0x03f
                instrObj.shamt = shamt

        if funct3 == 0b101:
            if funct6 == 0b000010:
                imm = (instr & 0x03F00000)>>20
                instrObj.rs1 = rs1
                instrObj.rd = rd
                instrObj.imm = imm
                instrObj.instr_name = 'unshfli'
            elif self.arch == 'rv32' and (imm>>5) == 0b0110000:
                instrObj.imm = imm & 0x1f
                instrObj.shamt = imm & 0x1f
                instrObj.instr_name = 'rori'
                instrObj.rs1 = rs1
                instrObj.rd = rd
            elif self.arch == 'rv64' and (imm>>6) == 0b011000:
                instrObj.imm = imm & 0x3f
                instrObj.shamt = imm & 0x3f
                instrObj.instr_name = 'rori'
                instrObj.rs1 = rs1
                instrObj.rd = rd
            elif rs3[0] == 0b01101:
                imm = ((instr & 0x07f00000) >> 20)
                instrObj.instr_name = 'grevi'
                instrObj.rs1 = rs1
                instrObj.rd = rd
                instrObj.imm = imm
            else:
                instrObj.imm = None
                if self.arch == 'rv32':
                    shamt = imm & 0x01f
                elif self.arch == 'rv64':
                    shamt = imm & 0x03f
                instrObj.shamt = shamt
                rtype_bit = (imm >> 10) & 0x1
                if rtype_bit == 1:
                    instrObj.instr_name = 'srai'
                if rtype_bit == 0:
                    instrObj.instr_name = 'srli'

        return instrObj

    def arithm_ops(self, instrObj):
        instr = instrObj.instr
        funct3 = (instr & self.FUNCT3_MASK) >> 12
        rd = ((instr & self.RD_MASK) >> 7, 'x')
        rs1 = ((instr & self.RS1_MASK) >> 15, 'x')
        rs2 = ((instr & self.RS2_MASK) >> 20, 'x')

        instrObj.rd = rd
        instrObj.rs1 = rs1
        instrObj.rs2 = rs2

        if funct3 == 0b000:
            instrObj.instr_name = 'mul'
        if funct3 == 0b001:
            instrObj.instr_name = 'mulh'
        if funct3 == 0b010:
            instrObj.instr_name = 'mulhsu'
        if funct3 == 0b011:
            instrObj.instr_name = 'mulhu'
        if funct3 == 0b100:
            instrObj.instr_name = 'div'
        if funct3 == 0b101:
            instrObj.instr_name = 'divu'
        if funct3 == 0b110:
            instrObj.instr_name = 'rem'
        if funct3 == 0b111:
            instrObj.instr_name = 'remu'

        return instrObj

    def arith_ops(self, instrObj):

        instr = instrObj.instr
            # Test for RV32M ops
        funct7 = (instr >> 25)
        if funct7 == 0b0000001:
            return self.arithm_ops(instrObj)

        # Test for RV32I ops
        funct3 = (instr & self.FUNCT3_MASK) >> 12
        funct4 = (instr & self.FUNCT4_MASK) >> 25
        rd = ((instr & self.RD_MASK) >> 7, 'x')
        rs1 = ((instr & self.RS1_MASK) >> 15, 'x')
        rs2 = ((instr & self.RS2_MASK) >> 20, 'x')
        bs = (instr & self.BS_MASK) >> 30

        instrObj.rd = rd
        instrObj.rs1 = rs1
        instrObj.rs2 = rs2

        if funct3 == 0b000:
            if funct7 == 0b0000000:
                instrObj.instr_name = 'add'
            if funct7 == 0b0100000:
                instrObj.instr_name = 'sub'
            if funct4 == 0b01000:
                instrObj.instr_name = 'sha512sum0r'
                instrObj.rs1 = rs1
                instrObj.rs2 = rs2
                instrObj.rd = rd
                instrObj.imm = bs
            elif funct4 == 0b01001:
                instrObj.instr_name = 'sha512sum1r'
                instrObj.rs1 = rs1
                instrObj.rs2 = rs2
                instrObj.rd = rd
                instrObj.imm = bs
            elif funct4 == 0b01010:
                instrObj.instr_name = 'sha512sig0l'
                instrObj.rs1 = rs1
                instrObj.rs2 = rs2
                instrObj.rd = rd
                instrObj.imm = bs
            elif funct4 == 0b01110:
                instrObj.instr_name = 'sha512sig0h'
                instrObj.rs1 = rs1
                instrObj.rs2 = rs2
                instrObj.rd = rd
                instrObj.imm = bs
            elif funct4 == 0b01011:
                instrObj.instr_name = 'sha512sig1l'
                instrObj.rs1 = rs1
                instrObj.rs2 = rs2
                instrObj.rd = rd
                instrObj.imm = bs
            elif funct4 == 0b01111:
                instrObj.instr_name = 'sha512sig1h'
                instrObj.rs1 = rs1
                instrObj.rs2 = rs2
                instrObj.rd = rd
                instrObj.imm = bs
            elif funct4 == 0b11000:
                instrObj.instr_name = 'sm4ed'
                instrObj.rs1 = rs1
                instrObj.rs2 = rs2
                instrObj.rd = rd
                instrObj.imm = bs
            elif funct4 == 0b11010:
                instrObj.instr_name = 'sm4ks'
                instrObj.rs1 = rs1
                instrObj.rs2 = rs2
                instrObj.rd = rd
                instrObj.imm = bs
            elif funct4 == 0b10011:
                instrObj.instr_name = 'aes32esmi'
                instrObj.rs1 = rs1
                instrObj.rs2 = rs2
                instrObj.rd = rd
                instrObj.imm = bs
            elif funct4 == 0b11011:
                instrObj.instr_name = 'aes64esm'
                instrObj.rs1 = rs1
                instrObj.rs2 = rs2
                instrObj.rd = rd
                instrObj.imm = bs
            elif funct4 == 0b10001:
                instrObj.instr_name = 'aes32esi'
                instrObj.rs1 = rs1
                instrObj.rs2 = rs2
                instrObj.rd = rd
                instrObj.imm = bs
            elif funct4 == 0b11001:
                instrObj.instr_name = 'aes64es'
                instrObj.rs1 = rs1
                instrObj.rs2 = rs2
                instrObj.rd = rd
                instrObj.imm = bs
            elif funct4 == 0b10111:
                instrObj.instr_name = 'aes32dsmi'
                instrObj.rs1 = rs1
                instrObj.rs2 = rs2
                instrObj.rd = rd
                instrObj.imm = bs
            elif funct4 == 0b11111:
                    if bs == 0b00:
                        instrObj.instr_name = 'aes64dsm'
                        instrObj.rs1 = rs1
                        instrObj.rs2 = rs2
                        instrObj.rd = rd
                        instrObj.imm = bs
                    elif bs == 0b01:
                        instrObj.instr_name = 'aes64ks2'
                        instrObj.rs1 = rs1
                        instrObj.rs2 = rs2
                        instrObj.rd = rd
                        instrObj.imm = bs
            elif funct4 == 0b10101:
                instrObj.instr_name = 'aes32dsi'
                instrObj.rs1 = rs1
                instrObj.rs2 = rs2
                instrObj.rd = rd
                instrObj.imm = bs
            elif funct4 == 0b11101:
                instrObj.instr_name = 'aes64ds'
                instrObj.rs1 = rs1
                instrObj.rs2 = rs2
                instrObj.rd = rd
                instrObj.imm = bs

        if funct3 == 0b001:
            if funct7 == 0b0110000:
                instrObj.instr_name = 'rol'
                instrObj.rs1 = rs1
                instrObj.rs2 = rs2
                instrObj.rd = rd
            elif funct7 == 0b0000101:
                instrObj.instr_name = 'clmul'
                instrObj.rs1 = rs1
                instrObj.rs2 = rs2
                instrObj.rd = rd
            else:
                instrObj.instr_name = 'sll'

        if funct3 == 0b010:
            if funct7 == 0b0010100:
                instrObj.instr_name = 'xperm.n'
                instrObj.rs1 = rs1
                instrObj.rs2 = rs2
                instrObj.rd = rd
            else:
                instrObj.instr_name = 'slt'

        if funct3 == 0b011:
            if funct7 == 0b0000101:
                instrObj.instr_name = 'clmulh'
                instrObj.rs1 = rs1
                instrObj.rs2 = rs2
                instrObj.rd = rd
            else:
                instrObj.instr_name = 'sltu'

        if funct3 == 0b100:
            if funct7 == 0b0100000:
                instrObj.instr_name = 'xnor'
                instrObj.rs1 = rs1
                instrObj.rs2 = rs2
                instrObj.rd = rd
            elif funct7 == 0b0000100:
                instrObj.instr_name = 'pack'
                instrObj.rs1 = rs1
                instrObj.rs2 = rs2
                instrObj.rd = rd
            # elif funct7 == 0b0100100:
            #     instrObj.instr_name = 'packu'
            #     instrObj.rs1 = rs1
            #     instrObj.rs2 = rs2
            #     instrObj.rd = rd
            elif funct7 == 0b0010100:
                instrObj.instr_name = 'xperm.b'
                instrObj.rs1 = rs1
                instrObj.rs2 = rs2
                instrObj.rd = rd
            else:
                instrObj.instr_name = 'xor'

        if funct3 == 0b101:
            if funct7 == 0b0000000:
                instrObj.instr_name = 'srl'
            elif funct7 == 0b0100000:
                instrObj.instr_name = 'sra'
            elif funct7 == 0b0110000:
                instrObj.instr_name = 'ror'
                instrObj.rs1 = rs1
                instrObj.rs2 = rs2
                instrObj.rd = rd

        if funct3 == 0b110:
            if funct7 == 0b0100000:
                instrObj.instr_name = 'orn'
                instrObj.rs1 = rs1
                instrObj.rs2 = rs2
                instrObj.rd = rd
            else:
                instrObj.instr_name = 'or'

        if funct3 == 0b111:
            if funct7 == 0b0100000:
                instrObj.instr_name = 'andn'
                instrObj.rs1 = rs1
                instrObj.rs2 = rs2
                instrObj.rd = rd
            elif funct7 == 0b0000100:
                instrObj.instr_name = 'packh'
                instrObj.rs1 = rs1
                instrObj.rs2 = rs2
                instrObj.rd = rd
            else:
                instrObj.instr_name = 'and'

        return instrObj

    def fence_ops(self, instrObj):
        instr = instrObj.instr
        funct3 = (instr & self.FUNCT3_MASK) >> 12

        pred = (instr >> 20) & 0x0000000f
        succ = (instr >> 24) & 0x0000000f

        if funct3 == 0b000:
            instrObj.succ = succ
            instrObj.pred = pred
            instrObj.instr_name = 'fence'
        if funct3 == 0b001:
            instrObj.instr_name = 'fence.i'

        return instrObj

    def priviledged_ops(self, instrObj):
        instr = instrObj.instr
        funct3 = (instr & self.FUNCT3_MASK) >> 12

        # Test for ecall and ebreak ops
        if funct3 == 0b000:
            etype = (instr >> 20) & 0x01
            if etype == 0b0:
                instrObj.instr_name = 'ecall'
                return instrObj
            if etype == 0b1:
                instrObj.instr_name = 'ebreak'
                return instrObj

        # Test for csr ops
        rd = ((instr & self.RD_MASK) >> 7, 'x')
        rs1 = ((instr & self.RS1_MASK) >> 15, 'x')
        csr = (instr >> 20)

        instrObj.rd = rd
        instrObj.rs1 = rs1
        instrObj.csr = csr

        if funct3 == 0b001:
            instrObj.instr_name = 'csrrw'
        if funct3 == 0b010:
            instrObj.instr_name = 'csrrs'
        if funct3 == 0b011:
            instrObj.instr_name = 'csrrc'
        if funct3 == 0b101:
            instrObj.instr_name = 'csrrwi'
            instrObj.rs1 = None
            instrObj.zimm = rs1[0]
        if funct3 == 0b110:
            instrObj.instr_name = 'csrrsi'
            instrObj.rs1 = None
            instrObj.zimm = rs1[0]
        if funct3 == 0b101:
            instrObj.instr_name = 'csrrci'
            instrObj.rs1 = None
            instrObj.zimm = rs1[0]

        return instrObj

    def rv64i_arithi_ops(self, instrObj):

        instr = instrObj.instr

        funct3 = (instr & self.FUNCT3_MASK) >> 12
        funct7 = (instr >> 25)
        rd = ((instr & self.RD_MASK) >> 7, 'x')
        rs1 = ((instr & self.RS1_MASK) >> 15, 'x')
        imm = ((instr & self.RS2_MASK) >> 20)

        instrObj.rd = rd
        instrObj.rs1 = rs1

        if funct3 == 0b000:
            imm = self.twos_comp((instr >> 20) & 0x00000FFF, 12)
            instrObj.imm = imm
            instrObj.instr_name = 'addiw'
            return instrObj

        shamt = (instr >> 20) & 0x0000001f
        instrObj.shamt = shamt

        if funct3 == 0b001:
            instrObj.instr_name = 'slliw'
        if funct3 == 0b101:
            if funct7 == 0b0110000:
                instrObj.instr_name = 'roriw'
                instrObj.rs1 = rs1
                instrObj.rd = rd
                instrObj.imm = imm
            else:
                rtype_bit = (instr >> 30) & 0x01
                if rtype_bit == 0:
                    instrObj.instr_name = 'srliw'
                if rtype_bit == 1:
                    instrObj.instr_name = 'sraiw'

        return instrObj

    def rv64m_arithm_ops(self, instrObj):
        instr = instrObj.instr
        funct3 = (instr & self.FUNCT3_MASK) >> 12
        rd = ((instr & self.RD_MASK) >> 7, 'x')
        rs1 = ((instr & self.RS1_MASK) >> 15, 'x')
        rs2 = ((instr & self.RS2_MASK) >> 20, 'x')

        instrObj.rd = rd
        instrObj.rs1 = rs1
        instrObj.rs2 = rs2

        if funct3 == 0b000:
            instrObj.instr_name = 'mulw'
        if funct3 == 0b100:
            instrObj.instr_name = 'divw'
        if funct3 == 0b101:
            instrObj.instr_name = 'divuw'
        if funct3 == 0b110:
            instrObj.instr_name = 'remw'
        if funct3 == 0b111:
            instrObj.instr_name = 'remuw'

        return instrObj

    def rv64i_arith_ops(self, instrObj):

        instr = instrObj.instr

        # Test for rv64m ops
        funct7 = (instr >> 25)
        if funct7 == 0b0000001:
            return self.rv64m_arithm_ops(instrObj)

        # Test for RV64I ops
        funct3 = (instr & self.FUNCT3_MASK) >> 12
        rd = ((instr & self.RD_MASK) >> 7, 'x')
        rs1 = ((instr & self.RS1_MASK) >> 15, 'x')
        rs2 = ((instr & self.RS2_MASK) >> 20, 'x')

        instrObj.rd = rd
        instrObj.rs1 = rs1
        instrObj.rs2 = rs2

        if funct3 == 0b000:
            if funct7 == 0b0000000:
                instrObj.instr_name = 'addw'
            if funct7 == 0b0100000:
                instrObj.instr_name = 'subw'

        if funct3 == 0b001:
            if funct7 == 0b0110000:
                instrObj.instr_name = 'rolw'
                instrObj.rs1 = rs1
                instrObj.rs2 = rs2
                instrObj.rd = rd
            else:
                instrObj.instr_name = 'sllw'

        if funct3 == 0b100:
            if funct7 == 0b0000100:
                instrObj.instr_name = 'packw'
                instrObj.rs1 = rs1
                instrObj.rs2 = rs2
                instrObj.rd = rd
            # elif funct7 == 0b0100100:
            #     instrObj.instr_name = 'packuw'
            #     instrObj.rs1 = rs1
            #     instrObj.rs2 = rs2
            #     instrObj.rd = rd

        if funct3 == 0b101:
            if funct7 == 0b0000000:
                instrObj.instr_name = 'srlw'
            elif funct7 == 0b0100000:
                instrObj.instr_name = 'sraw'
            elif funct7 == 0b0110000:
                instrObj.instr_name = 'rorw'
                instrObj.rs1 = rs1
                instrObj.rs2 = rs2
                instrObj.rd = rd

        return instrObj

    rv32a_instr_names = {
            0b00010: 'lr.w',
            0b00011: 'sc.w',
            0b00001: 'amoswap.w',
            0b00000: 'amoadd.w',
            0b00100: 'amoxor.w',
            0b01100: 'amoand.w',
            0b01000: 'amoor.w',
            0b10000: 'amomin.w',
            0b10100: 'amomax.w',
            0b11000: 'amominu.w',
            0b11100: 'amomaxu.w'
    }

    rv64a_instr_names = {
            0b00010: 'lr.d',
            0b00011: 'sc.d',
            0b00001: 'amoswap.d',
            0b00000: 'amoadd.d',
            0b00100: 'amoxor.d',
            0b01100: 'amoand.d',
            0b01000: 'amoor.d',
            0b10000: 'amomin.d',
            0b10100: 'amomax.d',
            0b11000: 'amominu.d',
            0b11100: 'amomaxu.d'
    }

    def rv64_rv32_atomic_ops(self, instrObj):

        instr = instrObj.instr
        funct5 = (instr >> 27) & 0x0000001f
        funct3 = (instr & self.FUNCT3_MASK) >> 12
        rd = ((instr & self.RD_MASK) >> 7, 'x')
        rs1 = ((instr & self.RS1_MASK) >> 15, 'x')
        rs2 = ((instr & self.RS2_MASK) >> 20, 'x')
        rl = (instr >> 25) & 0x00000001
        aq = (instr >> 26) & 0x00000001

        instrObj.rd = rd
        instrObj.rs1 = rs1
        instrObj.rs2 = rs2

        instrObj.rl = rl
        instrObj.aq = aq

        #RV32A instructions
        if funct3 == 0b010:
            if funct5 == 0b00010:
                instrObj.rs2 = None
                instrObj.instr_name = self.rv32a_instr_names[funct5]
            else:
                instrObj.instr_name = self.rv32a_instr_names[funct5]

            return instrObj

        #RV64A instructions
        if funct3 == 0b011:
            if funct5 == 0b00010:
                instrObj.rs2 = None
                instrObj.instr_name = self.rv64a_instr_names[funct5]
            else:
                instrObj.instr_name = self.rv64a_instr_names[funct5]

            return instrObj

    def flw_fld(self, instrObj):
        instr = instrObj.instr
        rd = ((instr & self.RD_MASK) >> 7, 'f')
        rs1 = ((instr & self.RS1_MASK) >> 15, 'x')
        funct3 = (instr & self.FUNCT3_MASK) >> 12
        imm = self.twos_comp((instr >> 20), 12)

        instrObj.rd = rd
        instrObj.rs1 = rs1
        instrObj.imm = imm

        if funct3 == 0b010:
            instrObj.instr_name = 'flw'
        elif funct3 == 0b011:
            instrObj.instr_name = 'fld'

        return instrObj

    def fsw_fsd(self, instrObj):
        instr = instrObj.instr
        imm_4_0 = (instr & self.RD_MASK) >> 7
        imm_11_5 = (instr >> 25) << 5
        imm = self.twos_comp(imm_4_0 + imm_11_5, 12)
        rs1 = ((instr & self.RS1_MASK) >> 15, 'd')
        rs2 = ((instr & self.RS2_MASK) >> 20, 'f')

        funct3 = (instr & self.FUNCT3_MASK) >> 12

        instrObj.rs1 = rs1
        instrObj.rs2 = rs1
        instrObj.imm = imm

        if funct3 == 0b010:
            instrObj.instr_name = 'fsw'
        elif funct3 == 0b011:
            instrObj.instr_name = 'fsd'

        return instrObj

    def fmadd(self, instrObj):
        instr = instrObj.instr
        rd = ((instr & self.RD_MASK) >> 7, 'f')
        rm = (instr >> 12) & 0x00000007
        rs1 = ((instr & self.RS1_MASK) >> 15, 'f')
        rs2 = ((instr & self.RS2_MASK) >> 20, 'f')
        rs3 = ((instr >> 27), 'f')
        size_bit = (instr >> 25) & 0x00000001

        instrObj.rs1 = rs1
        instrObj.rs2 = rs1
        instrObj.rd = rd

        instrObj.rm = rm
        instrObj.rs3 = rs3

        if size_bit == 0b0:
            instrObj.instr_name = 'fmadd.s'
        elif size_bit == 0b1:
            instrObj.instr_name = 'fmadd.d'

        return instrObj

    def fmsub(self, instrObj):
        instr = instrObj.instr
        rd = ((instr & self.RD_MASK) >> 7, 'f')
        rm = (instr >> 12) & 0x00000007
        rs1 = ((instr & self.RS1_MASK) >> 15, 'f')
        rs2 = ((instr & self.RS2_MASK) >> 20, 'f')
        rs3 = ((instr >> 27), 'f')
        size_bit = (instr >> 25) & 0x00000001

        instrObj.rs1 = rs1
        instrObj.rs2 = rs1
        instrObj.rd = rd

        instrObj.rm = rm
        instrObj.rs3 = rs3

        if size_bit == 0b0:
            instrObj.instr_name = 'fmsub.s'
        elif size_bit == 0b1:
            instrObj.instr_name = 'fmsub.d'

        return instrObj

    def fnmsub(self, instrObj):
        instr = instrObj.instr
        rd = ((instr & self.RD_MASK) >> 7, 'f')
        rm = (instr >> 12) & 0x00000007
        rs1 = ((instr & self.RS1_MASK) >> 15, 'f')
        rs2 = ((instr & self.RS2_MASK) >> 20, 'f')
        rs3 = ((instr >> 27), 'f')
        size_bit = (instr >> 25) & 0x00000001

        instrObj.rs1 = rs1
        instrObj.rs2 = rs1
        instrObj.rd = rd

        instrObj.rm = rm
        instrObj.rs3 = rs3

        if size_bit == 0b0:
            instrObj.instr_name = 'fnmsub.s'
        elif size_bit == 0b1:
            instrObj.instr_name = 'fnmsub.d'

        return instrObj

    def fnmadd(self, instrObj):
        instr = instrObj.instr
        rd = ((instr & self.RD_MASK) >> 7, 'f')
        rm = (instr >> 12) & 0x00000007
        rs1 = ((instr & self.RS1_MASK) >> 15, 'f')
        rs2 = ((instr & self.RS2_MASK) >> 20, 'f')
        rs3 = ((instr >> 27), 'f')
        size_bit = (instr >> 25) & 0x00000001

        instrObj.rs1 = rs1
        instrObj.rs2 = rs1
        instrObj.rd = rd
        instrObj.rm = rm
        instrObj.rs3 = rs3

        if size_bit == 0b0:
            instrObj.instr_name = 'fnmadd.s'
        elif size_bit == 0b1:
            instrObj.instr_name = 'fnmadd.d'

        return instrObj

    def rv32_rv64_float_ops(self, instrObj):
        instr = instrObj.instr
        rd = ((instr & self.RD_MASK) >> 7, 'f')
        rm = (instr >> 12) & 0x00000007
        rs1 = ((instr & self.RS1_MASK) >> 15, 'f')
        rs2 = ((instr & self.RS2_MASK) >> 20, 'f')
        funct7 = (instr >> 25)

        instrObj.rs1 = rs1
        instrObj.rs2 = rs1
        instrObj.rd = rd
        instrObj.rm = rm

        # fadd, fsub, fmul, fdiv
        if funct7 == 0b0000000:
            instrObj.instr_name = 'fadd.s'
        elif funct7 == 0b0000100:
            instrObj.instr_name = 'fsub.s'
        elif funct7 == 0b0001000:
            instrObj.instr_name = 'fmul.s'
        elif funct7 == 0b0001100:
            instrObj.instr_name = 'fdiv.s'
        elif funct7 == 0b0000001:
            instrObj.instr_name = 'fadd.d'
        elif funct7 == 0b0000101:
            instrObj.instr_name = 'fsub.d'
        elif funct7 == 0b0001001:
            instrObj.instr_name = 'fmul.d'
        elif funct7 == 0b0001101:
            instrObj.instr_name = 'fdiv.d'

        if instrObj.instr_name is not None:
            return instrObj

        # fsqrt
        if funct7 == 0b0101100:
            instrObj.instr_name = 'fsqrt.s'
            instrObj.rs2 = None
            return instrObj
        elif funct7 == 0b0101101:
            instrObj.instr_name = 'fsqrt.d'
            instrObj.rs2 = None
            return instrObj

        # fsgnj, fsgnjn, fsgnjx
        if funct7 == 0b0010000:
            if rm == 0b000:
                instrObj.instr_name = 'fsgnj.s'
                return instrObj
            elif rm == 0b001:
                instrObj.instr_name = 'fsgnjn.s'
                return instrObj
            elif rm == 0b010:
                instrObj.instr_name = 'fsgnjx.s'
                return instrObj
        elif funct7 == 0b0010001:
            if rm == 0b000:
                instrObj.instr_name = 'fsgnj.d'
                return instrObj
            elif rm == 0b001:
                instrObj.instr_name = 'fsgnjn.d'
                return instrObj
            elif rm == 0b010:
                instrObj.instr_name = 'fsgnjx.d'
                return instrObj

        # fmin, fmax
        if funct7 == 0b0010100:
            if rm == 0b000:
                instrObj.instr_name = 'fmin.s'
                return instrObj
            elif rm == 0b001:
                instrObj.instr_name = 'fmax.s'
                return instrObj
        elif funct7 == 0b0010101:
            if rm == 0b000:
                instrObj.instr_name = 'fmin.d'
                return instrObj
            elif rm == 0b001:
                instrObj.instr_name = 'fmax.d'
                return instrObj

        # fcvt.w, fcvt.wu, fcvt.l, fcvt.lu
        if funct7 == 0b1100000:
            mode = rs2[0]
            instrObj.rd = (rd[0], 'x')
            instrObj.rs2 = None

            if mode == 0b00000:
                instrObj.instr_name = 'fcvt.w.s'
                return instrObj
            elif mode == 0b00001:
                instrObj.instr_name = 'fcvt.wu.s'
                return instrObj
            elif mode == 0b00010:
                instrObj.instr_name = 'fcvt.l.s'
                return instrObj
            elif mode == 0b00011:
                instrObj.instr_name = 'fcvt.lu.s'
                return instrObj

        # fcvt.s.d, fcvt.d.s
        if funct7 == 0b0100000:
            if rs2[0] == 0b00001:
                instrObj.instr_name = 'fcvt.s.d'
                instrObj.rs2 = None
                return instrObj
        if funct7 == 0b0100001:
            if rs2[0] == 0b00000:
                instrObj.instr_name = 'fcvt.d.s'
                instrObj.rs2 = None
                return instrObj

        # fmv.x.w, fclass.s
        if funct7 == 0b1110000:
            if rm == 0b000:
                instrObj.instr_name = 'fmv.x.w'
                instrObj.rd = (rd[0], 'x')
                instrObj.rs2 = None
                instrObj.rm = None
                return instrObj
            elif rm == 0b001:
                instrObj.instr_name = 'fclass.s'
                instrObj.rd = (rd[0], 'x')
                instrObj.rs2 = None
                instrObj.rm = None
                return instrObj

        # feq, flt, fle
        if funct7 == 0b1010000:
            instrObj.rd = (rd[0], 'x')
            if rm == 0b010:
                instrObj.instr_name = 'feq.s'
                return instrObj
            elif rm == 0b001:
                instrObj.instr_name = 'flt.s'
                return instrObj
            elif rm == 0b000:
                instrObj.instr_name = 'fle.s'
                return instrObj

        if funct7 == 0b1010001:
            instrObj.rd = (rd[0], 'x')
            if rm == 0b010:
                instrObj.instr_name = 'feq.d'
                return instrObj
            elif rm == 0b001:
                instrObj.instr_name = 'flt.d'
                return instrObj
            elif rm == 0b000:
                instrObj.instr_name = 'fle.d'
                return instrObj

        # fcvt.s.w, fcvt.s.wu, fcvt.s.l, fcvt.s.lu
        if funct7 == 0b1100100:
            mode = rs2[0]
            instrObj.rs1 = (rs1[0], 'x')
            instrObj.rs2 = None
            if mode == 0b00000:
                instrObj.instr_name = 'fcvt.s.w'
                return instrObj
            elif mode == 0b00001:
                instrObj.instr_name = 'fcvt.s.wu'
                return instrObj
            elif mode == 0b00010:
                instrObj.instr_name = 'fcvt.s.l'
                return instrObj
            elif mode == 0b00011:
                instrObj.instr_name = 'fcvt.s.lu'
                return instrObj

        # fmv.w.x
        if funct7 == 0b1111000:
            instrObj.instr_name = 'fmv.w.x'
            instrObj.rs1 = (rs1[0], 'x')
            instrObj.rs2 = None
            return instrObj

        # fclass.d, fmv.x.d
        if funct7 == 0b1110001:
            if rm == 0b001:
                instrObj.instr_name = 'fclass.d'
                instrObj.rd = (rd[0], 'x')
                instrObj.rs2 = None
                return instrObj
            elif rm == 0b000:
                instrObj.instr_name = 'fmv.x.d'
                instrObj.rd = (rd[0], 'x')
                instrObj.rs2 = None
                return instrObj

        # fcvt.w.d, fcvt.wu.d, fcvt.d.w, fcvt.d.wu, fcvt.l.d, fcvt.lu.d
        if funct7 == 0b1100001:
            mode = rs2[0]
            instrObj.rs2 = None
            instrObj.rd = (rd[0], 'x')
            if mode == 0b00000:
                instrObj.instr_name = 'fcvt.w.d'
                instrObj.rs2 = None
                return instrObj
            elif mode == 0b00001:
                instrObj.instr_name = 'fcvt.wu.d'
                instrObj.rs2 = None
                return instrObj
            elif mode == 0b00010:
                instrObj.instr_name = 'fcvt.l.d'
                instrObj.rs2 = None
                return instrObj
            elif mode == 0b00011:
                instrObj.instr_name = 'fcvt.lu.d'
                instrObj.rs2 = None
                return instrObj

        if funct7 == 0b1101001:
            mode = rs2[0]
            instrObj.rs2 = None
            instrObj.rs1 = (rs1[0], 'x')
            if mode == 0b00000:
                instrObj.instr_name = 'fcvt.d.w'
                instrObj.rs2 = None
                return instrObj
            elif mode == 0b00001:
                instrObj.instr_name = 'fcvt.d.wu'
                instrObj.rs2 = None
                return instrObj
            elif mode == 0b00010:
                instrObj.instr_name = 'fcvt.d.l'
                instrObj.rs2 = None
                return instrObj
            elif mode == 0b00011:
                instrObj.instr_name = 'fcvt.d.lu'
                instrObj.rs2 = None
                return instrObj

        if funct7 == 0b1111001:
            instrObj.instr_name = 'fmv.d.x'
            instrObj.rs1 = (rs1[0], 'x')
            instrObj.rs2 = None
            return instrObj

    ''' Compressed Instruction Parsing Functions '''
    C_FUNCT3_MASK = 0xe000
    C0_OP2_MASK = 0x0003
    C0_RDPRIME_MASK = 0x001C
    C0_RS2PRIME_MASK = 0x001C
    C0_RS1PRIME_MASK = 0x0380
    C0_UIMM_5_3_MASK = 0x1C00
    C0_UIMM_7_6_MASK = 0x0060
    C0_UIMM_6_MASK = 0x0020
    C0_UIMM_2_MASK = 0x0040

    C1_RD_MASK = 0x0F80
    C1_RDPRIME_MASK = 0x0380
    C1_RS1PRIME_MASK = 0x0380
    C1_RS2PRIME_MASK = 0x001C
    C1_IMM_5_MASK = 0x1000
    C1_IMM_4_0_MASK = 0x007c
    C1_IMM_17_MASK = 0x1000
    C1_IMM_16_12_MASK = 0x007c
    C1_MINOR_OP_MASK = 0x0C00
    C1_MINOR_OP2_MASK = 0x0060

    def get_bit(self, val, pos):
        return (val & (1 << pos)) >> pos

    def quad0(self, instrObj):
        '''Parse instructions from Quad0 of the Compressed extension in the RISCV-ISA-Standard'''
        instr = instrObj.instr
        funct3 = (self.C_FUNCT3_MASK & instr) >> 13

        # UIMM 7:6:5:3
        uimm_5_3 = (self.C0_UIMM_5_3_MASK & instr) >> 7
        uimm_7_6 = (self.C0_UIMM_7_6_MASK & instr) << 1
        uimm_7_6_5_3 = uimm_5_3 + uimm_7_6

        # UIMM 6:5:3:2
        uimm_2 = (self.C0_UIMM_2_MASK & instr) >> 4
        uimm_6 = (self.C0_UIMM_6_MASK & instr) << 1
        uimm_6_5_3_2 = uimm_6 + uimm_5_3 + uimm_2

        # Registers
        rdprime = (self.C0_RDPRIME_MASK & instr) >> 2
        rs1prime = (self.C0_RS1PRIME_MASK & instr) >> 7
        rs2prime = (self.C0_RS2PRIME_MASK & instr) >> 2

        if funct3 == 0b000:
            nzuimm_3 = self.get_bit(instr, 5)
            nzuimm_2 = self.get_bit(instr, 6)
            nzuimm_9_6 = self.get_bit(instr, 7) + (self.get_bit(instr,8) << 1) + (self.get_bit(instr,9) << 2) + (self.get_bit(instr,10)<<3)
            nzuimm_5_4 = self.get_bit(instr, 11) + (self.get_bit(instr, 12) << 1)
            nzuimm = (nzuimm_2 << 2) + (nzuimm_3 << 3) + (nzuimm_9_6 << 6) + (nzuimm_5_4 << 4)
            if nzuimm == 0 and rdprime == 0:
                instrObj.instr_name = 'c.illegal'
                instrObj.rd = (rdprime, 'x')
            else:
                instrObj.instr_name = 'c.addi4spn'
                instrObj.rd = (8 + rdprime, 'x')
            instrObj.imm = nzuimm
            return instrObj

        elif funct3 == 0b001:
            instrObj.instr_name = 'c.fld'
            instrObj.rd = (8 + rdprime, 'f')
            instrObj.rs1 = (8 + rs1prime, 'x')
            instrObj.imm = uimm_7_6_5_3

        elif funct3 == 0b010:
            instrObj.instr_name = 'c.lw'
            instrObj.rd = (8 + rdprime, 'x')
            instrObj.rs1 = (8 + rs1prime, 'x')
            instrObj.imm = uimm_6_5_3_2

        elif funct3 == 0b011:
            if self.arch == 'rv32':
                instrObj.instr_name = 'c.flw'
                instrObj.rd = (8 + rdprime, 'f')
                instrObj.rs1 = (8 + rs1prime, 'x')
                instrObj.imm = uimm_6_5_3_2
            elif self.arch == 'rv64':
                instrObj.instr_name = 'c.ld'
                instrObj.rd = (8 + rdprime, 'x')
                instrObj.rs1 = (8 + rs1prime, 'x')
                instrObj.imm = uimm_7_6_5_3

        elif funct3 == 0b101:
            instrObj.instr_name = 'c.fsd'
            instrObj.rs1 = (8 + rs1prime, 'x')
            instrObj.rs2 = (8 + rs2prime, 'f')
            instrObj.imm = uimm_7_6_5_3

        elif funct3 == 0b110:
            instrObj.instr_name = 'c.sw'
            instrObj.rs1 = (8 + rs1prime, 'x')
            instrObj.rs2 = (8 + rs2prime, 'x')
            instrObj.imm = uimm_6_5_3_2

        elif funct3 == 0b111:
            if self.arch == 'rv32':
                instrObj.instr_name = 'c.fsw'
                instrObj.rs1 = (8 + rs1prime, 'x')
                instrObj.rs2 = (8 + rs2prime, 'f')
                instrObj.imm = uimm_6_5_3_2
            elif self.arch == 'rv64':
                instrObj.instr_name = 'c.sd'
                instrObj.rs1 = (8 + rs1prime, 'x')
                instrObj.rs2 = (8 + rs2prime, 'x')
                instrObj.imm = uimm_7_6_5_3

        return instrObj

    def quad1(self, instrObj):
        '''Parse instructions from Quad1 of the Compressed extension in the RISCV-ISA-Standard'''
        instr = instrObj.instr
        funct3 = (self.C_FUNCT3_MASK & instr) >> 13

        # Registers
        rdprime = (self.C1_RDPRIME_MASK & instr) >> 7
        rs1prime = (self.C1_RS1PRIME_MASK & instr) >> 7
        rs2prime = (self.C1_RS2PRIME_MASK & instr) >> 2
        rd = (self.C1_RD_MASK & instr) >> 7
        rs1 = (self.C1_RD_MASK & instr) >> 7

        imm_5 = (self.C1_IMM_5_MASK & instr) >> 7
        imm_4_0 = (self.C1_IMM_4_0_MASK & instr) >> 2
        imm = imm_5 + imm_4_0

        imm_lui = ((self.C1_IMM_17_MASK & instr) >> 12) + ((self.C1_IMM_16_12_MASK & instr)>>2)
        imm_j_5 = self.get_bit(instr, 2) << 5
        imm_j_3_1 = self.get_bit(instr,3) + (self.get_bit(instr, 4) << 1) + (self.get_bit(instr,5) << 2)
        imm_j_7 = self.get_bit(instr,6) << 7
        imm_j_6 = self.get_bit(instr,7) << 6
        imm_j_10 = self.get_bit(instr, 8) << 10
        imm_j_9_8 = self.get_bit(instr, 9) + (self.get_bit(instr,10)<< 1)
        imm_j_4 = self.get_bit(instr,11) << 4
        imm_j_11 = self.get_bit(instr, 12) << 11
        imm_j = imm_j_5 + (imm_j_3_1 << 1) + imm_j_7 + imm_j_6 + imm_j_10 + (imm_j_9_8 << 8) + imm_j_4 + imm_j_11

        imm_b_5 = self.get_bit(instr, 2) << 5
        imm_b_2_1 = self.get_bit(instr, 3) + (self.get_bit(instr,4) << 1)
        imm_b_7_6 = self.get_bit(instr, 5) + (self.get_bit(instr,6) << 1)
        imm_b_4_3 = self.get_bit(instr, 10) + (self.get_bit(instr,11) << 1)
        imm_b_8 = self.get_bit(instr, 12) << 8
        imm_b = imm_b_5 + (imm_b_2_1 << 1) + (imm_b_7_6 << 6) + (imm_b_4_3 << 3) + imm_b_8

        imm_addi_5 = self.get_bit(instr, 2) << 5
        imm_addi_8_7 = (self.get_bit(instr, 3) + (self.get_bit(instr, 4)<< 1) ) << 7
        imm_addi_6 = self.get_bit(instr, 5) << 6
        imm_addi_4 = self.get_bit(instr, 6) << 4
        imm_addi_9 = self.get_bit(instr, 12) << 9
        imm_addi = imm_addi_5 + imm_addi_8_7 + imm_addi_6 + imm_addi_4 + imm_addi_9

        op = (self.C1_MINOR_OP_MASK & instr) >> 10
        op2 = (self.C1_MINOR_OP2_MASK & instr) >> 5

        if funct3 == 0:
            instrObj.rs1 = (rs1, 'x')
            instrObj.rd = (rd, 'x')
            instrObj.imm = self.twos_comp(imm, 6)
            if rd == 0:
                instrObj.instr_name = 'c.nop'
            else:
                instrObj.instr_name = 'c.addi'
        elif funct3 == 1:
            if self.arch == 'rv32':
                instrObj.instr_name = 'c.jal'
                instrObj.imm = self.twos_comp(imm_j, 12)
                instrObj.rd = (1, 'x')
            elif rd !=0 :
                instrObj.instr_name = 'c.addiw'
                instrObj.imm = self.twos_comp(imm, 6)
                instrObj.rs1 = (rs1, 'x')
                instrObj.rd = (rd, 'x')
        elif funct3 == 2:
            instrObj.instr_name = 'c.li'
            instrObj.imm = self.twos_comp(imm, 6)
            instrObj.rd = (rd, 'x')
        elif funct3 == 3:
            if rd == 2 and imm_addi != 0:
                instrObj.instr_name = 'c.addi16sp'
                instrObj.rs1 = (2, 'x')
                instrObj.rd = (2, 'x')
                instrObj.imm = self.twos_comp(imm_addi, 10)
            elif rd != 2 and imm_lui !=0:
                instrObj.instr_name = 'c.lui'
                instrObj.imm = imm
                instrObj.rs1 = (rd, 'x')
                instrObj.rd = (rd, 'x')
        elif funct3 == 4:
            if op == 0 and imm != 0:
                instrObj.instr_name = 'c.srli'
                instrObj.rs1 = (8 + rs1prime, 'x')
                instrObj.rd = (8 + rdprime, 'x')
                instrObj.imm = imm
            elif op == 1 and imm !=0:
                instrObj.instr_name = 'c.srai'
                instrObj.rs1 = (8 + rs1prime, 'x')
                instrObj.rd = (8 + rdprime, 'x')
                instrObj.imm = imm
            elif op == 2:
                instrObj.instr_name = 'c.andi'
                instrObj.rs1 = (8 + rs1prime, 'x')
                instrObj.rd = (8 + rdprime, 'x')
                instrObj.imm = self.twos_comp(imm, 6)
            elif op == 3 and op2 == 0 and imm_5 == 0:
                instrObj.instr_name = 'c.sub'
                instrObj.rs1 = (8 + rs1prime, 'x')
                instrObj.rd = (8 + rdprime, 'x')
                instrObj.rs2 = (8 + rs2prime, 'x')
            elif op == 3 and op2 == 1 and imm_5 == 0:
                instrObj.instr_name = 'c.xor'
                instrObj.rs1 = (8 + rs1prime, 'x')
                instrObj.rd = (8 + rdprime, 'x')
                instrObj.rs2 = (8 + rs2prime, 'x')
            elif op == 3 and op2 == 2 and imm_5 == 0:
                instrObj.instr_name = 'c.or'
                instrObj.rs1 = (8 + rs1prime, 'x')
                instrObj.rd = (8 + rdprime, 'x')
                instrObj.rs2 = (8 + rs2prime, 'x')
            elif op == 3 and op2 == 3 and imm_5 == 0:
                instrObj.instr_name = 'c.and'
                instrObj.rs1 = (8 + rs1prime, 'x')
                instrObj.rd = (8 + rdprime, 'x')
                instrObj.rs2 = (8 + rs2prime, 'x')
            elif op == 3 and op2 == 0 and imm_5 != 0 and self.arch == 'rv64':
                instrObj.instr_name = 'c.subw'
                instrObj.rs1 = (8 + rs1prime, 'x')
                instrObj.rd = (8 + rdprime, 'x')
                instrObj.rs2 = (8 + rs2prime, 'x')
            elif op == 3 and op2 == 1 and imm_5 != 0 and self.arch == 'rv64':
                instrObj.instr_name = 'c.addw'
                instrObj.rs1 = (8 + rs1prime, 'x')
                instrObj.rd = (8 + rdprime, 'x')
                instrObj.rs2 = (8 + rs2prime, 'x')
        elif funct3 == 5:
            instrObj.instr_name = 'c.j'
            instrObj.rd = (0, 'x')
            instrObj.imm = self.twos_comp(imm_j, 12)
        elif funct3 == 6:
            instrObj.instr_name = 'c.beqz'
            instrObj.rs1 = (8 + rs1prime, 'x')
            instrObj.rs2 = (0 , 'x')
            instrObj.imm = self.twos_comp(imm_b, 9)
        elif funct3 == 7:
            instrObj.instr_name = 'c.bnez'
            instrObj.rs1 = (8 + rs1prime, 'x')
            instrObj.rs2 = (0, 'x')
            instrObj.imm = self.twos_comp(imm_b, 9)



        return instrObj

    C2_RS2_MASK = 0x007C
    C2_RD_MASK = 0x0F80


    def quad2(self, instrObj):
        '''Parse instructions from Quad2 of the Compressed extension in the RISCV-ISA-Standard'''
        instr = instrObj.instr
        funct3 = (self.C_FUNCT3_MASK & instr) >> 13

        imm_5 = self.get_bit(instr, 12) << 5
        imm_4_0 = (instr & 0x007c) >> 2
        imm_4_3 = (instr & 0x0060) >> 2
        imm_4 = self.get_bit(instr, 6) << 4
        imm_4_2 = (instr & 0x0070) >> 2
        imm_8_6 = (instr & 0x001C) << 5
        imm_9_6 = (instr & 0x003C) << 5
        imm_7_6 = (instr & 0x000C) << 4
        imm_8_6 = (instr & 0x001C) << 4

        imm_5_3 = (instr & 0x1c00) >> 7
        imm_s_8_6 = (instr & 0x0380) >> 1
        imm_5_2 = (instr & 0x1E00) >> 7
        imm_s_7_6 = (instr & 0x0180) >> 1

        rd = (self.C2_RD_MASK & instr) >> 7
        rs1 = (self.C2_RD_MASK & instr) >> 7
        rs2 = (self.C2_RS2_MASK & instr) >> 2

        imm_slli = imm_5 + imm_4_0
        imm_fldsp = imm_5 + imm_4_3 + imm_8_6
        imm_lwsp = imm_5 + imm_4_2 + imm_7_6
        imm_ldsp = imm_5 + imm_4_3 + imm_8_6
        imm_fsdsp = imm_5_3 + imm_s_8_6
        imm_swsp = imm_5_2 + imm_s_7_6

        if funct3 == 0 and imm_slli !=0 and rd !=0:
            instrObj.instr_name = 'c.slli'
            instrObj.rd = (rd, 'x')
            instrObj.rs1 = (rs1, 'x')
            instrObj.imm = imm_slli
        elif funct3 == 1 and self.arch == 'rv64':
            instrObj.instr_name = 'c.fldsp'
            instrObj.rd = (rd, 'f')
            instrObj.imm = imm_fldsp
            instrObj.rs1 = (2, 'x')
        elif funct3 == 2 and rd != 0:
            instrObj.instr_name = 'c.lwsp'
            instrObj.rs1 = (2, 'x')
            instrObj.rd = (rd, 'x')
            instrObj.imm = imm_lwsp
        elif funct3 == 3 and self.arch == 'rv32':
            instrObj.instr_name = 'c.flwsp'
            instrObj.rd = (rd, 'f')
            instrObj.rs1 = (2, 'x')
            instrObj.imm = imm_lwsp
        elif funct3 == 3 and self.arch == 'rv64':
            instrObj.instr_name = 'c.ldsp'
            instrObj.rd = (rd, 'f')
            instrObj.rs1 = (2, 'x')
            instrObj.imm = imm_ldsp
        elif funct3 == 4 and rs1 != 0 and imm_5 == 0 and rs2 == 0:
            instrObj.instr_name = 'c.jr'
            instrObj.rs1 = (rs1, 'x')
            instrObj.imm = 0
        elif funct3 == 4 and rs2!=0 and imm_5 == 0:
            instrObj.instr_name = 'c.mv'
            instrObj.rs2 = (rs2, 'x')
            instrObj.rd = (rd, 'x')
        elif funct3 == 4 and rd ==0 and rs2 == 0 and imm_5 == 32:
            instrObj.instr_name = 'c.ebreak'
        elif funct3 == 4 and imm_5 == 32 and rs1 !=0 and rs2 == 0:
            instrObj.instr_name = 'c.jalr'
            instrObj.rs1 = (rs1, 'x')
            instrObj.rd = (1, 'x')
        elif funct3 == 4 and imm_5 == 32 and rs2 !=0 :
            instrObj.instr_name = 'c.add'
            instrObj.rs1 = (rs1, 'x')
            instrObj.rs2 = (rs2, 'x')
            instrObj.rd = (rd, 'x')
        elif funct3 == 5:
            instrObj.instr_name = 'c.fsdsp'
            instrObj.rs2 = (rs2, 'f')
            instrObj.imm = imm_fsdsp
            instrObj.rs1 = (2 , 'x')
        elif funct3 == 6:
            instrObj.instr_name = 'c.swsp'
            instrObj.rs2 = (rs2, 'x')
            instrObj.imm = imm_swsp
            instrObj.rs1 = (2 , 'x')
        elif funct3 == 7 and self.arch == 'rv32':
            instrObj.instr_name = 'c.fswsp'
            instrObj.rs2 = (rs2, 'f')
            instrObj.rs1 = (2, 'x')
            instrObj.imm = imm_swsp
        elif funct3 == 7 and self.arch == 'rv64':
            instrObj.instr_name = 'c.sdsp'
            instrObj.rs2 = (rs2, 'x')
            instrObj.imm = imm_fsdsp
            instrObj.rs1 = (2 , 'x')
        return instrObj



    def parseCompressedInstruction(self, instrObj_temp):
        ''' Parse a compressed instruction
            Args: instrObj_temp that contains partially filled data
            Returns: (instr_obj) with all fields filled
        '''
        instr = instrObj_temp.instr
        opcode = self.FIRST2_MASK & instr
        try:
            instrObj = self.C_OPCODES[opcode](instrObj_temp)
        except KeyError as e:
            print("Instruction not found", hex(instr))
            return None

        return instrObj

    def parseStandardInstruction(self, instrObj_temp):
        ''' Parse an input line and decode the instruction
            Args: instrObj_temp that contains partially filled data
            Returns: (instr_obj) with all fields filled
        '''
        instr = instrObj_temp.instr
        opcode = self.extractOpcode(instr)
        try:
            instrObj = self.OPCODES[opcode](instrObj_temp)
        except KeyError as e:
            print("Instruction not found", hex(instr))
            return None

        return instrObj

    @plugins.decoderHookImpl
    def decode(self, instrObj_temp):
        ''' Decodes the type of instruction
            Returns: instruction object
        '''
        instr = instrObj_temp.instr
        first_two_bits = self.FIRST2_MASK & instr
        if first_two_bits == 0b11:
            instrObj = self.parseStandardInstruction(instrObj_temp)
            return instrObj

        else:
            instrObj = self.parseCompressedInstruction(instrObj_temp)
            return instrObj







