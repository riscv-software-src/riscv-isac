
''' Parser for the execution trace file '''
import os
import re
import importlib

''' Constants for extracting the bits '''
FIRST2_MASK = 0x00000003
OPCODE_MASK = 0x0000007f

def extractOpcode(instr):
    ''' Function to extract the opcode from the instruction hex '''
    return OPCODE_MASK & instr

def parseInstruction(input_line, mode, arch='rv32'):

    ''' Check if we are parsing compressed or normal instructions '''
    try:
        mode_plugin = importlib.import_module("parser_"+ mode)
    except:
        print("Error while importing parser_"+ mode)
        instr = None

    if instr is None:
#        print("Skipping {}".format(input_line))
        return None, None
    
    try:
        class_m = getattr(mode_plugin, "class_"+mode) 
        extractInstruction = getattr(class_m, "extractInstruction")
        extractAddress = getattr(class_m, "extractAddress" )
    except KeyError as e:
        print("Attributes not found")
        return None, None

    instr, mnemonic = extractInstruction(input_line)
    addr = extractAddress(input_line)

    first_two_bits = FIRST2_MASK & instr

    if first_two_bits == 0b11:
        return parseStandardInstruction(instr, addr, arch), mnemonic
    else:
        return parseCompressedInstruction(instr, addr, arch), mnemonic

def parseCompressedInstruction(instr, addr, arch):
    ''' Parse a compressed instruction
        Args: instr, addr from ParseInstruction.
        Returns: (instr_obj)
    '''
    
    opcode = FIRST2_MASK & instr

    try:
        instr_plugin = importlib.import_module("Instruction_plugin")
    except:
        print("Error while importing Instruction_plugin")
        return None

    try:
        class_i = getattr(instr_plugin, "Plugin_dp")
        C_OPCODES = getattr(class_i, "C_OPCODES")
        instruction = getattr(class_i, C_OPCODES[opcode])
        instrObj = instruction(instr, addr, arch)
    except KeyError as e:
        print("Instruction not found", hex(instr))
        return None

    return instrObj

def parseStandardInstruction(instr, addr, arch):
    ''' Parse an input line and decode the instruction
        Args: input_line - Line from the log file
        Returns: (instr_name, rd, rs1, rs2, imm)
    '''
    opcode = extractOpcode(instr)

    try:
        instr_plugin = importlib.import_module("Instruction_plugin")
    except:
        print("Error while importing Instruction_plugin")
        return None

    try:
        class_i = getattr(instr_plugin, "Plugin_dp")
        OPCODES = getattr(class_i, "OPCODES")
        instruction = getattr(class_i, OPCODES[opcode])
        instrObj = instruction(instr, addr, arch)
    except KeyError as e:
        print("Instruction not found", hex(instr))
        return None

    return instrObj