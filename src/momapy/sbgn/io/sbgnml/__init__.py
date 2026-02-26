"""Classes for reading and writing SBGN-ML files."""

import sys

import momapy.sbgn.io.sbgnml._reader
import momapy.sbgn.io.sbgnml._writer

# Re-export public classes via sys.modules since the package attribute
# chain is not yet available during __init__.py execution.
_reader_mod = sys.modules["momapy.sbgn.io.sbgnml._reader"]
_writer_mod = sys.modules["momapy.sbgn.io.sbgnml._writer"]

SBGNML0_2Reader = _reader_mod.SBGNML0_2Reader
SBGNML0_3Reader = _reader_mod.SBGNML0_3Reader
SBGNML0_3Writer = _writer_mod.SBGNML0_3Writer
