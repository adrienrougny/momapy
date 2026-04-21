"""Abstract model base class."""

import abc
import dataclasses

from momapy.core.elements import MapElement, ModelElement, _walk_model_graph


@dataclasses.dataclass(frozen=True, kw_only=True)
class Model(MapElement):
    """Base class for models"""

    @abc.abstractmethod
    def is_submodel(self, other) -> bool:
        pass

    def descendants(self) -> list[ModelElement]:
        """Return every `ModelElement` reachable from this `Model`.

        Walks scalar `ModelElement` fields and `frozenset`/`tuple`
        containers of the `Model`, deduplicating by object identity.
        The `Model` itself is not a `ModelElement` and is not included.

        Returns:
            The list of reachable `ModelElement` instances in visit
            order.
        """
        seen: set[int] = set()
        result: list[ModelElement] = []
        for field in dataclasses.fields(type(self)):
            _walk_model_graph(getattr(self, field.name), seen, result)
        return result
