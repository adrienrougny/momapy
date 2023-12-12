import momapy.core
import momapy.builder
import momapy.meta.nodes
import momapy.rendering.core


def render_layout_elements_on_grid(
    output_file,
    layout_elements,
    n_cols,
    width,
    height,
    x_margin=10.0,
    y_margin=10.0,
    format="pdf",
    renderer="skia",
):
    max_x = x_margin * 2 + n_cols * width
    n_rows = len(layout_elements) // n_cols + int(
        bool(len(layout_elements) % n_cols)
    )
    max_y = y_margin * 2 + n_rows * height
    renderer = momapy.rendering.core.renderers[renderer].from_file(
        output_file, max_x, max_y, format
    )
    renderer.begin_session()
    for i, layout_element in enumerate(layout_elements):
        n_row = i // n_cols
        n_col = i % n_cols
        new_position = momapy.geometry.Point(
            x_margin + width * (n_col + 1 / 2),
            y_margin + height * (n_row + 1 / 2),
        )
        if momapy.builder.isinstance_or_builder(
            layout_element, momapy.core.Arc
        ):
            old_position = layout_element.points()[0] * (
                1 / 2
            ) + layout_element.points()[-1] * (1 / 2)
        elif momapy.builder.isinstance_or_builder(
            layout_element, momapy.core.Node
        ):
            old_position = layout_element.position
        else:
            raise TypeError(
                f"layout element must be of type {momapy.core.Node} or {momapy.core.Arc}"
            )
        if not isinstance(layout_element, momapy.builder.Builder):
            layout_element = momapy.builder.builder_from_object(layout_element)
        tx = new_position.x - old_position.x
        ty = new_position.y - old_position.y
        translation = momapy.geometry.Translation(tx, ty)
        if layout_element.transform is None:
            layout_element.transform = momapy.core.TupleBuilder()
        layout_element.transform.append(translation)
        layout_element = momapy.builder.object_from_builder(layout_element)
        renderer.render_layout_element(layout_element)
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
):
    node_objs = []
    for node_config in node_configs:
        node_cls = node_config[0]
        node_obj = momapy.meta.nodes.Rectangle(
            position=momapy.geometry.Point(0, 0),
            width=10.0,
            height=10.0,
            label=momapy.core.TextLayout(
                position=momapy.geometry.Point(0, 0),
                text=node_cls.__name__,
                font_size=7,
                font_family="Cantarell",
                font_style=momapy.drawing.FontStyle.ITALIC,
                font_weight=momapy.drawing.FontWeight.BOLD,
                fill=momapy.coloring.black,
                stroke=momapy.drawing.NoneValue,
            ),
            border_stroke_width=0.0,
            border_fill=momapy.coloring.white,
        )
        node_objs.append(node_obj)

        kwargs = node_config[1]
        kwargs["position"] = momapy.geometry.Point(0, 0)
        kwargs["fill"] = momapy.coloring.lightblue
        kwargs["stroke"] = momapy.coloring.black
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
            cross_point = momapy.meta.nodes.CrossPoint(
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
            cross_point = momapy.meta.nodes.CrossPoint(
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

    render_layout_elements_on_grid(
        output_file=output_file,
        layout_elements=node_objs,
        n_cols=4,
        width=width,
        height=height,
        x_margin=x_margin,
        y_margin=y_margin,
        format=format,
        renderer=renderer,
    )


def render_arcs_testing(
    output_file,
    arc_configs,
    width,
    height,
    x_margin=10.0,
    y_margin=10.0,
    format="pdf",
    renderer="skia",
    path_stroke=None,
    path_stroke_width=None,
    path_fill=None,
    arrowhead_stroke=None,
    arrowhead_stroke_width=None,
):
    arc_objs = []
    for arc_config in arc_configs:
        arc_cls = arc_config[0]
        arc_obj = momapy.meta.nodes.Rectangle(
            position=momapy.geometry.Point(0, 0),
            width=width,
            height=height,
            stroke_width=0.0,
            fill=momapy.drawing.NoneValue,
            label=momapy.core.TextLayout(
                position=momapy.geometry.Point(0, 0),
                text=arc_cls.__name__,
                font_size=10,
                font_family="Cantarell",
                fill=momapy.coloring.black,
                stroke=momapy.drawing.NoneValue,
            ),
        )
        arc_objs.append(arc_obj)

        kwargs = arc_config[1]
        if "path_stroke" not in kwargs:
            kwargs["path_stroke"] = path_stroke
        if "path_stroke_width" not in kwargs:
            kwargs["path_stroke_width"] = path_stroke_width
        if "path_fill" not in kwargs:
            kwargs["path_fill"] = path_fill

        if "arrowhead_stroke" not in kwargs:
            kwargs["arrowhead_stroke"] = arrowhead_stroke
        if "arrowhead_stroke_width" not in kwargs:
            kwargs["arrowhead_stroke_width"] = arrowhead_stroke_width
        kwargs["segments"] = tuple(
            [
                momapy.geometry.Segment(
                    momapy.geometry.Point(0, 0),
                    momapy.geometry.Point(0.8 * width, -0.8 * height),
                )
            ]
        )
        arc_obj = arc_cls(**kwargs)
        arc_objs.append(arc_obj)

        anchor_cross_points = []
        for anchor_name in [
            "start_point",
            "end_point",
            "arrowhead_base",
            "arrowhead_tip",
        ]:
            p = getattr(arc_obj, anchor_name)()
            cross_point = momapy.meta.nodes.CrossPoint(
                position=p,
                width=5.0,
                height=5.0,
                stroke=momapy.coloring.red,
                stroke_width=0.5,
            )
            anchor_cross_points.append(cross_point)
        kwargs["layout_elements"] = tuple(anchor_cross_points)
        arc_obj = arc_cls(**kwargs)
        arc_objs.append(arc_obj)

        fraction_cross_points = []
        for fraction in numpy.arange(0, 1.1, 0.2):
            p, _ = arc_obj.fraction(fraction)
            cross_point = momapy.meta.nodes.CrossPoint(
                position=p,
                width=5.0,
                height=5.0,
                stroke=momapy.coloring.darkgoldenrod,
                stroke_width=0.5,
            )
            fraction_cross_points.append(cross_point)
        kwargs["layout_elements"] = tuple(fraction_cross_points)
        arc_obj = arc_cls(**kwargs)
        arc_objs.append(arc_obj)

    render_layout_elements_on_grid(
        output_file=output_file,
        layout_elements=arc_objs,
        n_cols=4,
        width=width,
        height=height,
        x_margin=x_margin,
        y_margin=y_margin,
        format=format,
        renderer=renderer,
    )
