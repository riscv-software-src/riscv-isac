import struct


unsgn_rs1 = ['sw','sd','sh','sb','ld','lw','lwu','lh','lhu','lb', 'lbu','flw','fld','fsw','fsd',\
        'bgeu', 'bltu', 'sltiu', 'sltu','c.lw','c.ld','c.lwsp','c.ldsp',\
        'c.sw','c.sd','c.swsp','c.sdsp','mulhu','divu','remu','divuw',\
        'remuw','aes64ds','aes64dsm','aes64es','aes64esm','aes64ks2',\
        'sha256sum0','sha256sum1','sha256sig0','sha256sig1','sha512sig0',\
        'sha512sum1r','sha512sum0r','sha512sig1l','sha512sig0l','sha512sig1h','sha512sig0h',\
        'sha512sig1','sha512sum0','sha512sum1','sm3p0','sm3p1','aes64im',\
        'sm4ed','sm4ks','ror','rol','rori','rorw','rolw','roriw','clmul','clmulh','clmulr',\
        'andn','orn','xnor','pack','packh','packu','packuw','packw',\
        'xperm.n','xperm.b','grevi','aes64ks1i', 'shfli', 'unshfli', \
        'aes32esmi', 'aes32esi', 'aes32dsmi', 'aes32dsi','bclr','bext','binv',\
        'bset','zext.h','sext.h','sext.b','minu','maxu','orc.b','add.uw','sh1add.uw',\
        'sh2add.uw','sh3add.uw','slli.uw','clz','clzw','ctz','ctzw','cpop','cpopw','rev8',\
        'bclri','bexti','binvi','bseti','fcvt.d.wu','fcvt.s.wu','fcvt.d.lu','fcvt.s.lu']
unsgn_rs2 = ['bgeu', 'bltu', 'sltiu', 'sltu', 'sll', 'srl', 'sra','mulhu',\
        'mulhsu','divu','remu','divuw','remuw','aes64ds','aes64dsm','aes64es',\
        'aes64esm','aes64ks2','sm4ed','sm4ks','ror','rol','rorw','rolw','clmul',\
        'clmulh','clmulr','andn','orn','xnor','pack','packh','packu','packuw','packw',\
        'xperm.n','xperm.b', 'aes32esmi', 'aes32esi', 'aes32dsmi', 'aes32dsi',\
        'sha512sum1r','sha512sum0r','sha512sig1l','sha512sig1h','sha512sig0l','sha512sig0h','fsw',\
        'bclr','bext','binv','bset','minu','maxu','add.uw','sh1add.uw','sh2add.uw','sh3add.uw']
f_instrs_pref = ['fadd', 'fclass', 'fcvt', 'fdiv', 'feq', 'fld', 'fle', 'flt', 'flw', 'fmadd',\
        'fmax', 'fmin', 'fmsub', 'fmul', 'fmv', 'fnmadd', 'fnmsub', 'fsd', 'fsgnj', 'fsqrt',\
        'fsub', 'fsw']


instr_var_evaluator_funcs = {} # dictionary for holding registered evaluator funcs
def evaluator_func(instr_var_name, cond): # decorator for registering evaluator funcs
    def evaluator_func_registration_decorator(func):
        if instr_var_name in instr_var_evaluator_funcs:
            instr_var_evaluator_funcs[instr_var_name].append((cond, func))
        else:
            instr_var_evaluator_funcs[instr_var_name] = [(cond, func)]
        return func
    return evaluator_func_registration_decorator


