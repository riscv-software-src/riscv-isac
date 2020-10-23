# See LICENSE.incore for details

import ruamel
from ruamel.yaml import YAML
import riscv_isac.parsers as helpers
import riscv_isac.utils as utils
from riscv_isac.log import logger
from collections import Counter
import sys
yaml = YAML(typ="safe")
yaml.default_flow_style = True
yaml.explicit_start = True
yaml.allow_unicode = True
yaml.allow_duplicate_keys = False
from riscv_isac.cgf_normalize import *
import struct

'''Histogram post-processing module'''

help_message = '{:<20s} {:<10s}'.format('coverage', 'Compliance Coverage')

regfile = ['00000000']*32

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
    rpt_str = ''
    for cov_labels, value in cgf.items():
        if cov_labels != 'datasets':
            rpt_str += cov_labels + ':\n'
            total_uncovered = 0
            total_categories = 0
            for categories in value:
                if categories not in ['cond','config','ignore']:
                    for coverpoints, coverage in value[categories].items():
                        if coverage == 0:
                            total_uncovered += 1
                    total_categories += len(value[categories])
            rpt_str += '  coverage: '+str(total_categories -total_uncovered) + \
                    '/' + str(total_categories)+'\n'
            for categories in value:
                if categories not in ['cond','config','ignore']:
                    uncovered = 0
                    for coverpoints, coverage in value[categories].items():
                        if coverage == 0:
                            uncovered += 1
                    percentage_covered = str((len(value[categories]) - uncovered)/len(value[categories]))
                    node_level_str =  '  ' + categories + ':\n'
                    node_level_str += '    coverage: ' + \
                            str(len(value[categories]) - uncovered) + \
                            '/' + str(len(value[categories]))
                    rpt_str += node_level_str + '\n'
                    if detailed:
                        rpt_str += '    detail:\n'
                        for coverpoints in value[categories]:
                            rpt_str += '      - '+str(coverpoints) + ': ' + str(value[categories][coverpoints]) + '\n'
    return rpt_str

def merge_coverage(files, cgf_file, detailed, xlen):
    '''
    This function merges values of multiple CGF files and return a single cgf
    file. This can be treated analogous to how coverage files are merged
    traditionally.

    :param file: an array of input CGF file names which need to be merged.
    :param cgf_file: an input CGF file which contains all the nodes of interest.
    :param detailed: a boolean value indicating if a detailed report needs to be generated
    :param xlen: XLEN of the trace

    :type file: [str]
    :type cgf_file: str
    :type detailed: bool
    :type xlen: int

    :return: a string contain the final report of the merge.
    '''
    with open(cgf_file, "r") as file:
        cgf = expand_cgf(yaml.load(file),xlen)
    for logs in files:
        with open(logs, "r") as file:
            logs_cov = yaml.load(file)
        for cov_labels, value in logs_cov.items():
            for categories in value:
                if categories not in ['cond','config','ignore']:
                    for coverpoints, coverage in value[categories].items():
                        if coverpoints in cgf[cov_labels][categories]:
                            cgf[cov_labels][categories][coverpoints] += coverage
    return gen_report(cgf, detailed)

def twos_complement(val,bits):
    if (val & (1 << (bits - 1))) != 0:
        val = val - (1 << bits)
    return val

