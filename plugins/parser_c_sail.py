import re

instr_pattern_c_sail= re.compile(
        '\[\d*\]\s\[(.*?)\]:\s(?P<addr>[0-9xABCDEF]+)\s\((?P<instr>[0-9xABCDEF]+)\)\s*(?P<mnemonic>.*)')
instr_pattern_c_sail_regt_reg_val = re.compile('(?P<regt>[xf])(?P<reg>[\d]+)\s<-\s(?P<val>[0-9xABCDEF]+)')
''' Regex pattern and functions for extracting instruction and address '''


class class_c_sail():
        
        ## Extract instruction
        def extractInstruction(line):
            instr_pattern = instr_pattern_c_sail
            re_search = instr_pattern.search(line) 
            if re_search is not None:
                    return int(re_search.group('instr'), 16),re_search.group('mnemonic')
            else:
                return None, None
        
        ## Extract address
        def extractAddress(line):
            instr_pattern = instr_pattern_c_sail
            re_search = instr_pattern.search(line) 
            if re_search is not None:
                return int(re_search.group('addr'), 16)
            else:
                return 0 
        
        # Extract register commit value
        def extractRegisterCommitVal(line):
            instr_pattern = instr_pattern_c_sail_regt_reg_val
            re_search = instr_pattern.search(line)
            if re_search is not None:
                return (re_search.group('regt'), re_search.group('reg'), re_search.group('val'))
            else:
                return None

