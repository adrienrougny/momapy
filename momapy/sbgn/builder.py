from momapy.builder import get_or_make_builder_cls, LayoutBuilder, ModelLayoutMappingBuilder
from momapy.sbgn.core import SBGNModel, EntityPool, Process, SBGNMap

# def sbgn_model_builder_add_element(self, element):
#     if isinstance(element, get_or_make_builder_cls(EntityPool)):
#         self.entity_pools.add(element)
#     elif isinstance(element, get_or_make_builder_cls(Process)):
#         self.processes.add(element)

SBGNModelBuilder = get_or_make_builder_cls(SBGNModel)

def sbgn_map_builder_new_model(self, *args, **kwargs):
    return SBGNModelBuilder(*args, **kwargs)

def sbgn_map_builder_new_layout(self, *args, **kwargs):
    return LayoutBuilder(*args, **kwargs)

def sbgn_map_builder_new_model_layout_mapping(self, *args, **kwargs):
    return ModelLayoutMappingBuilder(*args, **kwargs)

SBGNMapBuilder = get_or_make_builder_cls(
    SBGNMap,
    builder_namespace={
        "new_model": sbgn_map_builder_new_model,
        "new_layout": sbgn_map_builder_new_layout,
        "new_model_layout_mapping": sbgn_map_builder_new_model_layout_mapping
    }
)
