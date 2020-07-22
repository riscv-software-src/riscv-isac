# See LICENSE.incore file for details
from riscv_isac.log import logger
import riscv_isac.utils as utils
import riscv_isac.coverage as cov
from elftools.elf.elffile import ELFFile

def isac(output_file,elf ,trace_file, cgf_file, mode, merge_cov, detailed, startlabel, endlabel, dump):
    start_address = None
    end_address = None
    if elf is not None and startlabel is not None and \
            endlabel is not None:
        start_address = utils.collect_label_address(elf, startlabel)
        end_address = utils.collect_label_address(elf, endlabel)
        logger.info('Start Region Label: ' + startlabel + ' @ ' +
                str(start_address))
        logger.info('End Region Label  : ' + endlabel + ' @ ' +
                str(end_address))
    rpt = cov.compute(trace_file, cgf_file, mode, \
            merge_cov, detailed, 32, start_address, end_address, dump)
    if output_file is None:
        logger.info('Coverage Report:')
        logger.info('\n\n' + rpt)
    else:
        rpt_file = open(output_file,'w')
        rpt_file.write(rpt)
        rpt_file.close()
        logger.info('Report File Generated : ' + str(output_file))
