"""CellDesigner writing context.

Holds the CellDesigner-specific writing state (subunit-to-complex index and
degraded-participant entries) layered on top of the shared
`momapy.io._utils.WritingContext`. Internal: not part of the public API.
"""

import dataclasses

from momapy.io._utils import WritingContext


@dataclasses.dataclass
class CellDesignerWritingContext(WritingContext):
    """Shared state for the writer.

    ``subunit_to_complex`` is keyed by ``id(species)`` because model
    species use ``compare=False`` on ``id_`` — two distinct species
    objects can be content-equal, and this index answers an identity
    question ("is *this* exact species a subunit of some complex?").
    The map being written holds strong references to every species for
    the duration of ``write()``, so ``id()`` addresses cannot be reused.

    The unique-id machinery (``element_to_xml_id``, ``used_xml_ids``)
    lives on the base ``WritingContext``; the former species-id memo and
    metaid set are subsumed by it.
    """

    subunit_to_complex: dict = dataclasses.field(default_factory=dict)
    degraded_entries: list = dataclasses.field(default_factory=list)
