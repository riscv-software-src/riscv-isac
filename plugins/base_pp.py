## Plugin_model : Plug in for execution traces from the different RISC-V models

## base_pp.py => Base for parser plugins. sub_classes -> for different models
import os
import core    ## For accessing the variables of core file

Modes = {}

class Plugin_models(object):
  pass

def init_plugin_m():

    ##find_plugin(); ## Explicitly hard-coding

    ## Create subclasses:
    class mode_spike(Plugin_models):
        mode = 'spike'

        ## Extract instruction
        def extractInstruction(line, mode = 'standard'):
            instr_pattern = core.instr_pattern_spike
            re_search = instr_pattern.search(core.line)  ## Check this (where is line coming from)......
            if re_search is not None:
                return int(re_search.group('instr'), 16), None
            else:
                return None, None
        
        ## Extract address
        def extractAddress(line, mode = 'standard'):
            instr_pattern = core.instr_pattern_spike
            re_search = instr_pattern.search(core.line)  ## Check this......
            if re_search is not None:
                return int(re_search.group('addr'), 16)
            else:
                return 0
        
        # Extract register commit value
        def extractRegisterCommitVal(line, mode):

            instr_pattern = core.instr_pattern_spike_xd
            re_search = instr_pattern.search(line)
            if re_search is not None:
                return (re_search.group('regt'), re_search.group('reg'), re_search.group('val'))
            else:
                return None

    class mode_sail(Plugin_models):
        mode = 'c_sail'

        ## Extract instruction
        def extractInstruction(line, mode = 'standard'):
            instr_pattern = core.instr_pattern_c_sail
            re_search = instr_pattern.search(core.line)  ## Check this..... 
            if re_search is not None:
                    return int(re_search.group('instr'), 16),re_search.group('mnemonic')
            else:
                return None, None
        
        ## Extract address
        def extractAddress(line, mode = 'standard'):
            instr_pattern = core.instr_pattern_c_sail
            re_search = instr_pattern.search(core.line)  ## Check this..... 
            if re_search is not None:
                return int(re_search.group('addr'), 16)
            else:
                return 0 
        
        # Extract register commit value
        def extractRegisterCommitVal(line, mode):
            instr_pattern = core.extractOpcodeinstr_pattern_c_sail_regt_reg_val
            re_search = instr_pattern.search(line)
            if re_search is not None:
                return (re_search.group('regt'), re_search.group('reg'), re_search.group('val'))
            else:
                return None
    
    class mode_standard(Plugin_models):
        mode = 'standard'

        ## Extract instruction
        def extractInstruction(line, mode = 'standard'):
            instr_pattern = core.instr_pattern_standard
            re_search = instr_pattern.search(core.line)
            if re_search is not None:
                return int(re_search.group('instr'), 16), None
            else:
                return None, None
        
        ## Extract address
        def extractAddress(line, mode = 'standard'):
            instr_pattern = core.instr_pattern_standard
            re_search = instr_pattern.search(core.line)
            if re_search is not None:
                return int(re_search.group('addr'), 16)
            else:
                return 0

    create_dict()
    

## Create dictionary
def create_dict():
    for plugin in Plugin_models.__subclasses__():
        Modes[plugin.mode] = plugin


  
