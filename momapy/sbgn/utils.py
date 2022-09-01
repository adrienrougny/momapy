import collections

import momapy.positioning

def set_compartments_to_fit_content(map_builder, xsep=0, ysep=0):
    compartment_entity_pools_mapping = collections.defaultdict(list)
    model = map_builder.model
    for entity_pool in model.entity_pools:
        compartment = entity_pool.compartment
        if compartment is not None:
            compartment_entity_pools_mapping[compartment].append(entity_pool)
    for compartment in compartment_entity_pools_mapping:
        for compartment_layout in map_builder.model_layout_mapping[
                compartment]:
            elements = []
            for entity_pool in compartment_entity_pools_mapping[compartment]:
                a = map_builder.model_layout_mapping[entity_pool]
                elements += map_builder.model_layout_mapping[entity_pool]
            momapy.positioning.set_fit(
                compartment_layout, elements, xsep, ysep)
            if compartment_layout.label is not None:
                compartment_layout.label.position = compartment_layout.position
