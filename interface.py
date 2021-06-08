
import importlib
import pluggy
from riscv_isac.plugins.specification import *
import riscv_isac.plugins as plugins
# import specification as spec

def interface (trace, arch, mode):
    parser_pm = pluggy.PluginManager("parser")
    decoder_pm = pluggy.PluginManager("decoder")
    parser_pm.add_hookspecs(ParserSpec)
    decoder_pm.add_hookspecs(DecoderSpec)

    parserfile = importlib.import_module("riscv_isac.plugins.newparser_"+mode) # Parser file
    parserclass = getattr(parserfile, "mode_"+mode) # Class
    parser_pm.register(parserclass())
    parser = parser_pm.hook
    parser.setup(trace=trace,arch=arch)

    instructionObjectfile = importlib.import_module("riscv_isac.plugins.newInstruction_plugin") # Instruction file
    decoderclass = getattr(instructionObjectfile, "Plugin_dp")  # Instruction Class
    decoder_pm.register(decoderclass())
    decoder = decoder_pm.hook
    decoder.setup(arch=arch)

    iterator = iter(parser.__iter__()[0])

    for instr, mnemonic, addr, commitvalue in iterator: # Instrcution_stream yields the given values.
        if instr is not None:
            instrObj = decoder.decode(instr=instr, addr=addr) # decode is a fn in Instruction class that returns an InstrObj for given instr, addr.


    # parserfile = importlib.import_module("newparser_"+mode) # Parser file
    # parserclass = getattr(parserfile, "mode_"+mode)(trace, arch) # Class

    # instructionObjectfile = importlib.import_module("newInstruction_plugin") # Instruction file
    # decoder = getattr(instructionObjectfile, "Plugin_dp")(arch)  # Instruction Class

    # for instr, mnemonic, addr, commitvalue in parserclass.instruction_stream(): # Instrcution_stream yields the given values.
    #     instrObj = decoder.decode(instr, addr) # decode is a fn in Instruction class that returns an InstrObj for given instr, addr.

log_file_path = "/home/sharder/git/incoresemi/riscof/riscof_work/misalign-beq-01.S/misalign-beq-01.log"
# trace = open(log_file_path,"r")

interface(log_file_path, "rv32i","c_sail")



