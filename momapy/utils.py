import frozendict
import collections.abc
import dataclasses
import colorama

import momapy.rendering.core
import momapy.rendering.skia


def pretty_print(obj, max_depth=0, _depth=0, _indent=0):
    def _print_with_indent(s, indent):
        print(f"{'  '*indent}{s}")

    def _get_value_string(attr_value, max_len=30):
        s = str(attr_value)
        if len(s) > max_len:
            s = f"{s[:max_len]}..."
        return s

    if _depth > max_depth:
        return
    obj_typing = type(obj)
    obj_value_string = _get_value_string(obj)
    obj_string = f"{colorama.Fore.BLACK}{obj_typing}{colorama.Fore.RED}: {obj_value_string}{colorama.Style.RESET_ALL}"
    _print_with_indent(obj_string, _indent)
    if dataclasses.is_dataclass(type(obj)):
        for field in dataclasses.fields(obj):
            attr_name = field.name
            if not attr_name.startswith("_"):
                attr_value = getattr(obj, attr_name)
                attr_typing = field.type
                attr_value_string = _get_value_string(attr_value)
                attr_string = f"{colorama.Fore.BLUE}* {attr_name}{colorama.Fore.MAGENTA}: {attr_typing} = {colorama.Fore.RED}{attr_value_string}{colorama.Style.RESET_ALL}"
                _print_with_indent(attr_string, _indent + 1)
                pretty_print(
                    attr_value,
                    max_depth=max_depth,
                    _depth=_depth + 1,
                    _indent=_indent + 2,
                )
    if isinstance(obj, collections.abc.Iterable):
        for i, elem_value in enumerate(obj):
            elem_typing = type(elem_value)
            elem_value_string = _get_value_string(elem_value)
            elem_string = f"{colorama.Fore.BLUE}- {i}{colorama.Fore.MAGENTA}: {elem_typing} = {colorama.Fore.RED}{elem_value_string}{colorama.Style.RESET_ALL}"
            _print_with_indent(elem_string, _indent + 1)
            pretty_print(
                elem_value,
                max_depth=max_depth,
                _depth=_depth + 1,
                _indent=_indent + 2,
            )


def print_classes(obj):
    for cls in type(obj).__mro__:
        print(cls)


def render_nodes_on_grid(
    output_file,
    nodes,
    n_cols,
    width,
    height,
    x_margin=10.0,
    y_margin=10.0,
    format="pdf",
    renderer="skia",
):
    max_x = x_margin * 2 + n_cols * width
    n_rows = len(nodes) // n_cols + int(bool(len(nodes) % n_cols))
    max_y = y_margin * 2 + n_rows * height
    renderer = momapy.rendering.core.renderers[renderer].from_file(
        output_file, max_x, max_y, format
    )
    renderer.begin_session()
    for i, node in enumerate(nodes):
        n_row = i // n_cols
        n_col = i % n_cols
        position = momapy.geometry.Point(
            x_margin + width * (n_col + 1 / 2),
            y_margin + height * (n_row + 1 / 2),
        )
        if not isinstance(node, momapy.core.NodeLayoutBuilder):
            node = momapy.builder.builder_from_object(node)
        tx = position.x - node.position.x
        ty = position.y - node.position.y
        translation = momapy.geometry.Translation(tx, ty)
        if node.transform is None:
            node.transform = momapy.core.TupleBuilder()
        node.transform.append(translation)
        node = momapy.builder.object_from_builder(node)
        renderer.render_layout_element(node)
    renderer.end_session()


def render_nodes_testing(
    output_file,
    node_configs,
    width,
    height,
    x_margin=10.0,
    y_margin=10.0,
    format="pdf",
    renderer="skia",
    node_width=60.0,
    node_height=30.0,
    border_stroke=None,
    border_stroke_width=None,
    border_fill=None,
):
    node_objs = []
    for node_config in node_configs:
        node_cls = node_config[0]
        node_obj = momapy.nodes.Rectangle(
            position=momapy.geometry.Point(0, 0),
            width=node_width,
            height=node_height,
            stroke_width=0.0,
            fill=momapy.drawing.NoneValue,
            label=momapy.core.TextLayout(
                position=momapy.geometry.Point(0, 0),
                text=node_cls.__name__,
                font_size=10,
                font_family="Cantarell",
            ),
        )
        node_objs.append(node_obj)
        kwargs = node_config[1]
        if "width" not in kwargs:
            kwargs["width"] = node_width
        if "height" not in kwargs:
            kwargs["height"] = node_height
        kwargs["position"] = momapy.geometry.Point(0, 0)
        if "border_stroke" not in kwargs:
            kwargs["border_stroke"] = border_stroke
        if "border_stroke_width" not in kwargs:
            kwargs["border_stroke_width"] = border_stroke_width
        if "border_fill" not in kwargs:
            kwargs["border_fill"] = border_fill
        node_obj = node_cls(**kwargs)
        node_objs.append(node_obj)

        anchor_cross_points = []
        for anchor_name in [
            "north_west",
            "north",
            "north_east",
            "east",
            "south_east",
            "south",
            "south_west",
            "west",
            "center",
            "label_center",
        ]:
            p = getattr(node_obj, anchor_name)()
            cross_point = momapy.nodes.CrossPoint(
                position=p,
                width=5.0,
                height=5.0,
                stroke=momapy.coloring.red,
                stroke_width=0.5,
            )
            anchor_cross_points.append(cross_point)
        kwargs["layout_elements"] = tuple(anchor_cross_points)
        node_obj = node_cls(**kwargs)
        node_objs.append(node_obj)

        angle_cross_points = []
        for angle in range(0, 380, 30):
            p = node_obj.self_angle(angle)
            cross_point = momapy.nodes.CrossPoint(
                position=p,
                width=5.0,
                height=5.0,
                stroke=momapy.coloring.darkgoldenrod,
                stroke_width=0.5,
            )
            angle_cross_points.append(cross_point)
        kwargs["layout_elements"] = tuple(angle_cross_points)
        node_obj = node_cls(**kwargs)
        node_objs.append(node_obj)

    render_nodes_on_grid(
        output_file=output_file,
        nodes=node_objs,
        n_cols=4,
        width=width,
        height=height,
        x_margin=x_margin,
        y_margin=y_margin,
        format=format,
        renderer=renderer,
    )
