
import re
from riscv_isac.log import logger
import riscv_isac.plugins as plugins

class mode_spike():

    @plugins.parserHookImpl
    def setup(self, trace, arch):
        self.trace = trace
        self.arch = arch

    instr_pattern_spike = re.compile(
        '[0-9]\s(?P<addr>[0-9abcdefx]+)\s\((?P<instr>[0-9abcdefx]+)\)')
    instr_pattern_spike_xd = re.compile(
        '[0-9]\s(?P<addr>[0-9abcdefx]+)\s\((?P<instr>[0-9abcdefx]+)\)' +
        '\s(?P<regt>[xf])(?P<reg>[\s|\d]\d)\s(?P<val>[0-9abcdefx]+)'
        )

    ## Extract instruction
    def extractInstruction(self, line):
        instr_pattern = self.instr_pattern_spike
        re_search = instr_pattern.search(line)
        if re_search is not None:
            return int(re_search.group('instr'), 16), None
        else:
            return None, None

    ## Extract address
    def extractAddress(self, line):
        instr_pattern = self.instr_pattern_spike
        re_search = instr_pattern.search(line)
        if re_search is not None:
            return int(re_search.group('addr'), 16)
        else:
            return 0

    # Extract register commit value
    def extractRegisterCommitVal(self, line):

        instr_pattern = self.instr_pattern_spike_xd
        re_search = instr_pattern.search(line)
        if re_search is not None:
            return (re_search.group('regt'), re_search.group('reg'), re_search.group('val'))
        else:
            return None

    @plugins.parserHookImpl
    def instruction_stream(self):
        with open(self.trace) as fp:
            for line in fp:
                logger.debug('parsing ' + str(line))
                instr, mnemonic = self.extractInstruction(line)
                addr = self.extractAddress(line)
                commitvalue = self.extractRegisterCommitVal(line)
                yield instr, mnemonic, addr, commitvalue
