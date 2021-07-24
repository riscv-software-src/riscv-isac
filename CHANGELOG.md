# CHANGELOG

This project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.6.6] - 2021-07-23
- Minor corrections in Documentation

## [0.6.5] - 2021-07-14
- Bug fix for error while generating Data Propagation Report.

## [0.6.4] - 2021-07-08
- Added support for CSR coverage and its architectural state
- Updated the merge function to support multiprocessing 
- Added a parameter '-p' ( number of processes ) in merge command 
- Documentation update for CSR coverpoints
- Return value of parsers changed from 5 independent values (hexcode, addr, reg commmit, csr commit, mnemonics) to instruction object updated with these values
- Argument of decode and all decoding functions (in internaldecoder) changed from hexcode and addr to instruction object

## [0.6.3] - 2021-06-24
- Documentation updates to reflect plugin usage.
- Minor bug fixes in coverage reporting.
- Improved CLI help messages.

## [0.6.2] - 2021-06-15
- Added parser plugins for sail and spike 
- Added decoder plugin
- Added arguments in main.py for custom plugin paths and names.

## [0.6.1] - 2021-06-11
- Added initial support for F extension coverpoints based on IBM models.
- Added support for F extension architectural state
- Fixed author information and repo link in setup.py

## [0.6.0] - 2021-05-27
- added support in parsers for K-scalar crypto instructions
- added support for abstract functions: uniform random, byte-count, leading-ones, leading-zeros,
  trailing-ones, trailing-zeros
- now maintain a separate list of instructions which require unsigned interpretation of rs1 and rs2.
- restructured coverage report handling to preserve comments throughout processing and merging.
- switched yaml to a round-trip parser for preserving comments

## [0.5.2] - 2021-02-23
- Moved ci to github actions
- fixed links in docs

## [0.5.1] - 2020-12-14
- Fixed operand signedness for m ext ops.

## [0.5.0] - 2020-11-18
- added support to take multiple cgf files as input. The order matters
- added support for abstract function of special dataset 

## [0.4.0] - 2020-11-10
- added special data set for r-type instructions
- fixed data propagation report generation and templates
- using classes to manage architectural state and statistics
- updated docs

## [0.3.1] - 2020-10-26
  - use logger instead of log in coverage.py


## [0.3.0] - 2020-10-26
- Adding support for Data propagation report generation
- Added 'sig-label' as the new cli option under coverage to capture DP reports
- Added support in sail parsers to extract mnemonics also from the trace file
- added pytablewriter as part of the requirements

## [0.2.0] - 2020-10-23
- Added documentation for CGF and usage
- Added normalization routine as cli
- Added abstract functions
- using click for cli
- adding parsers for sail and spike
- added support for filtering based on labels
- added merge-reports cli command


## [0.1.0] - 2020-06-25
- initial draft
