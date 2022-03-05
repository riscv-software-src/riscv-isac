import os
import click
from git import Repo

import riscv_isac.plugins as plugins

# Path to riscv-opcodes
path_to_opcodes = ''

@click.group()
@click.option('--setup', 
                is_flag=True,
                help='Setup decoder from riscv-opcodes')
def cli(setup):
    pass

@cli.command(help = 'URL to the riscv-opcodes github repo')
@click.option('--url',
                type = str,
                default='https://github.com/incoresemi/riscv-opcodes',
                required=False)
def clone(url):
    Repo.clone_from(url, './riscv-opcodes/')
    path_to_opcodes = os.getcwd() + '/riscv-opcodes/'
    print(path_to_opcodes)

# Temporary CLI command to clean the cloned repo 
@cli.command(help = 'Clean cloned repo')
@click.option('--clean',
                default='./riscv-opcodes')
def clean(clean):
    os.system('rm -r -f ' + clean)

#  Disassembler implementation
class rvopcodes_decoder:
    '''
    This class implements the decoder plugin
    '''
    @plugins.decoderHookImpl
    def setup(self, arch):
        self.arch = arch
    
    @plugins.decoderHookImpl
    def decoder(self, instrObj_temp):
        pass
    

if __name__ == '__main__':
    cli()