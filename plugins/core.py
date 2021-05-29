## core.py
## Subdirectory - plugins - {base_pp, base_dp}

##  reg_commit, line, 2's complement

''' Parser for the execution trace file '''
import os
import re
from base_pp import Modes, init_plugin_m ## Parser plugin
from base_dp import Plugin_dp ## Disassembly plugin


''' Constants for extracting the bits '''
FIRST2_MASK = 0x00000003
OPCODE_MASK = 0x0000007f

## Adding patterns according to new models of Risc-V
instr_pattern_standard = re.compile('core\s+[0-9]+:\s+(?P<addr>[0-9abcdefx]+)\s+\((?P<instr>[0-9abcdefx]+)\)')
instr_pattern_spike = re.compile(
        '[0-9]\s(?P<addr>[0-9abcdefx]+)\s\((?P<instr>[0-9abcdefx]+)\)')
instr_pattern_spike_xd = re.compile(
        '[0-9]\s(?P<addr>[0-9abcdefx]+)\s\((?P<instr>[0-9abcdefx]+)\)' +
        '\s(?P<regt>[xf])(?P<reg>[\s|\d]\d)\s(?P<val>[0-9abcdefx]+)'
)
instr_pattern_c_sail= re.compile(
        '\[\d*\]\s\[(.*?)\]:\s(?P<addr>[0-9xABCDEF]+)\s\((?P<instr>[0-9xABCDEF]+)\)\s*(?P<mnemonic>.*)')
instr_pattern_c_sail_regt_reg_val = re.compile('(?P<regt>[xf])(?P<reg>[\d]+)\s<-\s(?P<val>[0-9xABCDEF]+)')
''' Regex pattern and functions for extracting instruction and address '''


def extractOpcode(instr):
    ''' Function to extract the opcode from the instruction hex '''
    return OPCODE_MASK & instr

## Initializing - Parser plugin
init_plugin_m()

## Where are we getting input_line??
## 2's complement
def parseInstruction(input_line, mode, arch='rv32'):

    ''' Check if we are parsing compressed or normal instructions '''

    if mode in Modes:
      class_m = Modes[mode]
      instr, mnemonic = class_m.extractInstruction(input_line)
    else:
      instr = None

    if instr is None:
#        print("Skipping {}".format(input_line))
        return None, None

    first_two_bits = FIRST2_MASK & instr

    if first_two_bits == 0b11:
        return parseStandardInstruction(input_line, mode, arch), mnemonic
    else:
        return parseCompressedInstruction(input_line, mode, arch), mnemonic

def parseCompressedInstruction(input_line, mode, arch):
    ''' Parse a compressed instruction
        Args: input_line - Line from the log file
        Returns: (instr_obj)
    '''
    
    if mode in Modes:
      class_m = Modes[mode]
      instr, mnemonic = class_m.extractInstruction(input_line)
    else:
      instr = None

    if instr is None:
        return None

    addr = class_m.extractAddress(input_line)
    opcode = FIRST2_MASK & instr


    try:
        class_i = Plugin_dp()
        instrObj = class_i.C_OPCODES[opcode](instr, addr, arch)
    except KeyError as e:
        print("Instruction not found", hex(instr))
        return None

    return instrObj

def parseStandardInstruction(input_line, mode, arch):
    ''' Parse an input line and decode the instruction
        Args: input_line - Line from the log file
        Returns: (instr_name, rd, rs1, rs2, imm)
    '''
    
    if mode in Modes:
      class_m = Modes[mode]
      instr, mnemonic = class_m.extractInstruction(input_line)
    else:
      instr = None

    if instr is None:
        return None

    addr = class_m.extractAddress(input_line)
    opcode = extractOpcode(instr)

 
    try:
        class_i = Plugin_dp()
        instrObj = class_i.OPCODES[opcode](instr, addr, arch)
    except KeyError as e:
        print("Instruction not found", hex(instr))
        return None

    return instrObj
