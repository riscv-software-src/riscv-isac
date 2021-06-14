import re
import riscv_isac.plugins as plugins
import riscv_isac.plugins. specification as spec

class c_sail(spec.ParserSpec):

    @plugins.parserHookImpl
    def setup(self, trace, arch):
        self.trace = trace
        self.arch = arch

    instr_pattern_c_sail= re.compile(
        '\[\d*\]\s\[(.*?)\]:\s(?P<addr>[0-9xABCDEF]+)\s\((?P<instr>[0-9xABCDEF]+)\)\s*(?P<mnemonic>.*)')
    instr_pattern_c_sail_regt_reg_val = re.compile('(?P<regt>[xf])(?P<reg>[\d]+)\s<-\s(?P<val>[0-9xABCDEF]+)')

    def extractInstruction(self, line):
        instr_pattern = self.instr_pattern_c_sail
        re_search = instr_pattern.search(line)
        if re_search is not None:
                return int(re_search.group('instr'), 16),re_search.group('mnemonic')
        else:
            return None, None

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
            return (re_search.group('regt'), re_search.group('reg'), re_search.group('val'))
        else:
            return None

    @plugins.parserHookImpl
    def __iter__(self):
        with open(self.trace) as fp:
            content = fp.read()
        instructions = content.split('\n\n')
        for line in instructions:
            instr, mnemonic = self.extractInstruction(line)
            addr = self.extractAddress(line)
            commitvalue = self.extractRegisterCommitVal(line)
            yield instr, mnemonic, addr, commitvalue
