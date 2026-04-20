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

    def descendants(self) -> list[momapy.core.elements.ModelElement]:
        """Return every `ModelElement` reachable from this `Model`.

        Walks scalar `ModelElement` fields and `frozenset`/`tuple`
        containers of the `Model`, deduplicating by object identity.
        The `Model` itself is not a `ModelElement` and is not included.

        Returns:
            The list of reachable `ModelElement` instances in visit
            order.
        """
        seen: set[int] = set()
        result: list[momapy.core.elements.ModelElement] = []
        for field in dataclasses.fields(type(self)):
            momapy.core.elements._walk_model_graph(
                getattr(self, field.name), seen, result
            )
        return result
