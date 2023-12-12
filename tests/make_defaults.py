import dataclasses

import momapy.core

import momapy.sbgn.pd

DEFAULT_KW = "defaults"

s = ""
for attr_name in dir(momapy.sbgn.pd):
    attr_value = getattr(momapy.sbgn.pd, attr_name)
    if (
        not attr_name.startswith("_")
        and isinstance(attr_value, type)
        and issubclass(attr_value, momapy.core.LayoutElement)
    ):
        for field in dataclasses.fields(attr_value):
            if (
                field.default_factory == dataclasses.MISSING
                and not field.name.startswith("_")
            ):
                if field.default != dataclasses.MISSING:
                    default_value = str(field.default)
                else:
                    default_value = ""
                s += f'{DEFAULT_KW}["{attr_name}"]["{field.name}"] = {default_value}\n'
print(s)
