import pluggy

decoderHookSpec = pluggy.HookspecMarker("decoder")
parserHookSpec = pluggy.HookspecMarker("parser")

class DecoderSpec():
    @decoderHookSpec
    def __init__(self, arch):
        pass

    @decoderHookSpec
    def decode(self, instr, addr):
        pass

class ParserSpec():
    @parserHookSpec
    def __init__(self,trace,arch):
        pass

    @parserHookSpec
    def instruction_stream(self):
        pass
