from dataclasses import dataclass, field

from momapy.types import ModelElement, Model, LayoutElement, Layout, Map

# @dataclass(frozen=True)
# class GraphModelElement(ModelElement):
#     pass
#
# @dataclass(frozen=True)
# class GraphLayoutElement(LayoutElement):
#     pass

@dataclass(frozen=True)
class Node(ModelElement):
    label: str = None

@dataclass(frozen=True)
class Edge(ModelElement):
    start_node: Node = None
    end_node: Node = None

@dataclass(frozen=True)
class GraphModel(Model):
    nodes: frozenset[Node] = field(default_factory=frozenset)
    edges: frozenset[Edge] = field(default_factory=frozenset)

    def add(self, obj):
        if isinstance(obj, Node):
            return self.__class__(self.id, self.nodes.union([obj]), self.edges)
        elif isinstance(obj, Edge):
            return self.__class__(self.id, self.nodes, self.edges.union([obj]))
        else:
            raise(TypeError)

@dataclass(frozen=True)
class GraphLayout(Layout):
    pass

@dataclass(frozen=True)
class GraphMap(Map):
    model: GraphModel = None
    layout: GraphLayout = None
    model_layout_mapping: ModelLayoutMapping = field(default_factory=ModelLayoutMapping)
