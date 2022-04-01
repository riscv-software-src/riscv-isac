========================
rvopcodesdecoder Plugin
========================

`rvopcodesdecoder` is a disassembler for the RISCV-ISAC. It is a decoder plugin dependent on the `riscv/riscv-opcodes <https://github.com/riscv/riscv-opcodes>`_ repository. The decoder is implemented in ``riscv_isac/plugins/rvopcodesdecoder.py`` file. 

Usage
~~~~~
`rvopcodesdecoder` uses files from ``riscv/riscv-opcodes`` repository to parse and generate datastructures
to support the decoder. Manually, these files should be checked into ``riscv_isac/plugins/riscv_opcodes`` directory.
This process is automated using the ``setup`` command of `riscv_isac`: ::
  
  riscv_isac setup

The above operation, by default clones the ``riscv/riscv-opcodes`` into ``riscv_isac/plugins/riscv_opcodes`` 

In order to clone into a different version of ``riscv_opcodes``, ``--url`` option can be used to enter the url of the
particular version.::

  rirscv_isac setup --url https://github.com/riscv/riscv-opcodes/tree/master

To use `rvopcodesdecoder` for coverage computation in RISCV-ISAC, ``rvopcodesdecoder`` should be supplied as argument for ``--decoder-name`` option. For example, ::

  riscv_isac --verbose info coverage -d -t trace.log --parser-name spike --decoder-name rvopcodesdecoder -o coverage.rpt --sig-label main _end --test-label   main _end -e add-01.out -c dataset.cgf -x 64

Plugin Implementation
~~~~~~~~~~~~~~~~~~~~~
The riscvopcodesdecoder module implements ``setup`` and ``decode`` methods for the decoder plugin.

Setup
*************
The setup function gathers all the necessary files and creates a nested dictionary by calling ``create_inst_dict`` which facilitates decoding of machine code instructions hierarchically

.. code-block:: python

    @plugins.decoderHookImpl
    def setup(self, arch: str):
      self.arch = arch
      # Create nested dictionary
      nested_dict = lambda: defaultdict(nested_dict)
      rvOpcodesDecoder.INST_DICT = nested_dict()
      rvOpcodesDecoder.create_inst_dict('*')

Decoder
*******
The ``decode`` method takes the instruction stored in an ``instructionOjbect`` and decodes the name and arguments associated with the instruction. The ``get_instr()`` method traverses through the dictionary tree recursively till it fetches the required instruction name and arguments.

.. code-block:: python    
  
    @plugins.decoderHookImpl
    def decode(self, temp_instrobj: instructionObject):

        mcode = temp_instrobj.instr
        name_args = rvOpcodesDecoder.get_instr(rvOpcodesDecoder.INST_DICT, mcode)

``riscv_isac/plugins/constants.py`` holds the necessary field position information to decode the arguments.
