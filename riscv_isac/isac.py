# See LICENSE.incore file for details
import sys
import os
import shutil
import yaml

from riscv_isac.log import *
from riscv_isac.utils import *
from riscv_isac.constants import *
from riscv_isac.__init__ import __version__

def isac(verbose, dir, clean):

    logger.level(verbose)
    logger.info('****** RISC-V ISA Coverage {0} *******'.format(__version__ ))
    logger.info('Copyright (c) 2020, InCore Semiconductors Pvt. Ltd.')
    logger.info('All Rights Reserved.')
    
