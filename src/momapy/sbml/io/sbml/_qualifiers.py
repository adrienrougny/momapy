"""Qualifier mappings for SBML-based readers and writers.

This is the canonical location for qualifier mappings. SBGN-ML and
CellDesigner import from here.
"""

from momapy.sbml.model import BQBiol, BQModel


QUALIFIER_MEMBER_TO_QUALIFIER_ATTRIBUTE = {
    BQBiol.ENCODES: (
        "http://biomodels.net/biology-qualifiers/",
        "encodes",
    ),
    BQBiol.HAS_PART: (
        "http://biomodels.net/biology-qualifiers/",
        "hasPart",
    ),
    BQBiol.HAS_PROPERTY: (
        "http://biomodels.net/biology-qualifiers/",
        "hasProperty",
    ),
    BQBiol.HAS_VERSION: (
        "http://biomodels.net/biology-qualifiers/",
        "hasVersion",
    ),
    BQBiol.IS: (
        "http://biomodels.net/biology-qualifiers/",
        "is",
    ),
    BQBiol.IS_DESCRIBED_BY: (
        "http://biomodels.net/biology-qualifiers/",
        "isDescribedBy",
    ),
    BQBiol.IS_ENCODED_BY: (
        "http://biomodels.net/biology-qualifiers/",
        "isEncodedBy",
    ),
    BQBiol.IS_HOMOLOG_TO: (
        "http://biomodels.net/biology-qualifiers/",
        "isHomologTo",
    ),
    BQBiol.IS_PART_OF: (
        "http://biomodels.net/biology-qualifiers/",
        "isPartOf",
    ),
    BQBiol.IS_PROPERTY_OF: (
        "http://biomodels.net/biology-qualifiers/",
        "isPropertyOf",
    ),
    BQBiol.IS_VERSION_OF: (
        "http://biomodels.net/biology-qualifiers/",
        "isVersionOf",
    ),
    BQBiol.OCCURS_IN: (
        "http://biomodels.net/biology-qualifiers/",
        "occursIn",
    ),
    BQBiol.HAS_TAXON: (
        "http://biomodels.net/biology-qualifiers/",
        "hasTaxon",
    ),
    BQModel.HAS_INSTANCE: (
        "http://biomodels.net/model-qualifiers/",
        "hasInstance",
    ),
    BQModel.IS: (
        "http://biomodels.net/model-qualifiers/",
        "is",
    ),
    BQModel.IS_DERIVED_FROM: (
        "http://biomodels.net/model-qualifiers/",
        "isDerivedFrom",
    ),
    BQModel.IS_DESCRIBED_BY: (
        "http://biomodels.net/model-qualifiers/",
        "isDescribedBy",
    ),
    BQModel.IS_INSTANCE_OF: (
        "http://biomodels.net/model-qualifiers/",
        "isInstanceOf",
    ),
}

QUALIFIER_ATTRIBUTE_TO_QUALIFIER_MEMBER = {
    v: k for k, v in QUALIFIER_MEMBER_TO_QUALIFIER_ATTRIBUTE.items()
}

# Extra entry: biology-qualifiers/hasInstance maps to BQModel.HAS_INSTANCE
# (used in SBML and CellDesigner readers, not in the writer)
QUALIFIER_ATTRIBUTE_TO_QUALIFIER_MEMBER[
    (
        "http://biomodels.net/biology-qualifiers/",
        "hasInstance",
    )
] = BQModel.HAS_INSTANCE
