# See LICENSE.incore for details

import os

root = os.path.abspath(os.path.dirname(__file__))

cwd = os.getcwd()

dpr_template = '''
## Data Propagation Report

| Param                     | Value    |
|---------------------------|----------|
| XLEN                      | {0}      |
| TEST_REGION               | {1}      |
| SIG_REGION                | {2}      |
| COV_LABELS                | {3}      |
| TEST_NAME                 | {4}.S    |
| Total Unique Coverpoints  | {5}      |
| Total Signature Updates   | {6}      |
| Ops w/o unique coverpoints | {7}      |
| Sig Updates w/o Coverpoints | {8}    |

## Report Table

- The first column indicates the signature address and the data at that location in hexadecimal in the following format: 
  ```
  [Address]
  Data
  ```

- The second column captures all the coverpoints which have been captured by that particular signature location

- The third column captures all the insrtuctions since the time a coverpoint was
  hit to the point when a store to the signature was performed. Each line has
  the following format:
  ```
  [PC of instruction] : mnemonic
  ```

'''
