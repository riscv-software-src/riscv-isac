Parallelized coverage calculation
=================================

Coverage computation in ISAC is an iterative process where all coverpoints
are evaluated for every instruction. This causes an exponential increase in coverage
computation time as the number of coverage increases. To improve the performance of 
ISAC, coverage computation is parallelized.

Parallelization of coverage computation is achieved by the parallelization of ``compute_per_line()``
method in ``coverage.py`` file. The implementation resorts to use of queues to relay statistics of hit
coverpoint back to the main process.

Usage
~~~~~
The number of processes to be spawned for coverage computation can be provided using
``--procs`` or ``-p`` option while running ISAC. As an example, ::
    
    riscv_isac --verbose info coverage -d -t add-01.log --parser-name c_sail --decoder-name internaldecoder -o coverage.rpt --sig-label begin_signature end_signature --test-label rvtest_code_begin rvtest_code_end -e add-01.elf -c dataset.cgf -c rv32i.cgf -x 32 -l add --procs 3

The default number of processes spawned is 1
