# See LICENSE.incore for details
"""Console script for riscv_isac."""

import click

from riscv_isac.isac import isac
from riscv_isac.__init__ import __version__
from riscv_isac.log import logger
@click.command()
@click.version_option(prog_name="RISC-V ISA Coverage Generator",version=__version__)
@click.option('--verbose', '-v', default='info', help='Set verbose level')
@click.option('--elf', '-e' , type=click.Path(exists=True,resolve_path=True),help="ELF file")
@click.option(
        '--trace-file','-t',
        type=click.Path(resolve_path=True,readable=True,exists=True),
        help="Instruction trace file to be analyzed"
    )

@click.option(
        '--cgf-file','-c',
        type=click.Path(resolve_path=True,readable=True,exists=True),
        help="Coverage Group File",required=True
    )

@click.option(
        '--merge_cov','-m',
        multiple=True,
        type=click.Path(resolve_path=True,readable=True,exists=True),
        help='Merge Coverage Reports. Provide the list of files to be merged.')

@click.option(
        '--detailed', '-d',
        is_flag=True,
        help='Select detailed mode of  coverage printing')

@click.option(
        '--mode',
        type=click.Choice(["standard","custom"],case_sensitive=False),
        default = 'standard',
        help='Select mode of trace file input.'
    )

@click.option(
        '--output-file','-o',
        type=click.Path(writable=True,resolve_path=True),
        help="Coverage Group File"
    )
@click.option(
        '--startlabel',
        type=str,
        metavar='NAME',
        default=None,
        help='Starting label of region'
    )
@click.option(
        '--endlabel',
        type=str,
        metavar='NAME',
        default=None,
        help='Ending label of region'
    )
def cli(verbose,elf,trace_file,cgf_file,merge_cov,detailed,mode,output_file,startlabel,endlabel):
    logger.level(verbose)
    logger.info('****** RISC-V ISA Coverage {0} *******'.format(__version__ ))
    logger.info('Copyright (c) 2020, InCore Semiconductors Pvt. Ltd.')
    logger.info('All Rights Reserved.')
    isac(output_file,elf,trace_file, cgf_file, mode, merge_cov, detailed, startlabel, endlabel)

