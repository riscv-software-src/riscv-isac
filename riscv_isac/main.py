# See LICENSE.incore for details
"""Console script for riscv_isac."""

import click

from riscv_isac.isac import isac
from riscv_isac.__init__ import __version__
from riscv_isac.log import logger
import riscv_isac.utils as utils
from riscv_isac.cgf_normalize import *

@click.group()
@click.version_option(prog_name="RISC-V ISA Coverage Generator",version=__version__)
@click.option('--verbose', '-v', default='info', help='Set verbose level', type=click.Choice(['info','error','debug'],case_sensitive=False))
def cli(verbose):
    logger.level(verbose)
    logger.info('****** RISC-V ISA Coverage {0} *******'.format(__version__ ))
    logger.info('Copyright (c) 2020, InCore Semiconductors Pvt. Ltd.')
    logger.info('All Rights Reserved.')

@cli.command(help = "Run Coverage analysis on tracefile.")
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
        '--dump',
        type=click.Path(writable=True,resolve_path=True),
        help="Expanded CGF"
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
def coverage(elf,trace_file,cgf_file,merge_cov,detailed,mode,output_file,startlabel,endlabel,dump):
    isac(output_file,elf,trace_file, cgf_file, mode, merge_cov, detailed,startlabel, endlabel, dump)

@cli.command(help = "Merge given coverage files.")
def merge():
    pass

@cli.command(help = "Normalize the cgf.")
@click.option(
        '--cgf-file','-c',
        type=click.Path(resolve_path=True,readable=True,exists=True),
        help="Coverage Group File",required=True
    )
@click.option(
        '--output-file','-o',
        type=click.Path(writable=True,resolve_path=True),
        help="Coverage Group File",
        required = True
    )
@click.option('--xlen','-x',type=click.Choice(['32','64']),default='32',help="XLEN value for the ISA.")
def normalize(cgf_file,output_file,xlen):
    logger.info("Writing normalized CGF to "+str(output_file))
    with open(output_file,"w") as outfile:
        utils.yaml.dump(expand_cgf(utils.load_yaml(cgf_file),int(xlen)),outfile)
