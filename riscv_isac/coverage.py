
# See LICENSE.incore for details
# See LICENSE.iitm for details

from itertools import islice
from threading import local

import ruamel
from ruamel.yaml import YAML
import riscv_isac.utils as utils
from riscv_isac.constants import *
from riscv_isac.log import logger
from collections import Counter
import sys
from riscv_isac.utils import yaml
from riscv_isac.cgf_normalize import *
import riscv_isac.fp_dataset as fmt
import struct
import pytablewriter
import importlib
import pluggy
import riscv_isac.plugins as plugins
from riscv_isac.plugins.specification import *
import math
from itertools import islice
import multiprocessing as mp
from collections.abc import MutableMapping

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
        'bclri','bexti','binvi','bseti','xperm4','xperm8','zip','unzip','gorci',\
        'fcvt.d.wu','fcvt.s.wu','fcvt.d.lu','fcvt.s.lu']

unsgn_rs2 = ['bgeu', 'bltu', 'sltiu', 'sltu', 'sll', 'srl', 'sra','mulhu',\
        'mulhsu','divu','remu','divuw','remuw','aes64ds','aes64dsm','aes64es',\
        'aes64esm','aes64ks2','sm4ed','sm4ks','ror','rol','rorw','rolw','clmul',\
        'clmulh','clmulr','andn','orn','xnor','pack','packh','packu','packuw','packw',\
        'xperm.n','xperm.b', 'aes32esmi', 'aes32esi', 'aes32dsmi', 'aes32dsi',\
        'sha512sum1r','sha512sum0r','sha512sig1l','sha512sig1h','sha512sig0l','sha512sig0h','fsw',\
        'bclr','bext','binv','bset','minu','maxu','add.uw','sh1add.uw','sh2add.uw','sh3add.uw',\
        'xperm4','xperm8','zip','unzip']

class cross():

    BASE_REG_DICT = { 'x'+str(i) : 'x'+str(i) for i in range(32)}

    def __init__(self,label,coverpoint):

        self.label = label
        self.coverpoint = coverpoint
        self.result = 0

        ## Extract relevant information from coverpt
        self.data = self.coverpoint.split('::')
        self.ops = self.data[0].replace(' ', '')[1:-1].split(':')
        self.assign_lst = self.data[1].replace(' ', '')[1:-1].split(':')
        self.cond_lst = self.data[2].lstrip().rstrip()[1:-1].split(':')

    def process(self, queue, window_size, addr_pairs):
        '''
        Check whether the coverpoint is a hit or not and update the metric
        '''
        if(len(self.ops)>window_size or len(self.ops)>len(queue)):
            return

        for index in range(len(self.ops)):

            instr = queue[index]
            instr_name = instr.instr_name
            if addr_pairs:
                if not (any([instr.instr_addr >= saddr and instr.instr_addr < eaddr for saddr,eaddr in addr_pairs])):
                    break

            rd = None
            rs1 = None
            rs2 = None
            rs3 = None
            imm = None
            zimm = None
            csr = None
            shamt = None
            succ = None
            pred = None
            rl = None
            aq = None
            rm = None

            if instr.rd is not None:
                rd = instr.rd[1] + str(instr.rd[0])
            if instr.rs1 is not None:
                rs1 = instr.rs1[1] + str(instr.rs1[0])
            if instr.rs2 is not None:
                rs2 = instr.rs2[1] + str(instr.rs2[0])
            if instr.rs3 is not None:
                rs3 = instr.rs3[1] + str(instr.rs3[0])
            if instr.imm is not None:
                imm = int(instr.imm)
            if instr.zimm is not None:
                zimm = int(instr.zimm)
            if instr.csr is not None:
                csr = instr.csr
            if instr.shamt is not None:
                shamt = int(instr.shamt)
            if instr.succ is not None:
                succ = int(instr.succ)
            if instr.pred is not None:
                pred = int(instr.pred)
            if instr.rl is not None:
                rl = int(instr.rl)
            if instr.aq is not None:
                aq = int(instr.aq)
            if instr.rm is not None:
                rm = int(instr.rm)

            if self.ops[index].find('?') == -1:
                # Handle instruction tuple
                if self.ops[index].find('(') != -1:
                    check_lst = self.ops[index].replace('(', '').replace(')', '').split(',')
                else:
                    check_lst = [self.ops[index]]
                if (instr_name not in check_lst):
                    break

            if self.cond_lst[index].find('?') == -1:
                if(eval(self.cond_lst[index], locals(), cross.BASE_REG_DICT)):
                    if(index==len(self.ops)-1):
                        self.result = self.result + 1
                else:
                    break

            if self.assign_lst[index].find('?') == -1:
                exec(self.assign_lst[index], locals(), cross.BASE_REG_DICT)

    def get_metric(self):
        return self.result


