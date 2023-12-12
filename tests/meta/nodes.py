import dataclasses

import momapy.meta.nodes
import momapy.utils

WIDTH = 60
HEIGHT = 30

node_configs = [
    (
        momapy.meta.nodes.Rectangle,
        {
            "width": WIDTH,
            "height": HEIGHT,
        },
    ),
    (
        momapy.meta.nodes.Rectangle,
        {
            "width": WIDTH,
            "height": HEIGHT,
            "top_left_rx": 10.0,
            "top_left_ry": 10.0,
            "top_left_rounded_or_cut": "rounded",
            "top_right_rx": 10.0,
            "top_right_ry": 10.0,
            "top_right_rounded_or_cut": "rounded",
            "bottom_left_rx": 10.0,
            "bottom_left_ry": 10.0,
            "bottom_left_rounded_or_cut": "rounded",
            "bottom_right_rx": 10.0,
            "bottom_right_ry": 10.0,
            "bottom_right_rounded_or_cut": "rounded",
        },
    ),
    (
        momapy.meta.nodes.Rectangle,
        {
            "width": WIDTH,
            "height": HEIGHT,
            "top_left_rx": 10.0,
            "top_left_ry": 10.0,
            "top_left_rounded_or_cut": "cut",
            "top_right_rx": 10.0,
            "top_right_ry": 10.0,
            "top_right_rounded_or_cut": "cut",
            "bottom_left_rx": 10.0,
            "bottom_left_ry": 10.0,
            "bottom_left_rounded_or_cut": "cut",
            "bottom_right_rx": 10.0,
            "bottom_right_ry": 10.0,
            "bottom_right_rounded_or_cut": "cut",
        },
    ),
    (
        momapy.meta.nodes.Rectangle,
        {
            "width": WIDTH,
            "height": HEIGHT,
            "top_left_rx": 5.0,
            "top_left_ry": 10.0,
            "top_left_rounded_or_cut": "rounded",
            "top_right_rx": 10.0,
            "top_right_ry": 5.0,
            "top_right_rounded_or_cut": "rounded",
            "bottom_left_rx": 5.0,
            "bottom_left_ry": 10.0,
            "bottom_left_rounded_or_cut": "cut",
            "bottom_right_rx": 10.0,
            "bottom_right_ry": 5.0,
            "bottom_right_rounded_or_cut": "cut",
        },
    ),
    (
        momapy.meta.nodes.Hexagon,
        {
            "width": WIDTH,
            "height": HEIGHT,
        },
    ),
    (
        momapy.meta.nodes.Hexagon,
        {
            "width": WIDTH,
            "height": HEIGHT,
            "left_angle": 120,
            "right_angle": 120,
        },
    ),
    (
        momapy.meta.nodes.Hexagon,
        {
            "width": WIDTH,
            "height": HEIGHT,
            "left_angle": 120,
            "right_angle": 60,
        },
    ),
    (
        momapy.meta.nodes.Hexagon,
        {
            "width": WIDTH,
            "height": HEIGHT,
            "left_angle": 60,
            "right_angle": 120,
        },
    ),
    (
        momapy.meta.nodes.TurnedHexagon,
        {
            "width": WIDTH,
            "height": HEIGHT,
        },
    ),
    (
        momapy.meta.nodes.TurnedHexagon,
        {
            "width": WIDTH,
            "height": HEIGHT,
            "top_angle": 100,
            "bottom_angle": 100,
        },
    ),
    (
        momapy.meta.nodes.TurnedHexagon,
        {
            "width": WIDTH,
            "height": HEIGHT,
            "top_angle": 100,
            "bottom_angle": 80,
        },
    ),
    (
        momapy.meta.nodes.TurnedHexagon,
        {
            "width": WIDTH,
            "height": HEIGHT,
            "top_angle": 80,
            "bottom_angle": 100,
        },
    ),
    (
        momapy.meta.nodes.Parallelogram,
        {
            "width": WIDTH,
            "height": HEIGHT,
        },
    ),
    (
        momapy.meta.nodes.Parallelogram,
        {
            "width": WIDTH,
            "height": HEIGHT,
            "angle": 120,
        },
    ),
    (
        momapy.meta.nodes.Ellipse,
        {
            "width": WIDTH,
            "height": HEIGHT,
        },
    ),
    (
        momapy.meta.nodes.CrossPoint,
        {
            "width": WIDTH,
            "height": HEIGHT,
        },
    ),
    (
        momapy.meta.nodes.Triangle,
        {
            "width": WIDTH,
            "height": HEIGHT,
        },
    ),
    (
        momapy.meta.nodes.Triangle,
        {
            "width": WIDTH,
            "height": HEIGHT,
            "direction": momapy.core.Direction.UP,
        },
    ),
    (
        momapy.meta.nodes.Triangle,
        {
            "width": WIDTH,
            "height": HEIGHT,
            "direction": momapy.core.Direction.LEFT,
        },
    ),
    (
        momapy.meta.nodes.Triangle,
        {
            "width": WIDTH,
            "height": HEIGHT,
            "direction": momapy.core.Direction.DOWN,
        },
    ),
    (
        momapy.meta.nodes.Diamond,
        {
            "width": WIDTH,
            "height": HEIGHT,
        },
    ),
    (
        momapy.meta.nodes.Bar,
        {
            "width": WIDTH,
            "height": HEIGHT,
        },
    ),
    (
        momapy.meta.nodes.ArcBarb,
        {
            "width": WIDTH,
            "height": HEIGHT,
        },
    ),
    (
        momapy.meta.nodes.ArcBarb,
        {
            "width": WIDTH,
            "height": HEIGHT,
            "direction": momapy.core.Direction.UP,
        },
    ),
    (
        momapy.meta.nodes.ArcBarb,
        {
            "width": WIDTH,
            "height": HEIGHT,
            "direction": momapy.core.Direction.LEFT,
        },
    ),
    (
        momapy.meta.nodes.ArcBarb,
        {
            "width": WIDTH,
            "height": HEIGHT,
            "direction": momapy.core.Direction.DOWN,
        },
    ),
    (
        momapy.meta.nodes.StraightBarb,
        {
            "width": WIDTH,
            "height": HEIGHT,
        },
    ),
    (
        momapy.meta.nodes.StraightBarb,
        {
            "width": WIDTH,
            "height": HEIGHT,
            "direction": momapy.core.Direction.UP,
        },
    ),
    (
        momapy.meta.nodes.StraightBarb,
        {
            "width": WIDTH,
            "height": HEIGHT,
            "direction": momapy.core.Direction.LEFT,
        },
    ),
    (
        momapy.meta.nodes.StraightBarb,
        {
            "width": WIDTH,
            "height": HEIGHT,
            "direction": momapy.core.Direction.DOWN,
        },
    ),
    (
        momapy.meta.nodes.To,
        {
            "width": WIDTH,
            "height": HEIGHT,
        },
    ),
    (
        momapy.meta.nodes.To,
        {
            "width": WIDTH,
            "height": HEIGHT,
            "direction": momapy.core.Direction.UP,
        },
    ),
    (
        momapy.meta.nodes.To,
        {
            "width": WIDTH,
            "height": HEIGHT,
            "direction": momapy.core.Direction.LEFT,
        },
    ),
    (
        momapy.meta.nodes.To,
        {
            "width": WIDTH,
            "height": HEIGHT,
            "direction": momapy.core.Direction.DOWN,
        },
    ),
]

momapy.utils.render_nodes_testing(
    "nodes.pdf",
    node_configs,
    WIDTH + 20,
    WIDTH + 20,
)
