import glob
from operator import itemgetter
from collections import defaultdict
import pprint
from statistics import mode

from ruamel import yaml as YAML

from constants import *
from riscv_isac.InstructionObject import instructionObject
from riscv_isac.plugins.internaldecoder import disassembler

#export PYTHONPATH=/home/edwin/myrepos/riscv-isac/

# Closure to get argument value
# TODO Handle special immediates
def get_arg_val(arg: str):
    (msb, lsb) = arg_lut[arg]
    mask = int(''.join('1' * (msb - lsb + 1)), 2) << lsb
    def mcode_in(mcode: int):
        val = (mask & mcode) >> lsb
        return val
    return mcode_in

# Functs handler
def get_funct(pos_tuple: tuple, mcode: int):
    msb = pos_tuple[0]
    lsb = pos_tuple[1]
    mask = int(''.join('1' * (msb - lsb + 1)), 2) << lsb
    val = (mask & mcode) >> lsb
    
    return val

class rvOpcodesDecoder:

    FIRST_TWO = 0x00000003
    OPCODE_MASK = 0x0000007f

    INST_LIST = []

    def __init__(self, file_filter: str):
        
        # Create nested dictionary
        nested_dict = lambda: defaultdict(nested_dict)
        rvOpcodesDecoder.INST_DICT = nested_dict()

        rvOpcodesDecoder.create_inst_dict(file_filter)

    def process_enc_line(line: str):

        functs = []
        args = []

        # get the name of instruction by splitting based on the first space
        [name, remaining] = line.split(' ', 1)

        # replace dots with underscores as dot doesn't work with C/Sverilog, etc
        name = name.replace('.', '_')

        # remove leading whitespaces
        remaining = remaining.lstrip()
       
        # extract bit pattern assignments of the form hi..lo=val. fixed_ranges is a
        # regex expression present in constants.py. The extracted patterns are
        # captured as a list in args where each entry is a tuple (msb, lsb, value)
        
        opcode_parsed = fixed_ranges.findall(remaining)
        opcode_functs = []
        for func in opcode_parsed:
            opcode_functs.append([int(a, 0) for a in func])

        # Sort in ascending order of lsb
        opcode_functs = sorted(opcode_functs, key=itemgetter(1))
        for (msb, lsb, value) in opcode_functs:
            flen = msb - lsb + 1
            value = f"{value:0{flen}b}"
            value = int(value, 2)     
            funct = (msb, lsb)

            functs.append((funct, value))

        # parse through the args
        args_list = fixed_ranges.sub(' ', remaining)
        args_list = single_fixed.sub(' ', args_list).split()
        for arg in args_list:
            args.append(arg)

        # do the same as above but for <lsb>=<val> pattern. single_fixed is a regex
        # expression present in constants.py
        for (lsb, value, drop) in single_fixed.findall(remaining):
            lsb = int(lsb, 0)
            value = int(value, 0)
            functs.append(((lsb, lsb), value))

        return (functs, (name, args))
    
    def create_inst_dict(file_filter):
        opcodes_dir = f'./riscv_opcodes/'

        # file_names contains all files to be parsed in the riscv-opcodes directory
        file_names = glob.glob(f'{opcodes_dir}rv{file_filter}')

        # first pass if for standard/original instructions
        for f in file_names:
            with open(f) as fp:
                lines = (line.rstrip()
                        for line in fp)  # All lines including the blank ones
                lines = list(line for line in lines if line)  # Non-blank lines
                lines = list(
                    line for line in lines
                    if not line.startswith("#"))  # remove comment lines

            # go through each line of the file
            for line in lines:
                # if the an instruction needs to be imported then go to the
                # respective file and pick the line that has the instruction.
                # The variable 'line' will now point to the new line from the
                # imported file

                # ignore all lines starting with $import and $pseudo
                if '$import' in line or '$pseudo' in line:
                    continue

                (functs, (name, args)) = rvOpcodesDecoder.process_enc_line(line)

                # [  [(funct, val)], name, [args]  ]
                rvOpcodesDecoder.INST_LIST.append([functs, name, args])

        rvOpcodesDecoder.INST_DICT['root'] = rvOpcodesDecoder.INST_LIST
        rvOpcodesDecoder.build_instr_dict(rvOpcodesDecoder.INST_DICT)
    
    def build_instr_dict(inst_dict):
        
        # Get all instructions in the level
        val = inst_dict['root']
        
        # Gather all functs
        funct_list = [item[0] for item in val]
        funct_occ = [funct[0] for ins in funct_list for funct in ins]
        
        # Path recoder
        funct_path = set()
        # Check if there are functions remaining
        while funct_occ:
            if (1, 0) in funct_occ:
                max_funct = (1, 0)
            else:
                max_funct = mode(funct_occ)

            funct_occ = list(filter(lambda a: a != max_funct, funct_occ))

            i = 0
            # For each instruciton...
            while i < len(val):
                # For each funct of each instruction...
                for funct in val[i][0]:
                    if funct[0] == max_funct:
                        # Max funct found!
                        
                        # Push into path recorder
                        funct_path.add(funct)
                        
                        # Push funct and its value into the dict
                        temp_dict = inst_dict[funct[0]][funct[1]]
                        
                        # Create empty list in the path
                        if not temp_dict:
                            inst_dict[funct[0]][funct[1]]['root'] = []
                        
                        # Delete appended funct
                        temp = val[i]
                        temp[0].remove(funct)
                        
                        if temp[0]:
                            # Add to the path
                            inst_dict[funct[0]][funct[1]]['root'].append(temp)
                            
                            # Remove the copied instruction from previous list
                            inst_dict['root'].remove(val[i])
                        else:
                            # Append name and args
                            temp_dict[temp[1]] = temp[2]

                        i = i - 1
                        
                i = i + 1
        else:
            # Remove previous root
            del inst_dict['root']

            for funct in funct_path:

                new_path = inst_dict[funct[0]][funct[1]]
                a = rvOpcodesDecoder.build_instr_dict(new_path)
                if a == None:
                    continue
                else:
                    return a
            return
            
    def get_instr(func_dict, mcode: int):
        # Get list of functions
        keys = func_dict.keys()
        for key in keys:
            if type(key) == str:     
                return func_dict
            if type(key) == tuple:
                val = get_funct(key, mcode)
            temp_func_dict = func_dict[key][val]
            if temp_func_dict.keys():
                a = rvOpcodesDecoder.get_instr(temp_func_dict, mcode)
                if a == None:
                    continue
                else:
                    return a
            else:
                continue
    
    def decoder(self, temp_instrobj: instructionObject):
        

        mcode = temp_instrobj.instr

        name_args = rvOpcodesDecoder.get_instr(rvOpcodesDecoder.INST_DICT, mcode)

        # Fill out the partially filled instructionObject
        if name_args:
            instr_names = list(name_args.keys())
            if len(instr_names) <= 1:
                # Fill instruction name
                temp_instrobj.instr_name = instr_names[0]

                # Fill arguments
                args = name_args[instr_names[0]]
                imm = ''
                for arg in args:
                    if arg == 'rd':
                        temp_instrobj.rd = get_arg_val(arg)(mcode)
                    if arg == 'rs1':
                        temp_instrobj.rs1 = get_arg_val(arg)(mcode)
                    if arg == 'rs2':
                        temp_instrobj.rs2 = get_arg_val(arg)(mcode)
                    if arg == 'rs3':
                        temp_instrobj.rs3 = get_arg_val(arg)(mcode)
                    if arg == 'csr':
                        temp_instrobj.csr = get_arg_val(arg)(mcode)
                    if arg == 'shamt':
                        temp_instrobj.shamt = get_arg_val(arg)(mcode)
                    if arg == 'succ':
                        temp_instrobj.succ = get_arg_val(arg)(mcode)
                    if arg == 'pred':
                        temp_instrobj.pred = get_arg_val(arg)(mcode)
                    if arg == 'rl':
                        temp_instrobj.rl = get_arg_val(arg)(mcode)
                    if arg == 'aq':
                        temp_instrobj.aq = get_arg_val(arg)(mcode)
                    if arg == 'rm':
                        temp_instrobj.rm = get_arg_val(arg)(mcode)
    
                    if arg in ['imm12', 'imm20', 'zimm', 'imm2', 'imm3', 'imm4', 'imm5', 'imm']:
                        temp_instrobj.imm = get_arg_val(arg)(mcode)
                    if arg == 'jimm20':
                        imm_temp = get_arg_val(arg)(mcode)
                        print(imm_temp)
                        imm_temp = f'{imm_temp:0{20}b}'
                        #imm_temp = '123456789abcdefghijkl'
                        print(imm_temp)
                        imm = imm_temp[0] + imm_temp[12:21] + imm_temp[12] + imm_temp[1:11]
                        print(imm)
                        temp_instrobj.imm = int(imm, 2)
                return temp_instrobj

            else:
                print('Found two instructions in the leaf node')

    def default_to_regular(d):
        if isinstance(d, defaultdict):
            d = {k: rvOpcodesDecoder.default_to_regular(v) for k, v in d.items()}
        return d
    
    def print_instr_dict():
        
        printer = pprint.PrettyPrinter(indent=1, width=800, depth=None, stream=None,
                 compact=False, sort_dicts=False)
        
        s = printer.pformat(rvOpcodesDecoder.default_to_regular(rvOpcodesDecoder.INST_DICT))
        f = open('dict_tree.txt', 'w+')
        f.write(s)
        f.close()

