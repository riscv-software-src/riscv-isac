import re
import riscv_isac.plugins as plugins
import riscv_isac.plugins. specification as spec
from riscv_isac.InstructionObject import instructionObject
from riscv_isac.log import logger

class c_sail(spec.ParserSpec):

    @plugins.parserHookImpl
    def setup(self, trace, arch):
        self.trace = trace
        self.arch = arch
        if arch[1] == 32:
            logger.warn('FLEN is set to 32. Commit values in the log will be terminated to 32 bits \
irrespective of their original size.')

    instr_pattern_c_sail= re.compile(
        '\[\d*\]\s\[(?P<mode>.*?)\]:\s(?P<addr>[0-9xABCDEF]+)\s\((?P<instr>[0-9xABCDEF]+)\)\s*(?P<mnemonic>.*)')
    instr_pattern_c_sail_regt_reg_val = re.compile('(?P<regt>[xf])(?P<reg>[\d]+)\s<-\s(?P<val>[0-9xABCDEF]+)')
    instr_pattern_c_sail_csr_reg_val = re.compile('(?P<CSR>CSR|clint::tick)\s(?P<reg>[a-z0-9]+)\s<-\s(?P<val>[0-9xABCDEF]+)(?:\s\(input:\s(?P<input_val>[0-9xABCDEF]+)\))?')
    instr_pattern_c_sail_mem_val = re.compile('mem\[(?P<addr>[0-9xABCDEF]+)\]\s<-\s(?P<val>[0-9xABCDEF]+)')
    instr_pattern_c_sail_trap = re.compile(r'trapping\sfrom\s(?P<mode_change>\w+\sto\s\w+)\sto\shandle\s(?P<call_type>\w+.*)\shandling\sexc#(?P<exc_num>0x[0-9a-fA-F]+)\sat\spriv\s\w\swith\stval\s(?P<tval>0x[0-9a-fA-F]+)')
    def extractInstruction(self, line):
        instr_pattern = self.instr_pattern_c_sail
        re_search = instr_pattern.search(line)
        if re_search is not None:
            return int(re_search.group('instr'), 16),re_search.group('mnemonic'),re_search.group('mode')
        else:
            return None, None, None

    def extractAddress(self, line):
        instr_pattern = self.instr_pattern_c_sail
        re_search = instr_pattern.search(line)
        if re_search is not None:
            return int(re_search.group('addr'), 16)
        else:
            return 0

    def extractRegisterCommitVal(self, line):
        instr_pattern = self.instr_pattern_c_sail_regt_reg_val
        re_search = instr_pattern.search(line)
        if re_search is not None:
            rtype = re_search.group('regt')
            cval = re_search.group('val')
            if rtype =='f' and self.arch[1] == 32:
                cval = cval[0:2]+cval[-8:]
            return (rtype, re_search.group('reg'), cval)
        else:
            return None

    def extractCsrCommitVal(self, line):
        instr_pattern = self.instr_pattern_c_sail_csr_reg_val
        csr_commit = re.findall(instr_pattern,line)
        if (len(csr_commit)==0):
            return None
        else:
            return csr_commit

    def extractVirtualMemory(self, line):
        mem_r_pattern = re.compile(r'mem\[R,([0-9xABCDEF]+)\] -> 0x([0-9xABCDEF]+)')
        mem_x_pattern = re.compile(r'mem\[X,([0-9xABCDEF]+)\] -> 0x([0-9xABCDEF]+)')
        mem_depa_pattern = re.compile(r'mem\[([0-9xABCDEF]+)\]')

        match_search_mnemonic = self.instr_pattern_c_sail.search(line)
        depa, ieva, ieva_align, depa_align, iepa, iepa_align = None, None, None, None, None, None
        iptw_list, dptw_list = [], []
        return_dict = {}

        if match_search_mnemonic:
            iepa_align, ieva_align = 0, 0
            line_upper_part, line_lower_part = line.split(match_search_mnemonic.group(0), 1)

            iepa_list=(mem_x_pattern.findall(line_upper_part))
            if len(iepa_list) != 0:
                iepa = int(iepa_list[0][0], 16)

            ieva = int(match_search_mnemonic.group('addr'),16)
            iptw_list=(mem_r_pattern.findall(line_upper_part))
            dptw_list=(mem_r_pattern.findall(line_lower_part))

            if dptw_list is not None:
                if "lw" in match_search_mnemonic.group('mnemonic'):
                    depa_list=dptw_list.pop()
                    depa=int(depa_list[0],16)
                else:
                    depa_list=mem_depa_pattern.findall(line_lower_part)
                    if len(depa_list) != 0:
                        depa=int(depa_list[0],16)

            ieva_align = 1 if ieva is not None and ieva & 0b11 == 0 else 0
            iepa_align = 1 if iepa is not None and iepa & 0b11 == 0 else 0
            depa_align = 1 if depa is not None and depa & 0b11 == 0 else 0

        return_dict['dptw_list']  = dptw_list
        return_dict['iptw_list']  = iptw_list
        return_dict['depa']       = depa
        return_dict['ieva']       = ieva
        return_dict['iepa']       = iepa
        return_dict['ieva_align'] = ieva_align
        return_dict['iepa_align'] = iepa_align
        return_dict['depa_align'] = depa_align

        return (return_dict)

    def extractMemVal(self, line):
        instr_pattern = self.instr_pattern_c_sail_mem_val
        mem_val = re.findall(instr_pattern, line)
        if(len(mem_val) == 0):
            return None
        else:
            return mem_val
    
    def extracttrapvals(self, line):
        instr_trap_pattern = self.instr_pattern_c_sail_trap.search(line)
        trap_dict = {"mode_change": None, "call_type": None, "exc_num": None, "tval": None}

        if instr_trap_pattern:
            trap_dict["mode_change"] = instr_trap_pattern.group("mode_change")
            trap_dict["call_type"]   = instr_trap_pattern.group("call_type")
            trap_dict["exc_num"]     = instr_trap_pattern.group("exc_num")
            trap_dict["tval"]        = instr_trap_pattern.group("tval")

        return trap_dict

    @plugins.parserHookImpl
    def __iter__(self):
        with open(self.trace) as fp:
            content = fp.read()
        instructions = content.split('\n\n')
        for line in instructions:
            instr, mnemonic, mode = self.extractInstruction(line)
            addr = self.extractAddress(line)
            reg_commit = self.extractRegisterCommitVal(line)
            csr_commit = self.extractCsrCommitVal(line)
            vm_addr_dict = self.extractVirtualMemory(line)
            mem_val = self.extractMemVal(line)
            trap_dict = self.extracttrapvals(line)
            instrObj = instructionObject(instr, 'None', addr, reg_commit = reg_commit, csr_commit = csr_commit, mnemonic = mnemonic, mode = mode, vm_addr_dict = vm_addr_dict, mem_val = mem_val, trap_dict = trap_dict)
            yield instrObj