class csr_registers(MutableMapping):
    '''
    Defines the architectural state of CSR Register file.
    '''

    def __init__ (self, xlen):
        '''
        Class constructor

        :param xlen: max XLEN value of the RISC-V device

        :type xlen: int

        Currently defines the CSR register files the
        width of which is defined by the xlen parameter. These are
        implemented as an array holding the hexadecimal representations of the
        values as string. These can be accessed by both integer addresses as well as string names

        '''

        if(xlen==32):
            self.csr = ['00000000']*4096
            self.csr[int('301',16)] = '40000000' # misa
        else:
            self.csr = ['0000000000000000']*4096
            self.csr[int('301',16)] = '8000000000000000' # misa

        # M-Mode CSRs
        self.csr[int('F11',16)] = '00000000' # mvendorid
        self.csr[int('306',16)] = '00000000' # mcounteren
        self.csr[int('B00',16)] = '0000000000000000' # mcycle
        self.csr[int('B02',16)] = '0000000000000000' # minstret
        for i in range(29): # mphcounter 3-31, 3h-31h
            self.csr[int('B03',16)+i] = '0000000000000000'
            self.csr[int('B83',16)+i] = '00000000'
        self.csr[int('320',16)] = '00000000' # mcounterinhibit
        self.csr[int('B80',16)] = '00000000' # mcycleh
        self.csr[int('B82',16)] = '00000000' # minstreth
        self.csr[int('001',16)] = '00000000'
        self.csr[int('002',16)] = '00000000'
        self.csr[int('003',16)] = '00000000'

        ## mtime, mtimecmp => 64 bits, platform defined memory mapping

        # S-Mode CSRs
        self.csr[int('106',16)] = '00000000' # scounteren

        self.csr_regs={
            "mvendorid":int('F11',16),
            "marchid":int('F12',16),
            "mimpid":int('F13',16),
            "mhartid":int('F14',16),
            "mstatus":int('300',16),
            "misa":int('301',16),
            "medeleg":int('302',16),
            "mideleg":int('303',16),
            "mie":int('304',16),
            "mtvec":int('305',16),
            "mcounteren":int('306',16),
            "mscratch":int('340',16),
            "mepc":int('341',16),
            "mcause":int('342',16),
            "mtval":int('343',16),
            "mip":int('344',16),
            "pmpcfg0":int('3A0',16),
            "pmpcfg1":int('3A1',16),
            "pmpcfg2":int('3A2',16),
            "pmpcfg3":int('3A3',16),
            "mcycle":int('B00',16),
            "minstret":int('B02',16),
            "mcycleh":int('B80',16),
            "minstreth":int('B82',16),
            "mcountinhibit":int('320',16),
            "tselect":int('7A0',16),
            "tdata1":int('7A1',16),
            "tdata2":int('7A2',16),
            "tdata3":int('7A3',16),
            "dcsr":int('7B0',16),
            "dpc":int('7B1',16),
            "dscratch0":int('7B2',16),
            "dscratch1":int('7B3',16),
            "sstatus": int('100',16),
            "sedeleg": int('102',16),
            "sideleg": int('103',16),
            "sie": int('104',16),
            "stvec": int('105',16),
            "scounteren": int('106',16),
            "sscratch": int('140',16),
            "sepc": int('141',16),
            "scause": int('142',16),
            "stval": int('143',16),
            "sip": int('144',16),
            "satp": int('180',16),
            "vxsat": int('009',16),
            "fflags":int('1',16),
            "frm":int('2',16),
            "fcsr":int('3',16)
        }
        for i in range(16):
            self.csr_regs["pmpaddr"+str(i)] = int('3B0',16)+i
        for i in range(3,32):
            self.csr_regs["mhpmcounter"+str(i)] = int('B03',16) + (i-3)
            self.csr_regs["mhpmcounter"+str(i)+"h"] = int('B83',16) + (i-3)
            self.csr_regs["mhpmevent"+str(i)] = int('323',16) + (i-3)

    def __setitem__ (self,key,value):

        if(isinstance(key, str)):
            self.csr[self.csr_regs[key]] = value
        else:
            self.csr[key] = value

    def __iter__(self):
        for entry in self.csr_regs.keys():
            yield (entry,self.csr_regs[entry],self.csr[self.csr_regs[entry]])

    def __len__(self):
        return len(self.csr)

    def __delitem__(self,key):
        pass

    def __getitem__ (self,key):
        if(isinstance(key, str)):
            return self.csr[self.csr_regs[key]]
        else:
            return self.csr[key]

class archState:
    '''
    Defines the architectural state of the RISC-V device.
    '''

    def __init__ (self, xlen, flen):
        '''
        Class constructor

        :param xlen: max XLEN value of the RISC-V device
        :param flen: max FLEN value of the RISC-V device

        :type xlen: int
        :type flen: int

        Currently defines the integer and floating point register files the
        width of which is defined by the xlen and flen parameters. These are
        implemented as an array holding the hexadecimal representations of the
        values as string.

        The program counter is also defined as an int.

        '''

        if xlen == 32:
            self.x_rf = ['00000000']*32
        else:
            self.x_rf = ['0000000000000000']*32

        if flen == 32:
            self.f_rf = ['00000000']*32
        else:
            self.f_rf = ['0000000000000000']*32
        self.pc = 0
        self.flen = flen

class statistics:
    '''
    Class for holding statistics used for Data propagation report
    '''

    def __init__(self, xlen, flen):
        '''
        This class maintains a collection of arrays which are useful in
        calculating the following set of statistics:

        - STAT1 : Number of instructions that hit unique coverpoints and update the signature.
        - STAT2 : Number of instructions that hit covepoints which are not unique but still update the signature
        - STAT3 : Number of instructions that hit a unique coverpoint but do not update signature
        - STAT4 : Number of multiple signature updates for the same coverpoint
        - STAT5 : Number of times the signature was overwritten
        '''

        self.xlen = xlen
        self.flen = flen

        self.stat1 = []
        self.stat2 = []
        self.stat3 = []
        self.stat4 = []
        self.stat5 = []
        self.code_seq = []
        self.ucode_seq = []
        self.covpt = []
        self.ucovpt = []
        self.cov_pt_sig = []
        self.last_meta = []

    def __add__(self, o):
        temp = statistics(self.xlen, self.flen)
        temp.stat1 = self.stat1 + o.stat1
        temp.stat2 = self.stat2 + o.stat2
        temp.stat3 = self.stat3 + o.stat3
        temp.stat4 = self.stat4 + o.stat4
        temp.stat5 = self.stat5 + o.stat5

        temp.code_seq = self.code_seq + o.code_seq
        temp.ucode_seq = self.ucode_seq + o.ucode_seq
        temp.covpt = self.covpt + o.covpt
        temp.ucovpt = self.ucovpt + o.ucovpt
        temp.cov_pt_sig = self.cov_pt_sig + o.cov_pt_sig
        temp.last_meta = self.last_meta + o.last_meta

        return temp