if __name__ == '__main__':

    decoder = rvOpcodesDecoder('*')
    rvOpcodesDecoder.print_instr_dict()

    ins = instructionObject(0x095050ef, '', '')

    # Tests
    name = decoder.decoder(ins).imm
    print(hex(name))
    
    #name = decoder.decoder(0x00000073).keys()
    
    
    '''f1 = open('./tests/none_result.txt', 'w+')
    f2 = open('./tests/matches_results.txt' , 'w+')
    f3 = open('./tests/no_matches_results.txt' , 'w+')

    with open('./tests/ratified.txt', 'r') as fp:
        for line in fp:
            line = line.strip('\n')
            code = int(line, 16)
            ins_obj = instructionObject(code, '', '')
            
            old_decoder = disassembler()
            old_decoder.setup('rv32')
            
            old_res = old_decoder.decode(ins_obj).instr_name
            result = decoder.decoder(code)

            if old_res:
                old_res = old_res.replace('.', '_')
            else:
                old_res = None
            
            if result != None:
                result = list(decoder.decoder(code).keys())[0]

            if result and old_res:
                if old_res == result:
                    f2.write(f'Match found! {result} for {line}\n')
                else:
                    f3.write(f'Not matching! {line}: {result} for rvopcodes-decoder; {old_res} for internal decoder\n')
            else:
                if not result:
                    result = 'None'
                if not old_res:
                    old_res = 'None'
                f1.write(f'{line}: {result} for rvopcodes-decoder; {old_res} for internal decoder\n')
                
    f1.close()
    f2.close()
    f3.close()'''