## core.py
## Subdirectory - plugins - {base_pp, base_dp}

## 3 subclasses, reg_commit, line, 2's complement

''' Parser for the execution trace file '''
import os
import re
from base_pp import Modes, init_plugin_m ## Parser plugin
from base_dp import OPCODES, init_plugin_i ## Disassembly plugin

''' Instruction Object '''
class instructionObject:
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



''' Constants for extracting the bits '''
FIRST2_MASK = 0x00000003
OPCODE_MASK = 0x0000007f
FUNCT3_MASK = 0x00007000
RD_MASK = 0x00000f80
RS1_MASK = 0x000f8000
RS2_MASK = 0x01f00000

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
      instr, mnemonic = class_m.extractInstruction(input_line, mode)
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
      instr, mnemonic = class_m.extractInstruction(input_line, mode)
    else:
      instr = None

    if instr is None:
        return None

    addr = class_m.extractAddress(input_line, mode)
    opcode = FIRST2_MASK & instr

    init_plugin_i(instr, addr, arch)
    try:
        class_i = OPCODES[opcode]
        instrObj = class_i.instrObj
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
      instr, mnemonic = class_m.extractInstruction(input_line, mode)
    else:
      instr = None

    if instr is None:
        return None

    addr = class_m.extractAddress(input_line, mode)
    opcode = extractOpcode(instr)

    init_plugin_i(instr, addr, arch)
    try:
        class_i = OPCODES[opcode]
        instrObj = class_i.instrObj
    except KeyError as e:
        print("Instruction not found", hex(instr))
        return None

    return instrObj



