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

    parserfile = importlib.import_module(abs_location_module) 
    plugin_class = "mode"+ trace_format
    parserclass = getattr(parserfile, plugin_class) 
    parser_pm.register(parserclass())
    parser = parser_pm.hook
    parser.setup(trace = execution_trace_file_path, arch = arch)
    
Here ``abs_location_module`` contains the absolute file path of parser plugin, ``trace_fromat`` contains the name of the RISC-V model of exection trace file. ``parser`` plugin is setup with ``arch`` containing the architecture of the set and ``execution_trace_file_path`` containing the absolute path of the trace file.

2. The decoder plugin can be plugged-in using the following template code:

.. code-block:: python

    instructionObjectfile = importlib.import_module(abs_location_module)
    decoderclass = getattr(instructionObjectfile, plugin_class) 
    decoder_pm.register(decoderclass())
    decoder = decoder_pm.hook
    decoder.setup(arch=arch)
    
Here ``abs_location_module`` contains the absolute file path of instruction plugin and ``plugin_class`` contains the class name. ``decoder`` is initialized with ``arch`` which is the architecture of the instruction set.

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