def compute_per_line(instr, commitvalue, cgf, xlen, addr_pairs):
    '''
    This function checks if the current instruction under scrutiny matches a
    particular coverpoint of interest. If so, it updates the coverpoints and
    return the same.

    :param instr: an instructionObject of the single instruction currently parsed
    :param commitvalue: a tuple containing the register to be updated and the value it should be updated with
    :param cgf: a cgf file against which coverpoints need to be checked for.
    :param xlen: Max xlen of the trace
    :param addr_pairs: pairs of start and end addresses for which the coverage needs to be updated

    :type instr: :class:`helpers.instructionObject`
    :type commitvalue: (str, str)
    :type cgf: dict
    :type xlen: int
    :type addr_pairs: (int, int)
    '''
    global regfile

    # assign default values to operands
    rs1 = 0
    rs2 = 0
    rd  = 0

    # create signed/unsigned conversion params
    if xlen == 32:
        unsgn_sz = '>I'
        sgn_sz = '>i'
    else:
        unsgn_sz = '>Q'
        sgn_sz = '>q'

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


    if enable:

        # capture the operands and their values from the regfile
        if instr.rs1 is not None:
            rs1 = instr.rs1[0]
        if instr.rs2 is not None:
            rs2 = instr.rs2[0]
        if instr.rd is not None:
            rd = instr.rd[0]
        if instr.imm is not None:
            imm_val = instr.imm
        if instr.shamt is not None:
            imm_val = instr.shamt

        # special value conversion based on signed/unsigned operations
        if instr.instr_name in ['bgeu', 'bltu', 'sltiu', 'sltu']:
            rs1_val = struct.unpack(unsgn_sz, bytes.fromhex(regfile[rs1]))[0]
        else:
            rs1_val = struct.unpack(sgn_sz, bytes.fromhex(regfile[rs1]))[0]

        if instr.instr_name in ['bgeu', 'bltu', 'sltiu', 'sltu', 'sll', 'srl', 'sra']:
            rs2_val = struct.unpack(unsgn_sz, bytes.fromhex(regfile[rs2]))[0]
        else:
            rs2_val = struct.unpack(sgn_sz, bytes.fromhex(regfile[rs2]))[0]

        # the ea_align variable is used by the eval statements of the
        # coverpoints for conditional ops and memory ops
        if instr.instr_name in ['jal','bge','bgeu','blt','bltu','beq','bne']:
            ea_align = (instr.instr_addr+(imm_val<<1)) % 4

        if instr.instr_name == "jalr":
            ea_align = (rs1_val + imm_val) % 4

        if instr.instr_name in ['sw','sh','sb','lw','lhu','lh','lb','lbu','lwu']:
            ea_align = (rs1_val + imm_val) % 4
        if instr.instr_name in ['ld','sd']:
            ea_align = (rs1_val + imm_val) % 8

        logger.debug(instr)

        for cov_labels,value in cgf.items():
            if cov_labels != 'datasets':
                if instr.instr_name in value['opcode']:
                    value['opcode'][instr.instr_name] += 1
                    if 'rs1' in value and 'x'+str(rs1) in value['rs1']:
                        value['rs1']['x'+str(rs1)] += 1
                    if 'rs2' in value and 'x'+str(rs2) in value['rs2']:
                        value['rs2']['x'+str(rs2)] += 1
                    if 'rd' in value and 'x'+str(rd) in value['rd']:
                        value['rd']['x'+str(rd)] += 1
                    if 'op_comb' in value and len(value['op_comb']) != 0 :
                        for coverpoints in value['op_comb']:
                            if eval(coverpoints):
                                cgf[cov_labels]['op_comb'][coverpoints] += 1
                    if 'val_comb' in value and len(value['val_comb']) != 0 :
                        for coverpoints in value['val_comb']:
                            if eval(coverpoints):
                                cgf[cov_labels]['val_comb'][coverpoints] += 1
                    if 'abstract_comb' in value and len(value['abstract_comb']) != 0 :
                        for coverpoints in value['abstract_comb']:
                            if eval(coverpoints):
                                cgf[cov_labels]['abstract_comb'][coverpoints] += 1

        if commitvalue is not None:
            regfile[int(commitvalue[1])] =  str(commitvalue[2][2:])

    return cgf

def compute(trace_file, cgf_files, mode, detailed, xlen, addr_pairs
        , dump, cov_labels):
    '''Compute the Coverage'''

    global regfile
    with utils.combineReader(cgf_files) as fp:
            cgf = expand_cgf(yaml.load(fp), xlen)

    if cov_labels:
        temp = {}
        for label in cov_labels:
            if label in cgf:
                temp[label] = cgf[label]
            else:
                logger.warn(label + ": Label not found in cgf file.")
        cgf = temp

    if dump is not None:
        dump_f = open(dump, 'w')
        dump_f.write(ruamel.yaml.round_trip_dump(cgf, indent=5, block_seq_indent=3))
        dump_f.close()
        sys.exit(0)

    if xlen == 32:
        regfile = ['00000000']*32
    else:
        regfile = ['0000000000000000']*32

    if mode == 'c_sail':
        with open(trace_file) as fp:
            content = fp.read()
        instructions = content.split('\n\n')
        print(len(instructions))
        for x in instructions:
            instr = helpers.parseInstruction(x, mode,"rv"+str(xlen))
            commitvalue = helpers.extractRegisterCommitVal(x, mode)
            cgf= compute_per_line(instr, commitvalue, cgf, xlen,
                    addr_pairs)
    elif mode == 'spike':
        with open(trace_file) as fp:
            for line in fp:
                instr = helpers.parseInstruction(line, mode,"rv"+str(xlen))
                commitvalue = helpers.extractRegisterCommitVal(line, mode)
                cgf = compute_per_line(instr, commitvalue, cgf, xlen,
                        addr_pairs)
    rpt_str = gen_report(cgf, detailed)
    dump_file = open(trace_file+'.cgf', 'w')
    dump_file.write(ruamel.yaml.round_trip_dump(cgf, indent=5, block_seq_indent=3))
    dump_file.close()


    return rpt_str