''' Instruction Object '''
class instructionObject():
    '''
        Instruction object class
    '''
    def __init__(
        self,
        instr,
        instr_name,
        instr_addr,
        rd = None,
        rs1 = None,
        rs2 = None,
        rs3 = None,
        imm = None,
        zimm = None,
        csr = None,
        shamt = None,
        succ = None,
        pred = None,
        rl = None,
        aq = None,
        rm = None,
        reg_commit = None,
        csr_commit = None,
        mnemonic = None
    ):

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
        self.instr = instr
        self.instr_name = instr_name
        self.instr_addr = instr_addr
        self.rd = rd
        self.rs1 = rs1
        self.rs2 = rs2
        self.rs3 = rs3
        self.imm = imm
        self.zimm = zimm
        self.csr = csr
        self.shamt = shamt
        self.succ = succ
        self.pred = pred
        self.rl = rl
        self.aq = aq
        self.rm = rm
        self.reg_commit = reg_commit
        self.csr_commit = csr_commit
        self.mnemonic = mnemonic
        self.is_rvp = False
        self.rs1_nregs = 1
        self.rs2_nregs = 1
        self.rs3_nregs = 1
        self.rd_nregs = 1


    def evaluate_instr_vars(self, xlen, flen, arch_state, csr_regfile, instr_vars):
        '''
        This function populates the provided instr_vars dictionary
        with the necessary fields to evaluate the coverpoints.
        '''
        self._xlen = xlen
        self._flen = flen

        # create signed/unsigned conversion params
        if xlen == 32:
            self._unsgn_sz = '>I'
            self._sgn_sz = '>i'
        else:
            self._unsgn_sz = '>Q'
            self._sgn_sz = '>q'

        self._iflen = flen
        if self.instr_name.endswith(".s") or 'fmv.x.w' in self.instr_name:
            self._iflen = 32
        elif self.instr_name.endswith(".d"):
            self._iflen = 64

        self._fsgn_sz = '>Q' if flen==64 else '>I'

        imm_val = instr_vars.get('imm_val', None)

        # capture the register operand values
        rs1_val = self.evaluate_instr_var("rs1_val", arch_state)
        rs2_val = self.evaluate_instr_var("rs2_val", arch_state)
        rs3_val = self.evaluate_instr_var("rs3_val", arch_state)

        ea_align = None
        # the ea_align variable is used by the eval statements of the
        # coverpoints for conditional ops and memory ops
        if self.instr_name in ['jal','bge','bgeu','blt','bltu','beq','bne']:
            ea_align = (self.instr_addr+(imm_val<<1)) % 4
        if self.instr_name == "jalr":
            ea_align = (rs1_val + imm_val) % 4
        if self.instr_name in ['sw','sh','sb','lw','lhu','lh','lb','lbu','lwu','flw','fsw']:
            ea_align = (rs1_val + imm_val) % 4
        if self.instr_name in ['ld','sd','fld','fsd']:
            ea_align = (rs1_val + imm_val) % 8

        instr_vars.update({
            'rs1_val': rs1_val,
            'rs2_val': rs2_val,
            'rs3_val': rs3_val,
            'rm_val': self.rm,
            'ea_align': ea_align,
            'xlen': self._xlen,
            'flen': self._flen,
            'iflen': self._iflen
        })

        # derived instruction variables specific to an extension
        ext_specific_vars = self.evaluate_instr_var("ext_specific_vars", instr_vars, arch_state, csr_regfile)
        if ext_specific_vars is not None:
            instr_vars.update(ext_specific_vars)


    def update_arch_state(self, arch_state, csr_regfile):
        '''
        This function updates the arch state and csr regfiles
        with the effect of this instruction.
        '''
        arch_state.pc = self.instr_addr

        commitvalue = self.reg_commit
        if commitvalue is not None:
            if self.rd[1] == 'x':
                arch_state.x_rf[int(commitvalue[1])] =  str(commitvalue[2][2:])
            elif self.rd[1] == 'f':
                arch_state.f_rf[int(commitvalue[1])] =  str(commitvalue[2][2:])

        csr_commit = self.csr_commit
        if csr_commit is not None:
            for commits in csr_commit:
                if (commits[0] == "CSR"):
                    csr_regfile[commits[1]] = str(commits[2][2:])


    def evaluate_instr_var(self, instr_var_name, *args):
        for cond, func in instr_var_evaluator_funcs.get(instr_var_name, []):
            if cond(
                instr_name = self.instr_name,
                rs1 = self.rs1,
                rs2 = self.rs2,
                rs3 = self.rs3,
                is_rvp = self.is_rvp
            ): # could just instr_name suffice?
                return func(self, *args)

        return None


    '''
    Evaluator funcs for rs1_val
    '''
    @evaluator_func("rs1_val", lambda **params: params['instr_name'] in unsgn_rs1 and params['rs1'] is not None)
    def evaluate_rs1_val_unsgn(self, arch_state):
        return self.evaluate_reg_val_unsgn(self.rs1[0], arch_state)


    @evaluator_func("rs1_val", lambda **params: params['is_rvp'] and params['rs1'] is not None)
    def evaluate_rs1_val_p_ext(self, arch_state):
        return self.evaluate_reg_val_p_ext(self.rs1[0], self.rs1_nregs, arch_state)


    # this gets messy because disjoint conditions are needed when we use the decoders, as the order in the list might vary
    @evaluator_func("rs1_val", lambda **params: not params['instr_name'] in unsgn_rs1 and not params['is_rvp'] and params['rs1'] is not None and params['rs1'][1] == 'x')
    def evaluate_rs1_val_sgn(self, arch_state):
        return self.evaluate_reg_val_sgn(self.rs1[0], arch_state)


    @evaluator_func("rs1_val", lambda **params: not params['instr_name'] in unsgn_rs1 and not params['is_rvp'] and params['rs1'] is not None and params['rs1'][1] == 'f')
    def evaluate_rs1_val_fsgn(self, arch_state):
        return self.evaluate_reg_val_fsgn(self.rs1[0], arch_state)


    '''
    Evaluator funcs for rs2_val
    '''
    @evaluator_func("rs2_val", lambda **params: params['instr_name'] in unsgn_rs2 and params['rs2'] is not None)
    def evaluate_rs2_val_unsgn(self, arch_state):
        return self.evaluate_reg_val_unsgn(self.rs2[0], arch_state)


    @evaluator_func("rs2_val", lambda **params: params['is_rvp'] and params['rs2'] is not None)
    def evaluate_rs2_val_p_ext(self, arch_state):
        return self.evaluate_reg_val_p_ext(self.rs2[0], self.rs2_nregs, arch_state)


    # this gets messy because disjoint conditions are needed when we use the decoders, as the order in the list might vary
    @evaluator_func("rs2_val", lambda **params: not params['instr_name'] in unsgn_rs2 and not params['is_rvp'] and params['rs2'] is not None and params['rs2'][1] == 'x')
    def evaluate_rs2_val_sgn(self, arch_state):
        return self.evaluate_reg_val_sgn(self.rs2[0], arch_state)


    @evaluator_func("rs2_val", lambda **params: not params['instr_name'] in unsgn_rs2 and not params['is_rvp'] and params['rs2'] is not None and params['rs2'][1] == 'f')
    def evaluate_rs2_val_fsgn(self, arch_state):
        return self.evaluate_reg_val_fsgn(self.rs2[0], arch_state)


    '''
    Evaluator funcs for rs3_val
    '''
    @evaluator_func("rs3_val", lambda **params: params['rs3'] is not None and params['rs3'][1] == 'f')
    def evaluate_rs3_val_fsgn(self, arch_state):
        return self.evaluate_reg_val_fsgn(self.rs3[0], arch_state)


    '''
    Evaluator funcs for extension specific variables
    '''
    @evaluator_func("ext_specific_vars", lambda **params: any([params['instr_name'].startswith(pref) for pref in f_instrs_pref]))
    def evaluate_f_ext_sem(self, instr_vars, arch_state, csr_regfile):
        f_ext_vars = {}

        f_ext_vars['fcsr'] = int(csr_regfile['fcsr'], 16)

        if self.rs1 is not None and self.rs1[1] == 'f':
            self.evaluate_reg_sem_f_ext(instr_vars['rs1_val'], "1", f_ext_vars)
        if self.rs2 is not None and self.rs2[1] == 'f':
            self.evaluate_reg_sem_f_ext(instr_vars['rs2_val'], "2", f_ext_vars)
        if self.rs3 is not None and self.rs3[1] == 'f':
            self.evaluate_reg_sem_f_ext(instr_vars['rs3_val'], "3", f_ext_vars)

        return f_ext_vars


    '''
    Helper functions for unpacking register values
    '''
    def evaluate_reg_val_unsgn(self, reg_idx, arch_state):
        return struct.unpack(self._unsgn_sz, bytes.fromhex(arch_state.x_rf[reg_idx]))[0]


    def evaluate_reg_val_sgn(self, reg_idx, arch_state):
        return struct.unpack(self._sgn_sz, bytes.fromhex(arch_state.x_rf[reg_idx]))[0]


    def evaluate_reg_val_fsgn(self, reg_idx, arch_state):
            return struct.unpack(self._fsgn_sz, bytes.fromhex(arch_state.f_rf[reg_idx]))[0]


    def evaluate_reg_val_p_ext(self, reg_idx, nregs, arch_state):
        reg_val = self.evaluate_reg_val_unsgn(reg_idx, arch_state)
        if nregs == 2:
            reg_hi_val = evaluate_reg_val_unsgn(reg_idx+1, arch_state)
            reg_val = (reg_hi_val << 32) | reg_val
        return reg_val


    def evaluate_reg_sem_f_ext(self, reg_val, postfix, f_ext_vars):
        '''
        This function expands reg_val and defines the respective sign, exponent and mantissa correspondence
        '''
        if reg_val is None:
            return

        if self._iflen == 32:
            e_sz = 8
            m_sz = 23
        else:
            e_sz = 11
            m_sz = 52
        bin_val = ('{:0'+str(self._flen)+'b}').format(reg_val)

        if self._flen > self._iflen:
            f_ext_vars['rs'+postfix+'_nan_prefix'] = int(bin_val[0:self._flen-self._iflen],2)
            bin_val = bin_val[self._flen-self._iflen:]

        f_ext_vars['fs'+postfix] = int(bin_val[0], 2)
        f_ext_vars['fe'+postfix] = int(bin_val[1:e_sz+1], 2)
        f_ext_vars['fm'+postfix] = int(bin_val[e_sz+1:], 2)


    def __str__(self):
        line = 'instr: '+ str(self.instr)+ ' addr: '+ str(hex(self.instr_addr)) +' instr_name: '+ str(self.instr_name)
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
        if self.zimm:
            line+= ' zimm: '+ str(self.zimm)
        if self.shamt:
            line+= ' shamt: '+ str(self.shamt)
        if self.succ:
            line+= ' succ: '+ str(self.succ)
        if self.pred:
            line+= ' pred: '+ str(self.pred)
        if self.rl:
            line+= ' rl: '+ str(self.rl)
        if self.aq:
            line+= ' aq: '+ str(self.aq)
        if self.rm:
            line+= ' rm: '+ str(self.rm)
        if self.reg_commit:
            line+= ' reg_commit: '+ str(self.reg_commit)
        if self.csr_commit:
            line+= ' csr_commit: '+ str(self.csr_commit)
        if self.mnemonic:
            line+= ' mnemonic: '+ str(self.mnemonic)
        return line
