"""Abstract model base class."""

import abc
import dataclasses

from momapy.core.elements import MapElement, ModelElement, _walk_model_graph


@dataclasses.dataclass(frozen=True, kw_only=True)
class Model(MapElement, abc.ABC):
    """Abstract base class for models"""

    @abc.abstractmethod
    def is_submodel(self, other: "Model") -> bool:
        """Return whether this model is a submodel of another model.

        Args:
            other: The model to test against.

        Returns:
            `True` if this model is a submodel of `other`.
        """
        pass

    def descendants(self) -> list[ModelElement]:
        """Return every `ModelElement` reachable from this `Model`.

        This reflectively walks the dataclass field-graph — i.e. *reference
        reachability* — across scalar `ModelElement` fields and
        `frozenset`/`tuple` containers of the `Model`, deduplicating by
        object identity. The `Model` itself is not a `ModelElement` and is
        not included.

        This mirrors
        [`ModelElement.descendants`][momapy.core.elements.ModelElement.descendants]
        and contrasts with
        [`LayoutElement.descendants`][momapy.core.elements.LayoutElement.descendants],
        which walks the explicit `children()` tree (visual *containment*)
        rather than reference reachability.

        Returns:
            The list of reachable `ModelElement` instances in visit
            order.
        """
        seen: set[int] = set()
        result: list[ModelElement] = []
        for field in dataclasses.fields(type(self)):
            _walk_model_graph(getattr(self, field.name), seen, result)
        return result
