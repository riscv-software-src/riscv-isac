========================
Writing Your Own Plugins
========================

RISCV-ISAC uses the `pluggy <https://pluggy.readthedocs.io/en/latest/>`_ system for supporting plugins. The hooks are predefined and can be accessed by importing the ``riscv_isac.plugins`` module. The template for custom plugins is available :ref:`here.<Templates>`.

Two classes of plugins are defined, namely:

* Parser Plugin(``parserHookImpl``): Parse the execution trace file to yield instruction (code), mnemonics, address and register commit value for each instruction. Currently, there are plugins for execution traces from 2 RISC V models - SPIKE and SAIL.
* Decoder Plugin(``decoderHookImpl``): Decodes the information into a common instruction class object. 


Function Definitions
=====================

Parser Plugin
~~~~~~~~~~~~~~~~~~

def setup(self, trace, arch):
------------------------------

This function initializes each instance of ``parserclass()`` (a subclass of ``ParserSpec``) of a given mode. 

* Arguments: (``trace``) file path of the execution trace file and (``arch``) architecture of the set. 

.. code-block:: python

    @plugins.parserHookImpl
    def setup(self, trace, arch):
        self.trace = trace
        self.arch = arch

def  __iter__(self):
------------------------

It converts the instance of ``parserclass()`` to an iterator. Thus, given an input trace file to the instance, this function will extract information from it line by line. An example is shown below from the c_sail parser.

* Arguments: ``self`` instance of the class that contains the input trace file. 
* Returns: Generates instruction (``instr``), mnemonics (``mnemonic``), address (``addr``) and register commit value (``commitvalue``) on each
  call. 

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
 
Decoder Plugin
~~~~~~~~~~~~~~~~~~~~~~~

def setup(self, arch):
------------------------------

This function initializes each instance of ``decoderclass()`` (a subclass of ``DecoderSpec``).

* Arguments- ``self`` instance of the class and ``arch`` architecture of the instruction set

.. code-block:: python

    @plugins.decoderHookImpl
    def setup(self, arch):
        self.arch = arch
        
def decode(self, instr, addr):
--------------------------------

This function decodes the instruction and returns an instruction object ``riscv_isac.InstructionObject.instructionObject``.

* Arguments: ``self`` instance of the class, ``instr`` Hexcode of instruction and ``addr`` address.
* Return value:  The instruction object in the standard format - (instr_name, instr_addr, rd, rs1, rs2, rs3, imm, csr, shamt)

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

.. ``parseStandardInstruction`` and ``parseCompressedInstruction`` takes in the same arguments along with the architecture of the instance and return the instruction object in the
.. above mentioned format.


.. _Templates:

Templates
=========

Parser Plugin
~~~~~~~~~~~~~

.. code-block:: python
    
    import riscv_isac.plugins

    class CustomParser()
        
        @plugins.parserHookImpl
        def setup(self, trace, arch):
            self.trace = trace
            self.arch = arch

        @plugins.parserHookImpl
        def __iter__(self):
            #extract instruction, mnemonic, addr and commit value
            yield instr, mnemonic, addr, commitval

Decoder Plugin
~~~~~~~~~~~~~~

.. code-block:: python

    from riscv_isac.plugins import decoderHookImpl
    from riscv_isac.InstructionObject import instructionObject

    class CustomDecoder()

        @decoderHookImpl
        def setup(self, arch):
            self.arch = arch

        @decoderHookImpl
        def decode(self, instr, addr):
            # construct Instruction Object and return