def define_sem(flen, iflen, rsval, postfix,local_dict):
    '''
    This function expands the rsval and defining the respective sign, exponent and mantissa correspondence
    :param flen: Floating point length
    :param rsval: base rs value used to expand it's respective sign, exponent and mantissa
    :postfix: Register number that is part of the instruction
    :local_dict: Holding the copy of all the local variables from the function calling this function
    :return: The dictionary of variables with it's values
    '''
    if iflen == 32:
        e_sz = 8
        m_sz = 23
    else:
        e_sz = 11
        m_sz = 52
    bin_val = ('{:0'+str(flen)+'b}').format(rsval)
    if flen > iflen:
        local_dict['rs'+postfix+'_nan_prefix'] = int(bin_val[0:flen-iflen],2)
        bin_val = bin_val[flen-iflen:]
    local_dict['fs'+postfix] = int(bin_val[0],2)
    local_dict['fe'+postfix] = int(bin_val[1:e_sz+1],2)
    local_dict['fm'+postfix] = int(bin_val[e_sz+1:],2)

def pretty_print_yaml(yaml):
    res = ''''''
    for line in ruamel.yaml.round_trip_dump(yaml, indent=5, block_seq_indent=3).splitlines(True):
        res += line
    return res

def pretty_print_regfile(regfile):
    res = ""
    for index in range(0, 32, 4):
        print('x'+str(index) +   ' : ' + regfile[index] + '\t' +\
              'x'+str(index+1) + ' : ' + regfile[index+1] + '\t' + \
              'x'+str(index+2) + ' : ' + regfile[index+2] + '\t' + \
              'x'+str(index+3) + ' : ' + regfile[index+3] + '\t' )
    print('\n\n')

def gen_report(cgf, detailed):
    '''
    Function to convert a CGF to a string report. A detailed report includes the individual coverpoints and the corresponding values of the same

    :param cgf: an input CGF dictionary
    :param detailed: boolean value indicating a detailed report must be generated.

    :type cgf: dict
    :type detailed: bool

    :return: string holding the final report
    '''
    temp = cgf.copy()
    for cov_labels, value in cgf.items():
        if cov_labels != 'datasets':
            total_uncovered = 0
            total_categories = 0
            for categories in value:
                if categories not in ['cond','config','ignore', 'base_op', 'p_op_cond']:
                    for coverpoints, coverage in value[categories].items():
                        if coverage == 0:
                            total_uncovered += 1
                    total_categories += len(value[categories])
            for categories in value:
                if categories not in ['cond','config','ignore', 'base_op', 'p_op_cond']:
                    uncovered = 0
                    for coverpoints, coverage in value[categories].items():
                        if coverage == 0:
                            uncovered += 1
                    percentage_covered = str((len(value[categories]) - uncovered)/len(value[categories]))
                    node_level_str =  '  ' + categories + ':\n'
                    node_level_str += '    coverage: ' + \
                            str(len(value[categories]) - uncovered) + \
                            '/' + str(len(value[categories]))
                    temp[cov_labels][categories]['coverage'] = '{0}/{1}'.format(\
                        str(len(value[categories]) - uncovered),\
                        str(len(value[categories])))
            temp[cov_labels]['total_coverage'] = '{0}/{1}'.format(\
                    str(total_categories-total_uncovered),\
                    str(total_categories))
    return dict(temp)

def merge_files(files,i,k):
    '''
    Merges files from i to n where n is len(files) or i+k

    Arguments:

    files: List of dictionaries to be merged
    i : beginning index to merge files on a given core
    k : number of files to be merged

    '''

    temp = files[i]
    n = min(len(files),i+k)
    for logs_cov in files[i+1:n]:
        for cov_labels, value in logs_cov.items():
            if cov_labels not in temp:
                temp[cov_labels] = value
                continue
            for categories in value:
                if categories not in ['cond','config','ignore','total_coverage','coverage']:
                    if categories not in temp[cov_labels]:
                        temp[cov_labels][categories] = value[categories]
                        continue
                    for coverpoints, coverage in value[categories].items():
                        if coverpoints not in temp[cov_labels][categories]:
                            temp[cov_labels][categories][coverpoints] = coverage
                        else:
                            temp[cov_labels][categories][coverpoints] += coverage
    return temp

def merge_fn(files, cgf, p):

    '''
    Each core is assigned ceil(n/k) processes where n is len(files)
    '''


    pool_work = mp.Pool(processes = p)
    while(len(files)>1):
        n = len(files)
        max_process = math.ceil(n/p)
        if(max_process==1):
            max_process = 2
        files = pool_work.starmap_async(merge_files,[(files,i,max_process) for i in range(0,n,max_process)])
        files = files.get()
    pool_work.close()
    pool_work.join()

    return files[0]


def merge_coverage(inp_files, cgf, detailed, p=1):
    '''
    This function merges values of multiple CGF files and return a single cgf
    file. This can be treated analogous to how coverage files are merged
    traditionally.

    :param inp_files: an array of input CGF file names which need to be merged.
    :param cgf: a cgf against which coverpoints need to be checked for.
    :param detailed: a boolean value indicating if a detailed report needs to be generated
    :param p: Number of worker processes (>=1)

    :type inp_files: [str]
    :type cgf: dict
    :type detailed: bool
    :type p: int

    :return: a string contain the final report of the merge.
    '''
    files = []
    for logs in inp_files:
        files.append(utils.load_yaml_file(logs))

    temp = merge_fn(files,cgf,p)
    for cov_labels, value in temp.items():
        for categories in value:
            if categories not in ['cond','config','ignore','total_coverage','coverage', 'base_op', 'p_op_cond']:
                for coverpoints, coverage in value[categories].items():
                    if coverpoints in cgf[cov_labels][categories]:
                        cgf[cov_labels][categories][coverpoints] += coverage

    return gen_report(cgf, detailed)

def twos_complement(val,bits):
    if (val & (1 << (bits - 1))) != 0:
        val = val - (1 << bits)
    return val

