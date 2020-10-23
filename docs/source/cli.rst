.. See LICENSE.incore for details

=====
Usage
=====

CLI
===

Once you have RISCV-ISAC installed, executing ``riscv_isac --help`` should print the following on the terminal. ::

   Options:
      --version                       Show the version and exit.
      -v, --verbose [info|error|debug]
                                      Set verbose level
      --help                          Show this message and exit.
    
   Commands:
     coverage   Run Coverage analysis on tracefile.
     merge      Merge given coverage files.
     normalize  Normalize the cgf.  

Help text for each command can be accessed by executing ``riscv_isac <command> --help``

* Coverage ::
    
    Usage: riscv_isac coverage [OPTIONS]
    
      Run Coverage analysis on tracefile.
    
    Options:
      -e, --elf PATH                  ELF file
      -t, --trace-file PATH           Instruction trace file to be analyzed
      -c, --cgf-file PATH             Coverage Group File  [required]
      -d, --detailed                  Select detailed mode of  coverage printing
      --mode [standard|spike|c_sail]  Select mode of trace file input.
      -o, --output-file PATH          Coverage Group File
      --test-label LABEL_START LABEL_END
                                      Pair of labels denoting start and end
                                      points. Multiple allowed.
    
      --dump PATH                     Dump Normalized Coverage Group File
      -l, --cov-label COVERAGE LABEL  Coverage labels to consider for this run.
      -x, --xlen [32|64]              XLEN value for the ISA.
      --help                          Show this message and exit. 

* Merge :: 

    Usage: riscv_isac merge [OPTIONS] [FILES]...
    
      Merge given coverage files.
    
    Options:
      -d, --detailed          Select detailed mode of  coverage printing
      -c, --cgf-file PATH     Coverage Group File  [required]
      -o, --output-file PATH  Coverage Group File.
      --help                  Show this message and exit.

* Normalize ::

    Usage: riscv_isac normalize [OPTIONS]
    
      Normalize the cgf.
    
    Options:
      -c, --cgf-file PATH     Coverage Group File  [required]
      -o, --output-file PATH  Coverage Group File  [required]
      -x, --xlen [32|64]      XLEN value for the ISA.
      --help                  Show this message and exit.


Other Projects
==============
To use RISC-V ISA Coverage in a project::

    import riscv_isac


