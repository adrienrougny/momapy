"""IO subpackage for reading and writing maps.

Provides functions and registries for reading and writing molecular maps
in various formats (SBGN-ML, CellDesigner, SBML, etc.).

Examples:
    ```python
    from momapy.io import get_reader, get_writer
    reader = get_reader("sbgnml")
    writer = get_writer("sbgnml")
    ```
"""

from momapy.io.core import get_reader as get_reader
from momapy.io.core import get_writer as get_writer
from momapy.io.core import list_readers as list_readers
from momapy.io.core import list_writers as list_writers
from momapy.io.core import read as read
from momapy.io.core import reader_registry as reader_registry
from momapy.io.core import register_lazy_reader as register_lazy_reader
from momapy.io.core import register_lazy_writer as register_lazy_writer
from momapy.io.core import register_reader as register_reader
from momapy.io.core import register_writer as register_writer
from momapy.io.core import write as write
from momapy.io.core import writer_registry as writer_registry


__all__ = [
    "get_reader",
    "get_writer",
    "list_readers",
    "list_writers",
    "read",
    "reader_registry",
    "register_lazy_reader",
    "register_lazy_writer",
    "register_reader",
    "register_writer",
    "write",
    "writer_registry",
]


for name, import_path in [
    ("sbgnml", "momapy.sbgn.io.sbgnml.reader:SBGNML0_3Reader"),
    ("sbgnml-0.2", "momapy.sbgn.io.sbgnml.reader:SBGNML0_2Reader"),
    ("sbgnml-0.3", "momapy.sbgn.io.sbgnml.reader:SBGNML0_3Reader"),
    ("celldesigner", "momapy.celldesigner.io.celldesigner.reader:CellDesignerReader"),
    ("sbml", "momapy.sbml.io.sbml:SBMLReader"),
    ("pickle", "momapy.io.pickle:PickleReader"),
]:
    register_lazy_reader(name, import_path)

for name, import_path in [
    ("sbgnml", "momapy.sbgn.io.sbgnml.writer:SBGNML0_3Writer"),
    ("sbgnml-0.3", "momapy.sbgn.io.sbgnml.writer:SBGNML0_3Writer"),
    ("celldesigner", "momapy.celldesigner.io.celldesigner.writer:CellDesignerWriter"),
    ("pickle", "momapy.io.pickle:PickleWriter"),
]:
    register_lazy_writer(name, import_path)
