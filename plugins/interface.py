
import importlib

def interface (trace, arch, mode):
    parserfile = importlib.import_module("newparser_"+mode) # Parser file
    parserclass = getattr(parserfile, "mode_"+mode)(trace, arch) # Class

    instructionObjectfile = importlib.import_module("newInstruction_plugin") # Instruction file
    decoder = getattr(instructionObjectfile, "Plugin_dp")(arch)  # Instruction Class 

    for instr, mnemonic, addr, commitvalue in parserclass.instruction_stream(): # Instrcution_stream yields the given values.
        instrObj = decoder.decode(instr, addr) # decode is a fn in Instruction class that returns an InstrObj for given instr, addr.





