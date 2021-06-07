
import importlib
import pluggy
import riscv_isac.plugins.specification as spec

def interface (trace, arch, mode):
    parser_pm = pluggy.PluginManager("parser")
    decoder_pm = pluggy.PluginManager("decoder")
    parser_pm.add_hookspecs(spec.ParserSpec)
    decoder_pm.add_hookspecs(spec.DecoderSpec)

    parserfile = importlib.import_module("newparser_"+mode) # Parser file
    parserclass = getattr(parserfile, "mode_"+mode) # Class
    parser_pm.register(parserclass)
    parser = (parser_pm.hook)(trace,arch)

    instructionObjectfile = importlib.import_module("newInstruction_plugin") # Instruction file
    decoderclass = getattr(instructionObjectfile, "Plugin_dp")  # Instruction Class
    decoder_pm.register(decoderclass)
    decoder = (decoder_pm.hook)(arch)

    for instr, mnemonic, addr, commitvalue in parser.instruction_stream(): # Instrcution_stream yields the given values.
        instrObj = decoder.decode(instr, addr) # decode is a fn in Instruction class that returns an InstrObj for given instr, addr.

    # parserfile = importlib.import_module("newparser_"+mode) # Parser file
    # parserclass = getattr(parserfile, "mode_"+mode)(trace, arch) # Class

    # instructionObjectfile = importlib.import_module("newInstruction_plugin") # Instruction file
    # decoder = getattr(instructionObjectfile, "Plugin_dp")(arch)  # Instruction Class

    # for instr, mnemonic, addr, commitvalue in parserclass.instruction_stream(): # Instrcution_stream yields the given values.
    #     instrObj = decoder.decode(instr, addr) # decode is a fn in Instruction class that returns an InstrObj for given instr, addr.





