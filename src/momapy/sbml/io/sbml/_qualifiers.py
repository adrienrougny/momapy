"""Qualifier mappings for SBML-based readers and writers.

This is the canonical location for qualifier mappings. SBGN-ML and
CellDesigner import from here.
"""

import momapy.sbml.core


QUALIFIER_MEMBER_TO_QUALIFIER_ATTRIBUTE = {
    momapy.sbml.core.BQBiol.ENCODES: (
        "http://biomodels.net/biology-qualifiers/",
        "encodes",
    ),
    momapy.sbml.core.BQBiol.HAS_PART: (
        "http://biomodels.net/biology-qualifiers/",
        "hasPart",
    ),
    momapy.sbml.core.BQBiol.HAS_PROPERTY: (
        "http://biomodels.net/biology-qualifiers/",
        "hasProperty",
    ),
    momapy.sbml.core.BQBiol.HAS_VERSION: (
        "http://biomodels.net/biology-qualifiers/",
        "hasVersion",
    ),
    momapy.sbml.core.BQBiol.IS: (
        "http://biomodels.net/biology-qualifiers/",
        "is",
    ),
    momapy.sbml.core.BQBiol.IS_DESCRIBED_BY: (
        "http://biomodels.net/biology-qualifiers/",
        "isDescribedBy",
    ),
    momapy.sbml.core.BQBiol.IS_ENCODED_BY: (
        "http://biomodels.net/biology-qualifiers/",
        "isEncodedBy",
    ),
    momapy.sbml.core.BQBiol.IS_HOMOLOG_TO: (
        "http://biomodels.net/biology-qualifiers/",
        "isHomologTo",
    ),
    momapy.sbml.core.BQBiol.IS_PART_OF: (
        "http://biomodels.net/biology-qualifiers/",
        "isPartOf",
    ),
    momapy.sbml.core.BQBiol.IS_PROPERTY_OF: (
        "http://biomodels.net/biology-qualifiers/",
        "isPropertyOf",
    ),
    momapy.sbml.core.BQBiol.IS_VERSION_OF: (
        "http://biomodels.net/biology-qualifiers/",
        "isVersionOf",
    ),
    momapy.sbml.core.BQBiol.OCCURS_IN: (
        "http://biomodels.net/biology-qualifiers/",
        "occursIn",
    ),
    momapy.sbml.core.BQBiol.HAS_TAXON: (
        "http://biomodels.net/biology-qualifiers/",
        "hasTaxon",
    ),
    momapy.sbml.core.BQModel.HAS_INSTANCE: (
        "http://biomodels.net/model-qualifiers/",
        "hasInstance",
    ),
    momapy.sbml.core.BQModel.IS: (
        "http://biomodels.net/model-qualifiers/",
        "is",
    ),
    momapy.sbml.core.BQModel.IS_DERIVED_FROM: (
        "http://biomodels.net/model-qualifiers/",
        "isDerivedFrom",
    ),
    momapy.sbml.core.BQModel.IS_DESCRIBED_BY: (
        "http://biomodels.net/model-qualifiers/",
        "isDescribedBy",
    ),
    momapy.sbml.core.BQModel.IS_INSTANCE_OF: (
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
] = momapy.sbml.core.BQModel.HAS_INSTANCE
