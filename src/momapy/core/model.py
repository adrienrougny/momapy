"""Abstract model base class."""

import abc
import dataclasses

import momapy.core.elements


@dataclasses.dataclass(frozen=True, kw_only=True)
class Model(momapy.core.elements.MapElement):
    """Base class for models"""

    @abc.abstractmethod
    def is_submodel(self, other) -> bool:
        pass
