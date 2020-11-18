CHANGELOG
=========

This project adheres to `Semantic Versioning <https://semver.org/spec/v2.0.0.html>`_.

[0.5.0] - 2020-11-18
  - added support to take multiple cgf files as input. The order matters
  - added support for abstract function of special dataset 

[0.4.0] - 2020-11-10
  - added special data set for r-type instructions
  - fixed data propagation report generation and templates
  - using classes to manage architectural state and statistics
  - updated docs

[0.3.1] - 2020-10-26
  - use logger instead of log in coverage.py


[0.3.0] - 2020-10-26
  - Adding support for Data propagation report generation
  - Added 'sig-label' as the new cli option under coverage to capture DP reports
  - Added support in sail parsers to extract mnemonics also from the trace file
  - added pytablewriter as part of the requirements

[0.2.0] - 2020-10-23
  - Added documentation for CGF and usage
  - Added normalization routine as cli
  - Added abstract functions
  - using click for cli
  - adding parsers for sail and spike
  - added support for filtering based on labels
  - added merge-reports cli command


[0.1.0] - 2020-06-25
  - initial draft
