import re

instr_pattern_spike = re.compile(
        '[0-9]\s(?P<addr>[0-9abcdefx]+)\s\((?P<instr>[0-9abcdefx]+)\)')
instr_pattern_spike_xd = re.compile(
        '[0-9]\s(?P<addr>[0-9abcdefx]+)\s\((?P<instr>[0-9abcdefx]+)\)' +
        '\s(?P<regt>[xf])(?P<reg>[\s|\d]\d)\s(?P<val>[0-9abcdefx]+)'
)

class class_spike():
        
        ## Extract instruction
        def extractInstruction(line):
            instr_pattern = instr_pattern_spike
            re_search = instr_pattern.search(line) 
            if re_search is not None:
                return int(re_search.group('instr'), 16), None
            else:
                return None, None
        
        ## Extract address
        def extractAddress(line):
            instr_pattern = instr_pattern_spike
            re_search = instr_pattern.search(line) 
            if re_search is not None:
                return int(re_search.group('addr'), 16)
            else:
                return 0
        
        # Extract register commit value
        def extractRegisterCommitVal(line):

            instr_pattern = instr_pattern_spike_xd
            re_search = instr_pattern.search(line)
            if re_search is not None:
                return (re_search.group('regt'), re_search.group('reg'), re_search.group('val'))
            else:
                return None