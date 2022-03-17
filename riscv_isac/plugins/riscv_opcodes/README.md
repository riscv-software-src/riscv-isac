# riscv-opcodes

This repo enumerates standard RISC-V instruction opcodes and control and
status registers.  It also contains a script to convert them into several
formats (C, Scala, LaTeX).

This repo is not meant to stand alone; it is a subcomponent of
[riscv-tools](https://github.com/riscv/riscv-tools) and assumes that it
is part of that directory structure.

## File Convention

1. `rv_x_y` - contains instructions common within the 32-bit and 64-bit modes when both x and y extensions are enabled (note in majority of the cases y will not exist).
2. `rv32_x_y` - contains instructions present in rv32xy only (absent in rv64X_Y eg. ???)
3. `rv64_x_y` - contains instructions present in rv64xy only (absent in rv32X_Y, eg. addw)
4. `_y` in the above is optional and can be null
5. for instructions present in multiple extensions, unless the spec allocates the instruction in a specific subset, the instruction encoding must be present in the first extension when canonically ordered. All other extensions can simply include a `$import prefix` followed by `<filename>` and `<instruction_name>` separate by `::` .  For e.g `pack` would be present in the `rv32_zbe` file as
`pack       rd rs1 rs2 31..25=4  14..12=4 6..2=0x0C 1..0=3` and `rv32_zbf` and `rv32_zbp` files would have the following entries : `$import rv32_zbe::pack`
6. For pseudo ops we use `$pseudo_op <filename>::<original instruction> <encoding description>` to indicate the original instruction that this pseudo op depends on and the pseudo instructions encoding in the entirety For e.g. the pseudo op `frflags` will be represented as `pseudo_op rv_zicsr::csrrs frflags rd 19..15=0 31..20=0x001 14..12=2 6..2=0x1C 1..0=3`
