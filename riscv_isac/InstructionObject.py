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
        self.init_rvp_dictionary()


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


    # Put the following function in instructionObject.py 
    def init_rvp_dictionary(self):

        # Create RVP Dictiory 0 for instruction:  clrs8  clrs16  clrs32  clo8  clo16  clo32  clz8  clz16  clz32  kabs8  kabs16  kabsw  sunpkd810  sunpkd820  sunpkd830  sunpkd831  sunpkd832  swap8  zunpkd810  zunpkd820  zunpkd830  zunpkd831  zunpkd832  kabs32
        self.rvp_dict_0 = {}
        self.rvp_dict_0[0xae000077] = 'clrs8'
        self.rvp_dict_0[0xae800077] = 'clrs16'
        self.rvp_dict_0[0xaf800077] = 'clrs32'
        self.rvp_dict_0[0xae300077] = 'clo8'
        self.rvp_dict_0[0xaeb00077] = 'clo16'
        self.rvp_dict_0[0xafb00077] = 'clo32'
        self.rvp_dict_0[0xae100077] = 'clz8'
        self.rvp_dict_0[0xae900077] = 'clz16'
        self.rvp_dict_0[0xaf900077] = 'clz32'
        self.rvp_dict_0[0xad000077] = 'kabs8'
        self.rvp_dict_0[0xad100077] = 'kabs16'
        self.rvp_dict_0[0xad400077] = 'kabsw'
        self.rvp_dict_0[0xac800077] = 'sunpkd810'
        self.rvp_dict_0[0xac900077] = 'sunpkd820'
        self.rvp_dict_0[0xaca00077] = 'sunpkd830'
        self.rvp_dict_0[0xacb00077] = 'sunpkd831'
        self.rvp_dict_0[0xad300077] = 'sunpkd832'
        self.rvp_dict_0[0xad800077] = 'swap8'
        self.rvp_dict_0[0xacc00077] = 'zunpkd810'
        self.rvp_dict_0[0xacd00077] = 'zunpkd820'
        self.rvp_dict_0[0xace00077] = 'zunpkd830'
        self.rvp_dict_0[0xacf00077] = 'zunpkd831'
        self.rvp_dict_0[0xad700077] = 'zunpkd832'
        self.rvp_dict_0[0xad200077] = 'kabs32'

        # Create RVP Dictiory 1 for instruction:  add8  add16  ave  bitrev  cmpeq8  cmpeq16  cras16  crsa16  kadd8  kadd16  kcras16  kcrsa16  khm8  khmx8  khm16  khmx16  ksll8  ksll16  kslra8  kslra8.u  kslra16  kslra16.u  ksub8  ksub16  maxw  minw  pbsad  pbsada  radd8  radd16  rcras16  rcrsa16  rsub8  rsub16  scmple8  scmple16  scmplt8  scmplt16  sll8  sll16  smaqa  smaqa.su  smax8  smax16  smin8  smin16  smul8  smulx8  smul16  smulx16  sra8  sra8.u  sra16  sra16.u  srl8  srl8.u  srl16  srl16.u  sub8  sub16  ucmple8  ucmple16  ucmplt8  ucmplt16  ukadd8  ukadd16  ukcras16  ukcrsa16  uksub8  uksub16  umaqa  umax8  umax16  umin8  umin16  umul8  umulx8  umul16  umulx16  uradd8  uradd16  urcras16  urcrsa16  ursub8  ursub16  wext
        self.rvp_dict_1 = {}
        self.rvp_dict_1[0x48000077] = 'add8'
        self.rvp_dict_1[0x40000077] = 'add16'
        self.rvp_dict_1[0xe0000077] = 'ave'
        self.rvp_dict_1[0xe6000077] = 'bitrev'
        self.rvp_dict_1[0x4e000077] = 'cmpeq8'
        self.rvp_dict_1[0x4c000077] = 'cmpeq16'
        self.rvp_dict_1[0x44000077] = 'cras16'
        self.rvp_dict_1[0x46000077] = 'crsa16'
        self.rvp_dict_1[0x18000077] = 'kadd8'
        self.rvp_dict_1[0x10000077] = 'kadd16'
        self.rvp_dict_1[0x14000077] = 'kcras16'
        self.rvp_dict_1[0x16000077] = 'kcrsa16'
        self.rvp_dict_1[0x8e000077] = 'khm8'
        self.rvp_dict_1[0x9e000077] = 'khmx8'
        self.rvp_dict_1[0x86000077] = 'khm16'
        self.rvp_dict_1[0x96000077] = 'khmx16'
        self.rvp_dict_1[0x6c000077] = 'ksll8'
        self.rvp_dict_1[0x64000077] = 'ksll16'
        self.rvp_dict_1[0x5e000077] = 'kslra8'
        self.rvp_dict_1[0x6e000077] = 'kslra8.u'
        self.rvp_dict_1[0x56000077] = 'kslra16'
        self.rvp_dict_1[0x66000077] = 'kslra16.u'
        self.rvp_dict_1[0x1a000077] = 'ksub8'
        self.rvp_dict_1[0x12000077] = 'ksub16'
        self.rvp_dict_1[0xf2000077] = 'maxw'
        self.rvp_dict_1[0xf0000077] = 'minw'
        self.rvp_dict_1[0xfc000077] = 'pbsad'
        self.rvp_dict_1[0xfe000077] = 'pbsada'
        self.rvp_dict_1[0x08000077] = 'radd8'
        self.rvp_dict_1[0x00000077] = 'radd16'
        self.rvp_dict_1[0x04000077] = 'rcras16'
        self.rvp_dict_1[0x06000077] = 'rcrsa16'
        self.rvp_dict_1[0x0a000077] = 'rsub8'
        self.rvp_dict_1[0x02000077] = 'rsub16'
        self.rvp_dict_1[0x1e000077] = 'scmple8'
        self.rvp_dict_1[0x1c000077] = 'scmple16'
        self.rvp_dict_1[0x0e000077] = 'scmplt8'
        self.rvp_dict_1[0x0c000077] = 'scmplt16'
        self.rvp_dict_1[0x5c000077] = 'sll8'
        self.rvp_dict_1[0x54000077] = 'sll16'
        self.rvp_dict_1[0xc8000077] = 'smaqa'
        self.rvp_dict_1[0xca000077] = 'smaqa.su'
        self.rvp_dict_1[0x8a000077] = 'smax8'
        self.rvp_dict_1[0x82000077] = 'smax16'
        self.rvp_dict_1[0x88000077] = 'smin8'
        self.rvp_dict_1[0x80000077] = 'smin16'
        self.rvp_dict_1[0xa8000077] = 'smul8'
        self.rvp_dict_1[0xaa000077] = 'smulx8'
        self.rvp_dict_1[0xa0000077] = 'smul16'
        self.rvp_dict_1[0xa2000077] = 'smulx16'
        self.rvp_dict_1[0x58000077] = 'sra8'
        self.rvp_dict_1[0x68000077] = 'sra8.u'
        self.rvp_dict_1[0x50000077] = 'sra16'
        self.rvp_dict_1[0x60000077] = 'sra16.u'
        self.rvp_dict_1[0x5a000077] = 'srl8'
        self.rvp_dict_1[0x6a000077] = 'srl8.u'
        self.rvp_dict_1[0x52000077] = 'srl16'
        self.rvp_dict_1[0x62000077] = 'srl16.u'
        self.rvp_dict_1[0x4a000077] = 'sub8'
        self.rvp_dict_1[0x42000077] = 'sub16'
        self.rvp_dict_1[0x3e000077] = 'ucmple8'
        self.rvp_dict_1[0x3c000077] = 'ucmple16'
        self.rvp_dict_1[0x2e000077] = 'ucmplt8'
        self.rvp_dict_1[0x2c000077] = 'ucmplt16'
        self.rvp_dict_1[0x38000077] = 'ukadd8'
        self.rvp_dict_1[0x30000077] = 'ukadd16'
        self.rvp_dict_1[0x34000077] = 'ukcras16'
        self.rvp_dict_1[0x36000077] = 'ukcrsa16'
        self.rvp_dict_1[0x3a000077] = 'uksub8'
        self.rvp_dict_1[0x32000077] = 'uksub16'
        self.rvp_dict_1[0xcc000077] = 'umaqa'
        self.rvp_dict_1[0x9a000077] = 'umax8'
        self.rvp_dict_1[0x92000077] = 'umax16'
        self.rvp_dict_1[0x98000077] = 'umin8'
        self.rvp_dict_1[0x90000077] = 'umin16'
        self.rvp_dict_1[0xb8000077] = 'umul8'
        self.rvp_dict_1[0xba000077] = 'umulx8'
        self.rvp_dict_1[0xb0000077] = 'umul16'
        self.rvp_dict_1[0xb2000077] = 'umulx16'
        self.rvp_dict_1[0x28000077] = 'uradd8'
        self.rvp_dict_1[0x20000077] = 'uradd16'
        self.rvp_dict_1[0x24000077] = 'urcras16'
        self.rvp_dict_1[0x26000077] = 'urcrsa16'
        self.rvp_dict_1[0x2a000077] = 'ursub8'
        self.rvp_dict_1[0x22000077] = 'ursub16'
        self.rvp_dict_1[0xce000077] = 'wext'

        # Create RVP Dictiory 2 for instruction:  insb  kslli8  sclip8  slli8  srai8  srai8.u  srli8  srli8.u  uclip8
        self.rvp_dict_2 = {}
        self.rvp_dict_2[0xac000077] = 'insb'
        self.rvp_dict_2[0x7c800077] = 'kslli8'
        self.rvp_dict_2[0x8c000077] = 'sclip8'
        self.rvp_dict_2[0x7c000077] = 'slli8'
        self.rvp_dict_2[0x78000077] = 'srai8'
        self.rvp_dict_2[0x78800077] = 'srai8.u'
        self.rvp_dict_2[0x7a000077] = 'srli8'
        self.rvp_dict_2[0x7a800077] = 'srli8.u'
        self.rvp_dict_2[0x8d000077] = 'uclip8'

        # Create RVP Dictiory 3 for instruction:  kslli16  sclip16  slli16  srai16  srai16.u  srli16  srli16.u  uclip16
        self.rvp_dict_3 = {}
        self.rvp_dict_3[0x75000077] = 'kslli16'
        self.rvp_dict_3[0x84000077] = 'sclip16'
        self.rvp_dict_3[0x74000077] = 'slli16'
        self.rvp_dict_3[0x70000077] = 'srai16'
        self.rvp_dict_3[0x71000077] = 'srai16.u'
        self.rvp_dict_3[0x72000077] = 'srli16'
        self.rvp_dict_3[0x73000077] = 'srli16.u'
        self.rvp_dict_3[0x85000077] = 'uclip16'

        # Create RVP Dictiory 4 for instruction:  sclip32  uclip32  wexti
        self.rvp_dict_4 = {}
        self.rvp_dict_4[0xe4000077] = 'sclip32'
        self.rvp_dict_4[0xf4000077] = 'uclip32'
        self.rvp_dict_4[0xde000077] = 'wexti'

        # Create RVP Dictiory 5 for instruction:  bitrevi
        self.rvp_dict_5 = {}
        self.rvp_dict_5[0xe8000077] = 'bitrevi'

        # Create RVP Dictiory 6 for instruction:  add64  kadd64  kaddh  kaddw  kdmbb  kdmbt  kdmtt  kdmabb  kdmabt  kdmatt  khmbb  khmbt  khmtt  kmabb  kmabt  kmatt  kmada  kmaxda  kmads  kmadrs  kmaxds  kmar64  kmda  kmxda  kmmac  kmmac.u  kmmawb  kmmawb.u  kmmawb2  kmmawb2.u  kmmawt  kmmawt.u  kmmawt2  kmmawt2.u  kmmsb  kmmsb.u  kmmwb2  kmmwb2.u  kmmwt2  kmmwt2.u  kmsda  kmsxda  kmsr64  ksllw  kslraw  kslraw.u  ksub64  ksubh  ksubw  kwmmul  kwmmul.u  maddr32  msubr32  mulr64  mulsr64  pkbb16  pkbt16  pktt16  pktb16  radd64  raddw  rsub64  rsubw  smal  smalbb  smalbt  smaltt  smalda  smalxda  smalds  smaldrs  smalxds  smar64  smbb16  smbt16  smtt16  smds  smdrs  smxds  smmul  smmul.u  smmwb  smmwb.u  smmwt  smmwt.u  smslda  smslxda  smsr64  sra.u  sub64  ukadd64  ukaddh  ukaddw  ukmar64  ukmsr64  uksub64  uksubh  uksubw  umar64  umsr64  uradd64  uraddw  ursub64  ursubw  kdmbb16  kdmbt16  kdmtt16  kdmabb16  kdmabt16  kdmatt16  khmbb16  khmbt16  khmtt16
        self.rvp_dict_6 = {}
        self.rvp_dict_6[0xc0001077] = 'add64'
        self.rvp_dict_6[0x90001077] = 'kadd64'
        self.rvp_dict_6[0x04001077] = 'kaddh'
        self.rvp_dict_6[0x00001077] = 'kaddw'
        self.rvp_dict_6[0x0a001077] = 'kdmbb'
        self.rvp_dict_6[0x1a001077] = 'kdmbt'
        self.rvp_dict_6[0x2a001077] = 'kdmtt'
        self.rvp_dict_6[0xd2001077] = 'kdmabb'
        self.rvp_dict_6[0xe2001077] = 'kdmabt'
        self.rvp_dict_6[0xf2001077] = 'kdmatt'
        self.rvp_dict_6[0x0c001077] = 'khmbb'
        self.rvp_dict_6[0x1c001077] = 'khmbt'
        self.rvp_dict_6[0x2c001077] = 'khmtt'
        self.rvp_dict_6[0x5a001077] = 'kmabb'
        self.rvp_dict_6[0x6a001077] = 'kmabt'
        self.rvp_dict_6[0x7a001077] = 'kmatt'
        self.rvp_dict_6[0x48001077] = 'kmada'
        self.rvp_dict_6[0x4a001077] = 'kmaxda'
        self.rvp_dict_6[0x5c001077] = 'kmads'
        self.rvp_dict_6[0x6c001077] = 'kmadrs'
        self.rvp_dict_6[0x7c001077] = 'kmaxds'
        self.rvp_dict_6[0x94001077] = 'kmar64'
        self.rvp_dict_6[0x38001077] = 'kmda'
        self.rvp_dict_6[0x3a001077] = 'kmxda'
        self.rvp_dict_6[0x60001077] = 'kmmac'
        self.rvp_dict_6[0x70001077] = 'kmmac.u'
        self.rvp_dict_6[0x46001077] = 'kmmawb'
        self.rvp_dict_6[0x56001077] = 'kmmawb.u'
        self.rvp_dict_6[0xce001077] = 'kmmawb2'
        self.rvp_dict_6[0xde001077] = 'kmmawb2.u'
        self.rvp_dict_6[0x66001077] = 'kmmawt'
        self.rvp_dict_6[0x76001077] = 'kmmawt.u'
        self.rvp_dict_6[0xee001077] = 'kmmawt2'
        self.rvp_dict_6[0xfe001077] = 'kmmawt2.u'
        self.rvp_dict_6[0x42001077] = 'kmmsb'
        self.rvp_dict_6[0x52001077] = 'kmmsb.u'
        self.rvp_dict_6[0x8e001077] = 'kmmwb2'
        self.rvp_dict_6[0x9e001077] = 'kmmwb2.u'
        self.rvp_dict_6[0xae001077] = 'kmmwt2'
        self.rvp_dict_6[0xbe001077] = 'kmmwt2.u'
        self.rvp_dict_6[0x4c001077] = 'kmsda'
        self.rvp_dict_6[0x4e001077] = 'kmsxda'
        self.rvp_dict_6[0x96001077] = 'kmsr64'
        self.rvp_dict_6[0x26001077] = 'ksllw'
        self.rvp_dict_6[0x6e001077] = 'kslraw'
        self.rvp_dict_6[0x7e001077] = 'kslraw.u'
        self.rvp_dict_6[0x92001077] = 'ksub64'
        self.rvp_dict_6[0x06001077] = 'ksubh'
        self.rvp_dict_6[0x02001077] = 'ksubw'
        self.rvp_dict_6[0x62001077] = 'kwmmul'
        self.rvp_dict_6[0x72001077] = 'kwmmul.u'
        self.rvp_dict_6[0xc4001077] = 'maddr32'
        self.rvp_dict_6[0xc6001077] = 'msubr32'
        self.rvp_dict_6[0xf0001077] = 'mulr64'
        self.rvp_dict_6[0xe0001077] = 'mulsr64'
        self.rvp_dict_6[0x0e001077] = 'pkbb16'
        self.rvp_dict_6[0x1e001077] = 'pkbt16'
        self.rvp_dict_6[0x2e001077] = 'pktt16'
        self.rvp_dict_6[0x3e001077] = 'pktb16'
        self.rvp_dict_6[0x80001077] = 'radd64'
        self.rvp_dict_6[0x20001077] = 'raddw'
        self.rvp_dict_6[0x82001077] = 'rsub64'
        self.rvp_dict_6[0x22001077] = 'rsubw'
        self.rvp_dict_6[0x5e001077] = 'smal'
        self.rvp_dict_6[0x88001077] = 'smalbb'
        self.rvp_dict_6[0x98001077] = 'smalbt'
        self.rvp_dict_6[0xa8001077] = 'smaltt'
        self.rvp_dict_6[0x8c001077] = 'smalda'
        self.rvp_dict_6[0x9c001077] = 'smalxda'
        self.rvp_dict_6[0x8a001077] = 'smalds'
        self.rvp_dict_6[0x9a001077] = 'smaldrs'
        self.rvp_dict_6[0xaa001077] = 'smalxds'
        self.rvp_dict_6[0x84001077] = 'smar64'
        self.rvp_dict_6[0x08001077] = 'smbb16'
        self.rvp_dict_6[0x18001077] = 'smbt16'
        self.rvp_dict_6[0x28001077] = 'smtt16'
        self.rvp_dict_6[0x58001077] = 'smds'
        self.rvp_dict_6[0x68001077] = 'smdrs'
        self.rvp_dict_6[0x78001077] = 'smxds'
        self.rvp_dict_6[0x40001077] = 'smmul'
        self.rvp_dict_6[0x50001077] = 'smmul.u'
        self.rvp_dict_6[0x44001077] = 'smmwb'
        self.rvp_dict_6[0x54001077] = 'smmwb.u'
        self.rvp_dict_6[0x64001077] = 'smmwt'
        self.rvp_dict_6[0x74001077] = 'smmwt.u'
        self.rvp_dict_6[0xac001077] = 'smslda'
        self.rvp_dict_6[0xbc001077] = 'smslxda'
        self.rvp_dict_6[0x86001077] = 'smsr64'
        self.rvp_dict_6[0x24001077] = 'sra.u'
        self.rvp_dict_6[0xc2001077] = 'sub64'
        self.rvp_dict_6[0xb0001077] = 'ukadd64'
        self.rvp_dict_6[0x14001077] = 'ukaddh'
        self.rvp_dict_6[0x10001077] = 'ukaddw'
        self.rvp_dict_6[0xb4001077] = 'ukmar64'
        self.rvp_dict_6[0xb6001077] = 'ukmsr64'
        self.rvp_dict_6[0xb2001077] = 'uksub64'
        self.rvp_dict_6[0x16001077] = 'uksubh'
        self.rvp_dict_6[0x12001077] = 'uksubw'
        self.rvp_dict_6[0xa4001077] = 'umar64'
        self.rvp_dict_6[0xa6001077] = 'umsr64'
        self.rvp_dict_6[0xa0001077] = 'uradd64'
        self.rvp_dict_6[0x30001077] = 'uraddw'
        self.rvp_dict_6[0xa2001077] = 'ursub64'
        self.rvp_dict_6[0x32001077] = 'ursubw'
        self.rvp_dict_6[0xda001077] = 'kdmbb16'
        self.rvp_dict_6[0xea001077] = 'kdmbt16'
        self.rvp_dict_6[0xfa001077] = 'kdmtt16'
        self.rvp_dict_6[0xd8001077] = 'kdmabb16'
        self.rvp_dict_6[0xe8001077] = 'kdmabt16'
        self.rvp_dict_6[0xf8001077] = 'kdmatt16'
        self.rvp_dict_6[0xdc001077] = 'khmbb16'
        self.rvp_dict_6[0xec001077] = 'khmbt16'
        self.rvp_dict_6[0xfc001077] = 'khmtt16'

        # Create RVP Dictiory 7 for instruction:  kslliw  sraiw.u
        self.rvp_dict_7 = {}
        self.rvp_dict_7[0x36001077] = 'kslliw'
        self.rvp_dict_7[0x34001077] = 'sraiw.u'

        # Create RVP Dictiory 8 for instruction:  srai.u
        self.rvp_dict_8 = {}
        self.rvp_dict_8[0xd4001077] = 'srai.u'

        # Create RVP Dictiory 9 for instruction:  kstas16  kstsa16  rstas16  rstsa16  stas16  stsa16  ukstas16  ukstsa16  urstas16  urstsa16  add32  cras32  crsa32  kadd32  kcras32  kcrsa32  kmabb32  kmabt32  kmatt32  kmaxda32  kmda32  kmxda32  kmads32  kmadrs32  kmaxds32  kmsda32  kmsxda32  ksll32  kslra32  kslra32.u  kstas32  kstsa32  ksub32  pkbb32  pkbt32  pktt32  pktb32  radd32  rcras32  rcrsa32  rstas32  rstsa32  rsub32  sll32  smax32  smbt32  smtt32  smds32  smdrs32  smxds32  smin32  sra32  sra32.u  srl32  srl32.u  stas32  stsa32  sub32  ukadd32  ukcras32  ukcrsa32  ukstas32  ukstsa32  uksub32  umax32  umin32  uradd32  urcras32  urcrsa32  urstas32  urstsa32  ursub32
        self.rvp_dict_9 = {}
        self.rvp_dict_9[0xc4002077] = 'kstas16'
        self.rvp_dict_9[0xc6002077] = 'kstsa16'
        self.rvp_dict_9[0xb4002077] = 'rstas16'
        self.rvp_dict_9[0xb6002077] = 'rstsa16'
        self.rvp_dict_9[0xf4002077] = 'stas16'
        self.rvp_dict_9[0xf6002077] = 'stsa16'
        self.rvp_dict_9[0xe4002077] = 'ukstas16'
        self.rvp_dict_9[0xe6002077] = 'ukstsa16'
        self.rvp_dict_9[0xd4002077] = 'urstas16'
        self.rvp_dict_9[0xd6002077] = 'urstsa16'
        self.rvp_dict_9[0x40002077] = 'add32'
        self.rvp_dict_9[0x44002077] = 'cras32'
        self.rvp_dict_9[0x46002077] = 'crsa32'
        self.rvp_dict_9[0x10002077] = 'kadd32'
        self.rvp_dict_9[0x14002077] = 'kcras32'
        self.rvp_dict_9[0x16002077] = 'kcrsa32'
        self.rvp_dict_9[0x5a002077] = 'kmabb32'
        self.rvp_dict_9[0x6a002077] = 'kmabt32'
        self.rvp_dict_9[0x7a002077] = 'kmatt32'
        self.rvp_dict_9[0x4a002077] = 'kmaxda32'
        self.rvp_dict_9[0x38002077] = 'kmda32'
        self.rvp_dict_9[0x3a002077] = 'kmxda32'
        self.rvp_dict_9[0x5c002077] = 'kmads32'
        self.rvp_dict_9[0x6c002077] = 'kmadrs32'
        self.rvp_dict_9[0x7c002077] = 'kmaxds32'
        self.rvp_dict_9[0x4c002077] = 'kmsda32'
        self.rvp_dict_9[0x4e002077] = 'kmsxda32'
        self.rvp_dict_9[0x64002077] = 'ksll32'
        self.rvp_dict_9[0x56002077] = 'kslra32'
        self.rvp_dict_9[0x66002077] = 'kslra32.u'
        self.rvp_dict_9[0xc0002077] = 'kstas32'
        self.rvp_dict_9[0xc2002077] = 'kstsa32'
        self.rvp_dict_9[0x12002077] = 'ksub32'
        self.rvp_dict_9[0x0e002077] = 'pkbb32'
        self.rvp_dict_9[0x1e002077] = 'pkbt32'
        self.rvp_dict_9[0x2e002077] = 'pktt32'
        self.rvp_dict_9[0x3e002077] = 'pktb32'
        self.rvp_dict_9[0x00002077] = 'radd32'
        self.rvp_dict_9[0x04002077] = 'rcras32'
        self.rvp_dict_9[0x06002077] = 'rcrsa32'
        self.rvp_dict_9[0xb0002077] = 'rstas32'
        self.rvp_dict_9[0xb2002077] = 'rstsa32'
        self.rvp_dict_9[0x02002077] = 'rsub32'
        self.rvp_dict_9[0x54002077] = 'sll32'
        self.rvp_dict_9[0x92002077] = 'smax32'
        self.rvp_dict_9[0x18002077] = 'smbt32'
        self.rvp_dict_9[0x28002077] = 'smtt32'
        self.rvp_dict_9[0x58002077] = 'smds32'
        self.rvp_dict_9[0x68002077] = 'smdrs32'
        self.rvp_dict_9[0x78002077] = 'smxds32'
        self.rvp_dict_9[0x90002077] = 'smin32'
        self.rvp_dict_9[0x50002077] = 'sra32'
        self.rvp_dict_9[0x60002077] = 'sra32.u'
        self.rvp_dict_9[0x52002077] = 'srl32'
        self.rvp_dict_9[0x62002077] = 'srl32.u'
        self.rvp_dict_9[0xf0002077] = 'stas32'
        self.rvp_dict_9[0xf2002077] = 'stsa32'
        self.rvp_dict_9[0x42002077] = 'sub32'
        self.rvp_dict_9[0x30002077] = 'ukadd32'
        self.rvp_dict_9[0x34002077] = 'ukcras32'
        self.rvp_dict_9[0x36002077] = 'ukcrsa32'
        self.rvp_dict_9[0xe0002077] = 'ukstas32'
        self.rvp_dict_9[0xe2002077] = 'ukstsa32'
        self.rvp_dict_9[0x32002077] = 'uksub32'
        self.rvp_dict_9[0xa2002077] = 'umax32'
        self.rvp_dict_9[0xa0002077] = 'umin32'
        self.rvp_dict_9[0x20002077] = 'uradd32'
        self.rvp_dict_9[0x24002077] = 'urcras32'
        self.rvp_dict_9[0x26002077] = 'urcrsa32'
        self.rvp_dict_9[0xd0002077] = 'urstas32'
        self.rvp_dict_9[0xd2002077] = 'urstsa32'
        self.rvp_dict_9[0x22002077] = 'ursub32'

        # Create RVP Dictiory 10 for instruction:  kslli32  slli32  srai32  srai32.u  srli32  srli32.u
        self.rvp_dict_10 = {}
        self.rvp_dict_10[0x84002077] = 'kslli32'
        self.rvp_dict_10[0x74002077] = 'slli32'
        self.rvp_dict_10[0x70002077] = 'srai32'
        self.rvp_dict_10[0x80002077] = 'srai32.u'
        self.rvp_dict_10[0x72002077] = 'srli32'
        self.rvp_dict_10[0x82002077] = 'srli32.u'

        # Create RVP Dictiory 11 for instruction:  bpick
        self.rvp_dict_11 = {}
        self.rvp_dict_11[0x00003077] = 'bpick'

