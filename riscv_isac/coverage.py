import ruamel
from ruamel.yaml import YAML
import riscv_isac.parsers as helpers
from collections import Counter
import sys
yaml = YAML(typ="rt")
yaml.default_flow_style = False
yaml.allow_unicode = True


'''Histogram post-processing module'''

help_message = '{:<20s} {:<10s}'.format('coverage', 'Compliance Coverage')

def pretty_print_yaml(yaml):
    res = ''''''
    for line in ruamel.yaml.round_trip_dump(yaml, indent=5, block_seq_indent=3).splitlines(True):
        res += line
    return res

def pretty_print_regfile(regfile):
    res = ""
    for index in range(0, 32, 4):
        print('x'+str(index) + ' : ' + str(regfile[index]) + '\t' +\
                'x'+str(index+1) + ' : ' + str(regfile[index+1]) + '\t' + \
                'x'+str(index+2) + ' : ' + str(regfile[index+2]) + '\t' + \
                'x'+str(index+3) + ' : ' + str(regfile[index+3]) + '\t' )
    print('\n\n')

def add_cov_points(cgf):
    for key,value in cgf.items():
        cov_dict = {}
        for nodes in value:
            if nodes != 'config' and nodes != 'opcode':
                length = len(value[nodes])
                init_cov = [0]*length
                cov_dict[nodes+'_cov'] = init_cov
        cgf[key].update(cov_dict)
    return cgf

def gen_report(cgf, detailed):
    rpt_str = ''
    for cov_points, value in cgf.items():
        rpt_str += cov_points + ':\n'
        total_uncovered = 0
        total_nodes = 0
        for nodes in value:
            if nodes != 'config' and nodes != 'opcode' and '_cov' not in nodes:
                total_uncovered += value[nodes+'_cov'].count(0)
                total_nodes += len(value[nodes])
        rpt_str += '  coverage: '+str(total_nodes -total_uncovered) + \
                '/' + str(total_nodes)+'\n'
        for nodes in value:
            if nodes != 'config' and nodes != 'opcode' and '_cov' not in nodes:
                uncovered = value[nodes+'_cov'].count(0)
                percentage_covered = str((len(value[nodes]) - uncovered)/len(value[nodes]))
                node_level_str =  '  ' + nodes + ':\n'
                node_level_str += '    coverage: ' + \
                        str(len(value[nodes]) - uncovered) + \
                        '/' + str(len(value[nodes]))
                rpt_str += node_level_str + '\n'
                if detailed:
                    rpt_str += '    detail:\n'
                    for x in range(len(value[nodes])):
                        rpt_str += '      - '+str(value[nodes][x]) + ': ' + str(value[nodes+'_cov'][x]) + '\n'
    return rpt_str

def merge_coverage(files, cgf_file, detailed):
    with open(cgf_file, "r") as file:
        cgf = add_cov_points(yaml.load(file))
    for logs in files:
        with open(logs, "r") as file:
            logs_cov = yaml.load(file)
        for key, value in cgf.items():
            for nodes in value:
                if '_cov' in nodes:
                    for x in range(len(value[nodes])):
                        cgf[key][nodes][x] += logs_cov[key][nodes][x]
    return gen_report(cgf, detailed)

def twos_complement(val,bits):
    if (val & (1 << (bits - 1))) != 0:
        val = val - (1 << bits)
    return val

def compute_per_line(line, cgf, mode, xlen, regfile, saddr, eaddr):
    instr = helpers.parseInstruction(line, mode)
    rs1 = 0
    rs2 = 0
    rd = 0
    if saddr is not None and eaddr is not None:
        if instr.instr_addr >= saddr and instr.instr_addr <= eaddr:
            enable = True
        else:
            enable = False
    else:
        enable=True
    if instr is not None and enable:
        commitvalue = helpers.extractRegisterCommitVal(line)
        if instr.rs1 is not None:
            rs1 = instr.rs1[0]
        if instr.rs2 is not None:
            rs2 = instr.rs2[0]
        if instr.imm is not None:
            imm_val = instr.imm
        if instr.shamt is not None:
            shift_val = instr.shamt
        if instr.rd is not None:
            rd = instr.rd[0]

        if instr.instr_name in ['bgeu', 'bltu', 'sltiu', 'sltu']:
            rs1_val = regfile[rs1]
        else:
            rs1_val = twos_complement(regfile[rs1], xlen)

        if instr.instr_name in ['bgeu', 'bltu', 'sltiu', 'sltu', 'sll', 'srl', 'sra']:
            rs2_val = regfile[rs2]
        else:
            rs2_val = twos_complement(regfile[rs2], xlen)

        if commitvalue is not None:
            rd_val = twos_complement(int(commitvalue[2],16), xlen)
        else:
            rd_val = 0
        for key,value in cgf.items():
            if instr.instr_name == value['opcode']:
                if 'rs1' in value and 'x'+str(rs1) in value['rs1']:
                    index = value['rs1'].index('x'+str(rs1))
                    cgf[key]['rs1_cov'][index] += 1
                if 'rs2' in value and 'x'+str(rs2) in value['rs2']:
                    index = value['rs2'].index('x'+str(rs2))
                    cgf[key]['rs2_cov'][index] += 1
                if 'rd' in value and 'x'+str(rd) in value['rd']:
                    index = value['rd'].index('x'+str(rd))
                    cgf[key]['rd_cov'][index] += 1
                if 'imm_val' in value and imm_val in value['imm_val']:
                    index = value['imm_val'].index(imm_val)
                    cgf[key]['imm_val_cov'][index] += 1
                if 'rs1_val' in value and rs1_val in value['rs1_val']:
                    index = value['rs1_val'].index(rs1_val)
                    cgf[key]['rs1_val_cov'][index] += 1
                if 'rs2_val' in value and rs2_val in value['rs2_val']:
                    index = value['rs2_val'].index(rs2_val)
                    cgf[key]['rs2_val_cov'][index] += 1
                if 'rd_val' in value and rd_val in value['rd_val']:
                    index = value['rd_val'].index(rd_val)
                    cgf[key]['rd_val_cov'][index] += 1
                if 'op_comb' in value and len(value['op_comb']) != 0 :
                    for x in range(len(value['op_comb'])):
                        if eval(value['op_comb'][x]):
                            cgf[key]['op_comb_cov'][x] += 1
                if 'val_comb' in value and len(value['val_comb']) != 0 :
                    for x in range(len(value['val_comb'])):
                        if eval(value['val_comb'][x]):
                            cgf[key]['val_comb_cov'][x] += 1

        if commitvalue is not None:
            regfile[int(commitvalue[1])] =  int(commitvalue[2], 16)

    return cgf, regfile

def compute(trace_file, cgf_file, mode, merge_cov, detailed, xlen, saddr,
        eaddr):
    '''Compute the Coverage'''

    regfile = [0]*32

    if merge_cov:
        return merge_coverage(merge_cov, cgf_file, detailed)
    else:
        with open(cgf_file, "r") as file:
            cgf = add_cov_points(yaml.load(file))

        with open(trace_file) as fp:
            for line in fp:
                cgf, regfile = compute_per_line(line, cgf, mode, xlen, regfile,
                        saddr, eaddr)
        rpt_str = gen_report(cgf, detailed)
        dump_file = open(trace_file+'.cgf', 'w')
        dump_file.write(ruamel.yaml.round_trip_dump(cgf, indent=5, block_seq_indent=3))
        dump_file.close()

        return rpt_str
