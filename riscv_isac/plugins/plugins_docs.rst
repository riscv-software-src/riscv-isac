================
Python Plugins:
================

RISC V-ISAC has python plugins for the following functions:

* Parse the execution trace file to yield instruction (code), mnemonics, address and register commit value for each instruction. Currently, there are plugins for execution traces from 2 RISC V models - SPIKE and SAIL.
* Decoding the information into a common instruction class object. 

Template Codes
===============

In order to use the plugins import riscv_isac.plugins.specifications.py module that contains the hook specifications.

1. The parser plugin can be plugged-in using the following template code:

.. code-block:: python

    parser_pm = pluggy.PluginManager("parser")
    parser_pm.add_hookspecs(ParserSpec)
    parserfile = importlib.import_module("riscv_isac.plugins.newparser_"+mode) 
    parserclass = getattr(parserfile, "mode_"+mode) 
    parser_pm.register(parserclass())
    parser = parser_pm.hook
    parser.setup(trace=trace_file,arch="rv"+str(xlen))
    
Here ``mode`` is the model of the trace file (spike/c_sail), HookSpecMarker is initialized with the name ``parser`` and ``ParserSpec`` is the hook specification.
The architecture is specified by ``arch``. ``parser`` is the instance of parserclass() which contains methods to extract the information.

2. The decoder plugin can be plugged-in using the following template code:

.. code-block:: python

    decoder_pm = pluggy.PluginManager("decoder")
    decoder_pm.add_hookspecs(DecoderSpec)
    instructionObjectfile = importlib.import_module("riscv_isac.plugins.newInstruction_plugin")
    decoderclass = getattr(instructionObjectfile, "Plugin_dp") 
    decoder_pm.register(decoderclass())
    decoder = decoder_pm.hook
    decoder.setup(arch="rv"+str(len))
    
HookSpecMarker is initialized with the name ``decoder`` and ``DecoderSpec`` is the hook specification. The architecture is specified by ``arch``. 
``decoder`` is an instance of decoderclass() which contains methods to decode the instruction and return a standard instruction object.

3. The parser plugin is iterable and yields information for each instruction of the trace file which can be extracted using iterators using the below template code:

.. code-block:: python

   iterator = iter(parser.__iter__()[0])
   for instr, mnemonic, addr, commitvalue in iterator:
   
Function Definitions
=====================

Class ParserSpec()
~~~~~~~~~~~~~~~~~~

def setup(self, trace, arch):
------------------------------

This function initializes each instance of ``parserclass()`` (a subclass of ``ParserSpec``) of a given mode with the path of the trace file (``trace``) and 
architecture of the instruction set (``arch``). 

.. code-block:: python

    @plugins.parserHookImpl
    def setup(self, trace, arch):
        self.trace = trace
        self.arch = arch

def  __iter__(self):
------------------------

It converts the instance of ``parserclass()`` to an iterator that generates instruction (``instr``), mnemonics (``mnemonic``), address (``addr``) and register commit value (``commitvalue``) on each
call. Thus, given an input trace file to the instance, this function will extract information from it line by line. An example is shown below from the c_sail parser.

.. code-block:: python

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
 
Class DecoderSpec()
~~~~~~~~~~~~~~~~~~~~~~~

def setup(self, arch):
------------------------------

This function initializes each instance of ``decoderclass()`` (a subclass of ``DecoderSpec``) with the argument-``arch`` architecture of the instruction set. 

.. code-block:: python

    @plugins.decoderHookImpl
    def setup(self, arch):
        self.arch = arch
        
def decode(self, instr, addr):
--------------------------------

This function takes in hexcode of instruction and address as arguments and returns the instruction object in the standard format - (instr_name, instr_addr, rd,
rs1, rs2, rs3, imm, csr, shamt)

.. code-block:: python

    @plugins.decoderHookImpl
    def decode(self, instr, addr):
        ''' Decodes the type of instruction
            Returns: instruction object
        '''
        first_two_bits = self.FIRST2_MASK & instr
        if first_two_bits == 0b11:
            return self.parseStandardInstruction(instr, addr, self.arch)
        else:
            return self.parseCompressedInstruction(instr, addr, self.arch)

``parseStandardInstruction`` and ``parseCompressedInstruction`` takes in the same aruguments along with the architecture of the instance and return the instruction object in the
above mentioned format.
