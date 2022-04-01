========================
rvopcodesdecoder Plugin
========================

``rvopcodesdecoder`` is a disassembler for the RISCV-ISAC. It is a decoder plugin dependent 
on the `riscv/riscv-opcodes <https://github.com/riscv/riscv-opcodes>`_ repository.

Usage
~~~~~
``rvopcodesdecoder`` uses files from ``riscv/riscv-opcodes`` to parse and generate datastructures
to support the decoder. Manually, these files should be checked into ``riscv_isac/plugins/riscv_opcodes`` directory.
This process is automated using the ``setup`` command of ``riscv_isac`` like this: 

``riscv_isac setup``

The above operation, by default clones the ``riscv/riscv-opcodes`` into ``riscv_isac/plugins/riscv_opcodes`` 

In order to clone into a different version of ``riscv_opcodes``, ``--url`` option can be used to enter the url to the
particular version.

``rirscv_isac setup --url https://github.com/riscv/riscv-opcodes/tree/master``

To use ``rvopcodesdecoder`` for coverage computation using RISCV-ISAC, ``rvopcodesdecoder`` should be used for ``--decoder-name`` option. For example,

``riscv_isac --verbose info coverage -d -t trace.log --parser-name spike --decoder-name rvopcodesdecoder -o coverage.rpt --sig-label main _end --test-label main _end -e a.out -c dataset.cgf -x 64``

Plugin Implementation
~~~~~~~~~~~~~~~~~~~~~
The ``riscvopcodesdecoder`` implements ``setup`` and ``decode`` methods which implements the decoder plugin. The setup
function gathers all the necessary files and creates a nested dictionary which facilitates decoding of machine code instructions hierarchically. 