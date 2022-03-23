import glob
from lib2to3.pgen2.token import VBAREQUAL
from operator import itemgetter
from collections import defaultdict
import pprint

from attr import field

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

# Standard functs
def func2(mcode: int):
    (msb, lsb) = arg_lut['funct2']
    mask = int(''.join('1' * (msb - lsb + 1)), 2) << lsb
    val = (mask & mcode) >> lsb
    
    return val

def func3(mcode: int):
    (msb, lsb) = arg_lut['funct3']
    mask = int(''.join('1' * (msb - lsb + 1)), 2) << lsb
    val = (mask & mcode) >> lsb
    
    return val

def func7(mcode: int):
    (msb, lsb) = arg_lut['funct7']
    mask = int(''.join('1' * (msb - lsb + 1)), 2) << lsb
    val = (mask & mcode) >> lsb
    
    return val

# For Non standard functs
def get_funct(pos_tuple: tuple, mcode: int):
    msb = pos_tuple[0]
    lsb = pos_tuple[1]
    mask = int(''.join('1' * (msb - lsb + 1)), 2) << lsb
    val = (mask & mcode) >> lsb
    
    return val

# For rd check:
def rd_check(mcode: int):
    mask = 0x00000f80
    val = (mask & mcode) >> 7
    return val

class rvOpcodesDecoder:

    FIRST_TWO = 0x00000003
    OPCODE_MASK = 0x0000007f

    def __init__(self, file_filter: str):
        
        # Create nested dictionary
        nested_dict = lambda: defaultdict(nested_dict)
        rvOpcodesDecoder.INS_DICT = nested_dict()
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
            args.append(get_arg_val(arg))

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
        
        funct_priority = dict()
        instr_list = list()

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

                # Priority dictionary
                for funct in functs:
                    if funct[0] in funct_priority:
                        count = funct_priority[funct[0]]
                        count += 1
                        funct_priority[funct[0]] = count
                    else:
                        funct_priority[funct[0]] = 1

                # [  [(funct, val)], name, [args]  ]
                instr_list.append([functs, name, args])
                

                '''func_dict = rvOpcodesDecoder.INS_DICT
                for func in functs:
                    func_dict = func_dict[func[0]]
                    func_dict = func_dict[func[-1]]
                
                func_dict[name] = args'''
        
        op_end = 2
        # Sort functions for each instruction
        for i in range(len(instr_list)):
            op = instr_list[i][0][0:op_end]
            functs = instr_list[i][0][op_end:]
            p_list = []
            for funct in functs:
                p_list.append(funct_priority[funct[0]])
            
            functs_sorted = [x for _,x in sorted(zip(p_list, functs), key=lambda key: key[0], reverse=True)]
            fields = op + functs_sorted
            instr_list[i][0] = fields


            if instr_list[i][1] == 'lr_w':
                print(functs)
                print(p_list)
                print(fields)
                print(fields)

        for instr in instr_list:
            funct_dict = rvOpcodesDecoder.INS_DICT
            for funct in instr[0]:
                funct_dict = funct_dict[funct[0]]
                funct_dict = funct_dict[funct[-1]]
            
            funct_dict[instr[1]] = instr[2]

    def get_instr(func_dict, mcode: int):
        # Get list of functions
        keys = func_dict.keys()
        print(keys)
        for key in keys:
            if type(key) == str:     
                return func_dict
            if type(key) == tuple:
                val = get_funct(key, mcode)             # Non standard fields
            else:
                val = key(mcode)                        # Standard fields
            print(val)
            temp_func_dict = func_dict[key][val]
            if temp_func_dict.keys():
                a = rvOpcodesDecoder.get_instr(temp_func_dict, mcode)
                #if a == None:
                #    continue
                #else:
                return a
            else:
                continue
    
    def decoder(self, mcode):
        
        func_dict = rvOpcodesDecoder.INS_DICT
        name_args = rvOpcodesDecoder.get_instr(func_dict, mcode)

        #TODO Create instruction object

        return name_args

    def print_instr_dict():
        
        printer = pprint.PrettyPrinter(indent=1, width=800, depth=None, stream=None,
                 compact=False, sort_dicts=False)
        
        s = printer.pformat(rvOpcodesDecoder.INS_DICT)
        f = open('dict_tree.txt', 'w+')
        f.write(s)
        f.close()

if __name__ == '__main__':

    decoder = rvOpcodesDecoder('*')
    rvOpcodesDecoder.print_instr_dict()
    
    # Tests
    name = decoder.decoder(0x8000202f).keys()
    print(name)
    
    '''
    f1 = open('./tests/none_result.txt', 'w+')
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