def simd_val_unpack(val_comb, op_width, op_name, val, local_dict):
    '''
    This function unpacks `val` into its simd elements.

    :param val_comb: val_comb from the cgf dictionary
    :param op_name: name of the operand (rs1/rs2)
    :param val: operand value
    :param local_dict: locals() of the calling context

    '''
    simd_size = op_width
    simd_sgn = False
    for coverpoints in val_comb:
        if f"{op_name}_b0_val" in coverpoints:
            simd_size = 8
        if f"{op_name}_h0_val" in coverpoints:
            simd_size = 16
        if f"{op_name}_w0_val" in coverpoints:
            simd_size = 32
        if op_name in coverpoints:
            if any([s in coverpoints for s in ["<", "== -", "== (-"]]):
                simd_sgn = True

    fmt = {8: 'b', 16: 'h', 32: 'w', 64: 'd'}
    sz = fmt[simd_size]

    if simd_size > op_width:
        return

    elm_urange = 1<<simd_size
    elm_mask = elm_urange-1
    elm_msb_mask = (1<<(simd_size-1))
    for i in range(op_width//simd_size):
        elm_val = (val >> (i*simd_size)) & elm_mask
        if simd_sgn and (elm_val & elm_msb_mask) != 0:
            elm_val = elm_val - elm_urange
        local_dict[f"{op_name}_{sz}{i}_val"]=elm_val
    if simd_size == op_width:
        local_dict[f"{op_name}_val"]=elm_val

def compute_per_line(queue, event, cgf_queue, stats_queue, cgf, xlen, flen, addr_pairs, sig_addrs, stats, arch_state, csr_regfile, result_count, no_count):
    '''
    This function checks if the current instruction under scrutiny matches a
    particular coverpoint of interest. If so, it updates the coverpoints and
    returns the same.

    :param queue: A queue thread to push instructionObject
    :param event: Event object to signal completion of decoding
    :param cgf_queue: A queue thread to push updated cgf
    :param stats_queue: A queue thread to push updated `stats` object

    :param cgf: a cgf against which coverpoints need to be checked for.
    :param xlen: Max xlen of the trace
    :param flen: Max flen of the trace
    :param addr_pairs: pairs of start and end addresses for which the coverage needs to be updated
    :param sig_addrs: pairs of start and end addresses for which signature update needs to be checked
    :param stats: `stats` object
    :param csr_regfile: Architectural state of CSR register file
    :param result_count:

    :type queue: class`multiprocessing.Queue`
    :type event: class`multiprocessing.Event`
    :type cgf_queue: class`multiprocessing.Queue`
    :type stats_queue: class`multiprocessing.Queue`
    :type instr: :class:`instructionObject`
    :type cgf: dict
    :type xlen: int
    :type flen: int
    :type addr_pairs: (int, int)
    :type sig_addrs: (int, int)
    :type stats: class `statistics`
    :type csr_regfile: class `csr_registers`
    :type result_count: int
    '''

    # List to hold hit coverpoints
    hit_covpts = []
    rcgf = copy.deepcopy(cgf)

    # Enter the loop only when Event is not set or when the
    # instruction object queue is not empty
    while (event.is_set() == False) or (queue.empty() == False):

        # If there are instructions in queue, compute coverage
        if queue.empty() is False:

            instr = queue.get_nowait()

            mnemonic = instr.mnemonic
            commitvalue = instr.reg_commit

            # assign default values to operands
            nxf_rs1 = 0
            nxf_rs2 = 0
            nxf_rs3 = 0
            nxf_rd  = 0
            rs1_type = 'x'
            rs2_type = 'x'
            rs3_type = 'x'
            rd_type  = 'x'

            csr_addr = None

            # create signed/unsigned conversion params
            if xlen == 32:
                unsgn_sz = '>I'
                sgn_sz = '>i'
            else:
                unsgn_sz = '>Q'
                sgn_sz = '>q'

            iflen = flen

            if instr.instr_name.endswith(".s") or 'fmv.x.w' in instr.instr_name:
                iflen = 32
            elif instr.instr_name.endswith(".d"):
                iflen = 64

            fsgn_sz = '>Q' if flen==64 else '>I'

            # if instruction is empty then return
            if instr is None:
                return cgf

            # check if instruction lies within the valid region of interest
            if addr_pairs:
                if any([instr.instr_addr >= saddr and instr.instr_addr < eaddr for saddr,eaddr in addr_pairs]):
                    enable = True
                else:
                    enable = False
            else:
                enable=True

            # capture the operands and their values from the regfile
            if instr.rs1 is not None:
                rs1_type = instr.rs1[1]
                rs1 = rs1_type + str(instr.rs1[0])
                nxf_rs1 = instr.rs1[0]
                exec(f'{rs1} = rs1')
            if instr.rs2 is not None:
                rs2_type = instr.rs2[1]
                rs2 = rs2_type + str(instr.rs2[0])
                nxf_rs2 = instr.rs2[0]
                exec(f'{rs2} = rs2')
            if instr.rs3 is not None:
                rs3_type = instr.rs3[1]
                rs3 = rs3_type + str(instr.rs3[0])
                nxf_rs3 = instr.rs3[0]
                exec(f'{rs3} = rs3')
            if instr.rd is not None:
                is_rd_valid = True
                rd_type = instr.rd[1]
                rd = rd_type + str(instr.rd[0])
                nxf_rd = instr.rd[0]
                exec(f'{rd} = rd')
            else:
                is_rd_valid = False
            if instr.imm is not None:
                imm_val = instr.imm
            if instr.shamt is not None:
                imm_val = instr.shamt



            instr_vars = {}

            # special value conversion based on signed/unsigned operations
            rs1_val = None
            if instr.instr_name in unsgn_rs1:
                rs1_val = struct.unpack(unsgn_sz, bytes.fromhex(arch_state.x_rf[nxf_rs1]))[0]
            elif instr.is_rvp:
                rs1_val = struct.unpack(unsgn_sz, bytes.fromhex(arch_state.x_rf[nxf_rs1]))[0]
                if instr.rs1_nregs == 2:
                    rs1_hi_val = struct.unpack(unsgn_sz, bytes.fromhex(arch_state.x_rf[nxf_rs1+1]))[0]
                    rs1_val = (rs1_hi_val << 32) | rs1_val
            elif rs1_type == 'x':
                rs1_val = struct.unpack(sgn_sz, bytes.fromhex(arch_state.x_rf[nxf_rs1]))[0]
            elif rs1_type == 'f':
                rs1_val = struct.unpack(fsgn_sz, bytes.fromhex(arch_state.f_rf[nxf_rs1]))[0]
                define_sem(flen,iflen,rs1_val,"1",instr_vars)

            rs2_val = None
            if instr.instr_name in unsgn_rs2:
                rs2_val = struct.unpack(unsgn_sz, bytes.fromhex(arch_state.x_rf[nxf_rs2]))[0]
            elif instr.is_rvp:
                rs2_val = struct.unpack(unsgn_sz, bytes.fromhex(arch_state.x_rf[nxf_rs2]))[0]
                if instr.rs2_nregs == 2:
                    rs2_hi_val = struct.unpack(unsgn_sz, bytes.fromhex(arch_state.x_rf[nxf_rs2+1]))[0]
                    rs2_val = (rs2_hi_val << 32) | rs2_val
            elif rs2_type == 'x':
                rs2_val = struct.unpack(sgn_sz, bytes.fromhex(arch_state.x_rf[nxf_rs2]))[0]
            elif rs2_type == 'f':
                rs2_val = struct.unpack(fsgn_sz, bytes.fromhex(arch_state.f_rf[nxf_rs2]))[0]
                define_sem(flen,iflen,rs2_val,"2",instr_vars)

            rs3_val = None
            if rs3_type == 'f':
                rs3_val = struct.unpack(fsgn_sz, bytes.fromhex(arch_state.f_rf[nxf_rs3]))[0]
                define_sem(flen,iflen,rs3_val,"3",instr_vars)

            sig_update = False
            if instr.instr_name in ['sh','sb','sw','sd','c.sw','c.sd','c.swsp','c.sdsp'] and sig_addrs:
                store_address = rs1_val + imm_val
                for start, end in sig_addrs:
                    if store_address >= start and store_address <= end:
                        sig_update = True
                        break

            if sig_update: # writing result operands of last non-store instruction to the signature region
                result_count = result_count - 1
            else:
                result_count = instr.rd_nregs

            instr_vars["rm_val"] = instr.rm
            instr_vars['fcsr'] = int(csr_regfile['fcsr'],16)

            arch_state.pc = instr.instr_addr

            ea_align = None
            # the ea_align variable is used by the eval statements of the
            # coverpoints for conditional ops and memory ops
            if instr.instr_name in ['jal','bge','bgeu','blt','bltu','beq','bne']:
                ea_align = (instr.instr_addr+(imm_val<<1)) % 4

            if instr.instr_name == "jalr":
                ea_align = (rs1_val + imm_val) % 4

            if instr.instr_name in ['sw','sh','sb','lw','lhu','lh','lb','lbu','lwu','flw','fsw']:
                ea_align = (rs1_val + imm_val) % 4
            if instr.instr_name in ['ld','sd','fld','fsd']:
                ea_align = (rs1_val + imm_val) % 8

            if rs1_val is not None:
                instr_vars['rs1_val'] = rs1_val
            if rs2_val is not None:
                instr_vars['rs2_val'] = rs2_val
            if rs3_val is not None:
                instr_vars['rs3_val'] = rs3_val
            if imm_val is not None:
                instr_vars['imm_val'] = imm_val
            if ea_align is not None:
                instr_vars['ea_align'] = ea_align
            instr_vars['xlen'] = xlen
            instr_vars['flen'] = flen
            instr_vars['iflen'] = iflen

            local_dict = {}
            for i in csr_regfile.csr_regs:
                local_dict[i] = int(csr_regfile[i],16)

            local_dict['xlen'] = xlen
            local_dict['flen'] = flen

            if enable :
                for cov_labels,value in cgf.items():
                    if cov_labels != 'datasets':
                        if 'mnemonics' in value:

                            req_node = 'mnemonics'
                            is_found = False

                            # Check if there is a base opcode
                            if 'base_op' in value:
                                # If base-op is the current instruction name, check for the p_op_cond node
                                # If conditions satisfy, the instruction is equivalent to the mnemonic
                                if instr.instr_name == value['base_op']:

                                    conds = value['p_op_cond']
                                    # Construct and evaluate conditions
                                    is_found = True
                                    if not eval(conds):
                                        is_found = False

                                    mnemonic = list(value[req_node].keys())
                                    mnemonic = mnemonic[0]

                                    # Update hit statistics of the mnemonic
                                    if is_found:
                                        if value[req_node][mnemonic] == 0:
                                            stats.ucovpt.append('mnemonic : ' + mnemonic)
                                        stats.covpt.append('mnemonic : ' + mnemonic)
                                        value[req_node][mnemonic] += 1
                                        rcgf[cov_labels][req_node][mnemonic] += 1

                            if instr.instr_name in value[req_node] or is_found:
                                if stats.code_seq:
                                    #logger.error('Found a coverpoint without sign Upd ' + str(stats.code_seq))
                                    stats.stat3.append('\n'.join(stats.code_seq))
                                    stats.code_seq = []
                                    stats.covpt = []
                                    stats.ucovpt = []
                                    stats.ucode_seq = []

                                # If mnemonic not detected via base-op
                                if not is_found:
                                    if value[req_node][instr.instr_name] == 0:
                                        stats.ucovpt.append('mnemonic : ' + instr.instr_name)
                                    stats.covpt.append('mnemonic : ' + instr.instr_name)
                                    value[req_node][instr.instr_name] += 1
                                    rcgf[cov_labels][req_node][instr.instr_name] += 1

                                if 'rs1' in value and rs1 in value['rs1']:
                                    if value['rs1'][rs1] == 0:
                                        stats.ucovpt.append('rs1 : ' + rs1)
                                        if no_count:
                                            hit_covpts.append((cov_labels, 'rs1', rs1))
                                    stats.covpt.append('rs1 : ' + rs1)
                                    value['rs1'][rs1] += 1

                                if 'rs2' in value and rs2 in value['rs2']:
                                    if value['rs2'][rs2] == 0:
                                        stats.ucovpt.append('rs2 : ' + rs2)
                                        if no_count:
                                            hit_covpts.append((cov_labels, 'rs2', rs2))
                                    stats.covpt.append('rs2 : ' + rs2)
                                    value['rs2'][rs2] += 1

                                if 'rd' in value and is_rd_valid and rd in value['rd']:
                                    if value['rd'][rd] == 0:
                                        stats.ucovpt.append('rd : ' + rd)
                                        if no_count:
                                            hit_covpts.append((cov_labels, 'rd', rd))
                                    stats.covpt.append('rd : ' + rd)
                                    value['rd'][rd] += 1

                                if 'rs3' in value and rs3 in value['rs3']:
                                    if value['rs3'][rs3] == 0:
                                        stats.ucovpt.append('rs3 : ' + rs3)
                                        if no_count:
                                            hit_covpts.append((cov_labels, 'rs3', rs3))
                                    stats.covpt.append('rs3 : ' + rs3)
                                    value['rs3'][rs3] += 1

                                if 'op_comb' in value and len(value['op_comb']) != 0 :
                                    for coverpoints in value['op_comb']:
                                        if eval(coverpoints):
                                            if cgf[cov_labels]['op_comb'][coverpoints] == 0:
                                                stats.ucovpt.append(str(coverpoints))
                                                if no_count:
                                                    hit_covpts.append((cov_labels, 'op_comb', coverpoints))
                                            stats.covpt.append(str(coverpoints))
                                            cgf[cov_labels]['op_comb'][coverpoints] += 1

                                if 'val_comb' in value and len(value['val_comb']) != 0:
                                    lcls={}
                                    if instr.is_rvp and "rs1" in value:
                                        op_width = 64 if instr.rs1_nregs == 2 else xlen
                                        simd_val_unpack(value['val_comb'], op_width, "rs1", rs1_val, lcls)
                                    if instr.is_rvp and "rs2" in value:
                                        op_width = 64 if instr.rs2_nregs == 2 else xlen
                                        simd_val_unpack(value['val_comb'], op_width, "rs2", rs2_val, lcls)
                                    instr_vars.update(lcls)
                                    for coverpoints in value['val_comb']:
                                        if eval(coverpoints, globals(), instr_vars):
                                            if cgf[cov_labels]['val_comb'][coverpoints] == 0:
                                                stats.ucovpt.append(str(coverpoints))
                                                if no_count:
                                                    hit_covpts.append((cov_labels, 'val_comb', coverpoints))
                                            stats.covpt.append(str(coverpoints))
                                            cgf[cov_labels]['val_comb'][coverpoints] += 1
                                if 'abstract_comb' in value \
                                        and len(value['abstract_comb']) != 0 :
                                    for coverpoints in value['abstract_comb']:
                                        if eval(coverpoints):
                                            if cgf[cov_labels]['abstract_comb'][coverpoints] == 0:
                                                stats.ucovpt.append(str(coverpoints))
                                                if no_count:
                                                        hit_covpts.append((cov_labels, 'abstract_comb', coverpoints))
                                            stats.covpt.append(str(coverpoints))
                                            cgf[cov_labels]['abstract_comb'][coverpoints] += 1

                                if 'csr_comb' in value and len(value['csr_comb']) != 0:
                                    for coverpoints in value['csr_comb']:
                                        if eval(coverpoints, {"__builtins__":None}, local_dict):
                                            if cgf[cov_labels]['csr_comb'][coverpoints] == 0:
                                                stats.ucovpt.append(str(coverpoints))
                                                if no_count:
                                                        hit_covpts.append((cov_labels, 'csr_comb', coverpoints))
                                            stats.covpt.append(str(coverpoints))
                                            cgf[cov_labels]['csr_comb'][coverpoints] += 1

                        elif 'opcode' not in value:
                            if 'csr_comb' in value and len(value['csr_comb']) != 0:
                                for coverpoints in value['csr_comb']:
                                    if eval(coverpoints, {"__builtins__":None}, local_dict):
                                        if cgf[cov_labels]['csr_comb'][coverpoints] == 0:
                                            stats.ucovpt.append(str(coverpoints))
                                            if no_count:
                                                        hit_covpts.append((cov_labels, 'csr_comb', coverpoints))
                                        stats.covpt.append(str(coverpoints))
                                        cgf[cov_labels]['csr_comb'][coverpoints] += 1
                if stats.covpt:
                    if mnemonic is not None :
                        stats.code_seq.append('[' + str(hex(instr.instr_addr)) + ']:' + mnemonic)
                    else:
                        stats.code_seq.append('[' + str(hex(instr.instr_addr)) + ']:' + instr.instr_name)
                if stats.ucovpt:
                    if mnemonic is not None :
                        stats.ucode_seq.append('[' + str(hex(instr.instr_addr)) + ']:' + mnemonic)
                    else:
                        stats.ucode_seq.append('[' + str(hex(instr.instr_addr)) + ']:' + instr.instr_name)

            if instr.instr_name in ['sh','sb','sw','sd','c.sw','c.sd','c.swsp','c.sdsp'] and sig_addrs:
                store_address = rs1_val + imm_val
                store_val = '0x'+arch_state.x_rf[nxf_rs2]
                for start, end in sig_addrs:
                    if store_address >= start and store_address <= end:
                        logger.debug('Signature update : ' + str(hex(store_address)))
                        stats.stat5.append((store_address, store_val, stats.ucovpt, stats.code_seq))
                        stats.cov_pt_sig += stats.covpt
                        if result_count <= 0:
                            if stats.ucovpt:
                                stats.stat1.append((store_address, store_val, stats.ucovpt, stats.ucode_seq))
                                stats.last_meta = [store_address, store_val, stats.ucovpt, stats.ucode_seq]
                                stats.ucovpt = []
                            elif stats.covpt:
                                _log = 'Op without unique coverpoint updates Signature\n'
                                _log += ' -- Code Sequence:\n'
                                for op in stats.code_seq:
                                    _log += '      ' + op + '\n'
                                _log += ' -- Signature Address: {0} Data: {1}\n'.format(
                                        str(hex(store_address)), store_val)
                                _log += ' -- Redundant Coverpoints hit by the op\n'
                                for c in stats.covpt:
                                    _log += '      - ' + str(c) + '\n'
                                logger.warn(_log)
                                stats.stat2.append(_log + '\n\n')
                                stats.last_meta = [store_address, store_val, stats.covpt, stats.code_seq]
                            else:
                                if len(stats.last_meta):
                                    _log = 'Last Coverpoint : ' + str(stats.last_meta[2]) + '\n'
                                    _log += 'Last Code Sequence : \n\t-' + '\n\t-'.join(stats.last_meta[3]) + '\n'
                                    _log +='Current Store : [{0}] : {1} -- Store: [{2}]:{3}\n'.format(\
                                        str(hex(instr.instr_addr)), mnemonic,
                                        str(hex(store_address)),
                                        store_val)
                                    logger.error(_log)
                                    stats.stat4.append(_log + '\n\n')
                            stats.covpt = []
                            stats.code_seq = []
                            stats.ucode_seq = []

            if commitvalue is not None:
                if rd_type == 'x':
                    arch_state.x_rf[int(commitvalue[1])] =  str(commitvalue[2][2:])
                elif rd_type == 'f':
                    arch_state.f_rf[int(commitvalue[1])] =  str(commitvalue[2][2:])

            csr_commit = instr.csr_commit
            if csr_commit is not None:
                for commits in csr_commit:
                    if(commits[0]=="CSR"):
                        csr_regfile[commits[1]] = str(commits[2][2:])

            # Remove hit coverpoints if no_count is set
            if no_count:
                for covpt in hit_covpts:
                    rcgf[covpt[0]][covpt[1]][covpt[2]] = 1
                    del cgf[covpt[0]][covpt[1]][covpt[2]]
                else:
                    hit_covpts = []
    else:
        # if no_count option is set, return rcgf
        # else return cgf
        if not no_count:
            cgf_queue.put_nowait(cgf)
        else:
            cgf_queue.put_nowait(rcgf)

        # Pass statistics back to main process
        stats_queue.put_nowait(stats)
        cgf_queue.close()
        stats_queue.close()

def compute(trace_file, test_name, cgf, parser_name, decoder_name, detailed, xlen, flen, addr_pairs
        , dump, cov_labels, sig_addrs, window_size, no_count=False, procs=1):
    '''Compute the Coverage'''

    global arch_state
    global csr_regfile
    global stats
    global cross_cover_queue
    global result_count

    temp = cgf.copy()
    if cov_labels:
        for groups in cgf:
            if groups not in cov_labels:
                del temp[groups]
        cgf = temp

    # If cgf does not have the covergroup pertaining to the cover-label, throw error
    # and exit
    if not cgf:
        logger.err('Covergroup(s) for ' + str(cov_labels) + ' not found')
        sys.exit(1)

    if dump is not None:
        dump_f = open(dump, 'w')
        dump_f.write(ruamel.yaml.round_trip_dump(cgf, indent=5, block_seq_indent=3))
        dump_f.close()
        sys.exit(0)

    arch_state = archState(xlen,flen)
    csr_regfile = csr_registers(xlen)
    stats = statistics(xlen, flen)
    cross_cover_queue = []
    result_count = 0

    ## Get coverpoints from cgf
    obj_dict = {} ## (label,coverpoint): object
    for cov_labels,value in cgf.items():
        if cov_labels != 'datasets':
            if 'cross_comb' in value and len(value['cross_comb'])!=0:
                for coverpt in value['cross_comb'].keys():
                    if(isinstance(coverpt,str)):
                        new_obj = cross(cov_labels,coverpt)
                        obj_dict[(cov_labels,coverpt)] = new_obj


    parser_pm = pluggy.PluginManager("parser")
    parser_pm.add_hookspecs(ParserSpec)
    try:
        parserfile = importlib.import_module(parser_name)
    except ImportError as e:
        logger.error('Error while importing Parser!')
        logger.error(e)
        raise SystemExit
    parserclass = getattr(parserfile, parser_name)
    parser_pm.register(parserclass())
    parser = parser_pm.hook
    parser.setup(trace=trace_file,arch="rv"+str(xlen))

    decoder_pm = pluggy.PluginManager("decoder")
    decoder_pm.add_hookspecs(DecoderSpec)
    try:
        instructionObjectfile = importlib.import_module(decoder_name)
    except ImportError as e:
        logger.error('Error while importing Decoder!')
        logger.error(e)
        raise SystemExit
    decoderclass = getattr(instructionObjectfile, "disassembler")
    decoder_pm.register(decoderclass())
    decoder = decoder_pm.hook
    decoder.setup(arch="rv"+str(xlen))

    iterator = iter(parser.__iter__()[0])

    # If number of processes to be spawned is more than that available,
    # allot number of processes to be equal to one less than maximum
    available_cores = mp.cpu_count()
    if procs > available_cores:
        procs = available_cores - 1

    # Partiton cgf to chunks
    chunk_len = math.ceil(len(cgf) / procs)
    chunks = [{k:cgf[k] for k in islice(iter(cgf), chunk_len)} for i in range(0, len(cgf), chunk_len)]

    queue_list = []                     # List of queues to pass instructions to daughter processes
    process_list = []                   # List of processes to be spawned
    event_list = []                     # List of Event objects to signal exhaustion of instruction list to daughter processes
    cgf_queue_list = []                 # List of queues to retrieve the updated CGF dictionary from each processes
    stats_queue_list = []               # List of queues to retrieve coverpoint hit statistics from each processes

    # For each chunk of cgf dictionary, spawn a new queue thread to pass instrObj,
    # to retrieve updated cgf, to retrieve statistics. An Event object is appended for
    # each processes spawned. A Process object is appended against every cgf chunk and initialized.
    for i in range(len(chunks)):
        queue_list.append(mp.Queue())
        cgf_queue_list.append(mp.Queue())
        stats_queue_list.append(mp.Queue())
        event_list.append(mp.Event())
        process_list.append(
                        mp.Process(target=compute_per_line,
                                args=(queue_list[i], event_list[i], cgf_queue_list[i], stats_queue_list[i],
                                    chunks[i], xlen, flen, addr_pairs, sig_addrs,
                                    stats,
                                    arch_state,
                                    csr_regfile,
                                    result_count,
                                    no_count
                                    )
                            )
                        )

    #Start each processes
    for each in process_list:
        each.start()

    # This loop facilitates parsing, disassembly and generation of instruction objects
    for instrObj_temp in iterator:
        instr = instrObj_temp.instr
        if instr is None:
            continue
        instrObj = (decoder.decode(instrObj_temp = instrObj_temp))[0]

        # Pass instrObjs to queues pertaining to each processes
        for each in queue_list:
            each.put_nowait(instrObj)

        logger.debug(instrObj)
        cross_cover_queue.append(instrObj)
        if(len(cross_cover_queue)>=window_size):
            for (label,coverpt) in obj_dict.keys():
                obj_dict[(label,coverpt)].process(cross_cover_queue, window_size,addr_pairs)
            cross_cover_queue.pop(0)



    # Close all instruction queues
    for each in queue_list:
        each.close()
        each.join_thread()

    # Signal each processes that instruction list is over
    for each in event_list:
        each.set()

    # Get the renewed cgfs
    cgf_list = []
    for each in cgf_queue_list:
        cgf_list.append(each.get())
        each.close()
        each.join_thread()

    # Get each stats
    stats_list = []
    for each in stats_queue_list:
        stats_list.append(each.get())
        each.close()
        each.join_thread()

    # Join all processes
    for each in process_list:
        each.join()

    # Merge stats
    for each in stats_list:
        stats = stats + each

    # Merge cgfs
    rcgf = dict()
    for d in cgf_list:
        for key, val in d.items():
            rcgf[key] = val

    ## Check for cross coverage for end instructions
    ## All metric is stored in objects of obj_dict
    while(len(cross_cover_queue)>1):
        for label,coverpt in obj_dict.keys():
            obj_dict[(label,coverpt)].process(cross_cover_queue, window_size,addr_pairs)
        cross_cover_queue.pop(0)

    for label,coverpt in obj_dict.keys():
        metric = obj_dict[(label,coverpt)].get_metric()
        if(metric!=0):
            rcgf[label]['cross_comb'][coverpt] = metric

    rpt_str = gen_report(rcgf, detailed)
    logger.info('Writing out updated cgf : ' + test_name + '.cgf')
    dump_file = open(test_name+'.cgf', 'w')
    dump_file.write(ruamel.yaml.round_trip_dump(rcgf, indent=5, block_seq_indent=3))
    dump_file.close()

    if sig_addrs:
        logger.info('Creating Data Propagation Report : ' + test_name + '.md')
        writer = pytablewriter.MarkdownTableWriter()
        writer.headers = ["s.no","signature", "coverpoints", "code"]
        for cov_labels, value in cgf.items():
            if cov_labels != 'datasets':
              #  rpt_str += cov_labels + ':\n'
                total_uncovered = 0
                total_categories = 0
                for categories in value:
                    if categories not in ['cond','config','ignore', 'total_coverage', 'coverage', 'base_op', 'p_op_cond']:
                        for coverpoints, coverage in value[categories].items():
                            if coverage == 0:
                                total_uncovered += 1
                        total_categories += len(value[categories])

        addr_pairs_hex = []
        for x in addr_pairs:
            _x = (hex(x[0]), hex(x[1]))
            addr_pairs_hex.append(_x)
        sig_addrs_hex = []
        for x in sig_addrs:
            if xlen == 64:
                _x = (hex(x[0]), hex(x[1]), str(int((x[1]-x[0])/8)) + ' dwords')
            else:
                _x = (hex(x[0]), hex(x[1]), str(int((x[1]-x[0])/4)) + ' words')
            sig_addrs_hex.append(_x)

        cov_set = set()
        count = 1
        stat5_log = []
        for addr,val,cover,code in stats.stat1:
            sig = ('[{0}]<br>{1}'.format(str(hex(addr)), str(val)))
            cov = ''
            for c in cover:
                cov += '- ' + str(c) + '<br>\n'
                cov_set.add(c)
            cod = ''
            for i in code:
                cod += str(i) + '<br>\n'

            row = [count, sig, cov, cod]
            writer.value_matrix.append(row)
            count += 1
        f =open(test_name+'.md','w')
        if xlen == 64:
            sig_count = 2*len(stats.stat5)
        else:
            sig_count = len(stats.stat5)

        stat2_log = ''
        for _l in stats.stat2:
            stat2_log += _l + '\n\n'

        stat4_log = ''
        for _l in stats.stat4:
            stat4_log += _l + '\n\n'

        stat3_log = ''
        for _l in stats.stat3:
            stat3_log += _l + '\n\n'

        stat5_log = ''
        sig_set = set()
        overwrites = 0
        for addr, val, cover, code in stats.stat5:
            if addr in sig_set:
                stat5_log += ('[{0}]<br>{1}'.format(str(hex(addr)), str(val)))
                stat5_log += code + '\n\n'
                overwrites += 1
                sig_set.add(addr)
                logger.error('Found overwrite in Signature at Addr : ' +
                        str(addr))

        f.write(dpr_template.format(str(xlen),
            str(addr_pairs_hex),
            str(sig_addrs_hex),
            str(cov_labels),
            test_name,
            total_categories,
            len(stats.stat5),
            len(set(stats.cov_pt_sig)),
            len(stats.stat1),
            len(stats.stat2),
            len(stats.stat3),
            len(stats.stat4),
            len(stat5_log),
            stat2_log,
            stat3_log,
            stat4_log,
            stat5_log))
        f.write(writer.dumps())
        f.close()

    return rpt_str

