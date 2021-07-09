# See LICENSE.incore for details
"""Console script for riscv_isac."""

import click

from riscv_isac.isac import isac
from riscv_isac.__init__ import __version__
from riscv_isac.log import logger
import riscv_isac.utils as utils
from riscv_isac.cgf_normalize import *
import riscv_isac.coverage as cov

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
        '--cgf-file','-c',multiple=True,
        type=click.Path(resolve_path=True,readable=True,exists=True),
        help="Coverage Group File(s). Multiple allowed.",required=True
    )
@click.option(
        '--detailed', '-d',
        is_flag=True,
        help='Select detailed mode of  coverage printing')

@click.option(
        '--parser-name',
        type = str,
        default = 'c_sail',
        metavar = 'NAME',
        help='Parser plugin name'
    )

@click.option(
        '--decoder-name',
        type = str,
        default = 'internaldecoder',
        metavar = 'NAME',
        help = 'Decoder plugin name'
    )

@click.option(
        '--parser-path',
        type=click.Path(resolve_path=True,readable=True,exists=True),
        help="Parser file path"
    )

@click.option(
        '--decoder-path',
        type=click.Path(resolve_path=True,readable=True,exists=True),
        help="Decoder file path"
    )

@click.option(
        '--output-file','-o',
        type=click.Path(writable=True,resolve_path=True),
        help="Coverage Group File"
    )
@click.option(
        '--test-label',
        type=(str,str),
        multiple=True,
        metavar='LABEL_START LABEL_END',
        default=None,
        help='Pair of labels denoting start and end points of the test region(s). Multiple allowed.'
    )
@click.option(
        '--sig-label',
        type=(str,str),
        multiple=True,
        metavar='LABEL_START LABEL_END',
        default=None,
        help='Pair of labels denoting start and end points of the signature region(s). Multiple allowed.'
    )
@click.option(
        '--dump',
        type=click.Path(writable=True,resolve_path=True),
        help="Dump Normalized Coverage Group File"
    )
@click.option(
        '--cov-label','-l',
        metavar='COVERAGE LABEL',
        type=str,
        multiple=True,
        help = "Coverage labels to consider for this run."
)
@click.option('--xlen','-x',type=click.Choice(['32','64']),default='32',help="XLEN value for the ISA.")
def coverage(elf,trace_file,cgf_file,detailed,parser_name, decoder_name, parser_path, decoder_path,output_file, test_label,
        sig_label, dump,cov_label, xlen):
    isac(output_file,elf,trace_file, expand_cgf(cgf_file,int(xlen)), parser_name, decoder_name, parser_path, decoder_path, detailed, test_label,
            sig_label, dump, cov_label, int(xlen))



@cli.command(help = "Merge given coverage files.")
@click.argument(
        'files',
        type=click.Path(resolve_path=True,readable=True,exists=True),
        nargs=-1
        )
@click.option(
        '--detailed', '-d',
        is_flag=True,
        help='Select detailed mode of  coverage printing')
@click.option(
        '-p',
        type = int,
        default = 1,
        help='Number of processes'
        )
@click.option(
        '--cgf-file','-c',multiple=True,
        type=click.Path(resolve_path=True,readable=True,exists=True),
        help="Coverage Group File(s). Multiple allowed.",required=True
    )
@click.option(
        '--output-file','-o',
        type=click.Path(writable=True,resolve_path=True),
        help="Coverage Group File."
    )
@click.option('--xlen','-x',type=click.Choice(['32','64']),default='32',help="XLEN value for the ISA.")
def merge(files,detailed,p,cgf_file,output_file,xlen):
    rpt = cov.merge_coverage(files,expand_cgf(cgf_file,int(xlen)),detailed,int(xlen),p)
    if output_file is None:
        logger.info('Coverage Report:')
        logger.info('\n\n' + rpt)
    else:
        rpt_file = open(output_file,'w')
        utils.dump_yaml(rpt,rpt_file)
        rpt_file.close()
        logger.info('Report File Generated : ' + str(output_file))



@cli.command(help = "Normalize the cgf.")
@click.option(
        '--cgf-file','-c',multiple=True,
        type=click.Path(resolve_path=True,readable=True,exists=True),
        help="Coverage Group File(s). Multiple allowed.",required=True
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
        utils.dump_yaml(expand_cgf(cgf_file,int(xlen)),outfile)


