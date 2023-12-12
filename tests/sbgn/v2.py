#!python

import momapy.builder
import momapy.positioning
import momapy.rendering.core
import momapy.rendering.skia
import momapy.styling
import momapy.sbgn.pd


def make_node(
    cls,
    position=None,
    width=None,
    height=None,
    text=None,
    font_size=14.0,
    anchor="center",
):
    cls = momapy.builder.get_or_make_builder_cls(cls)
    node = cls()
    if width is not None:
        node.width = width
    if height is not None:
        node.height = height
    if position is not None:
        if isinstance(position, (tuple, list)):
            position = momapy.geometry.Point(position[0], position[1])
        momapy.positioning.set_position(node, position, anchor)
    if text is not None:
        label = momapy.core.TextLayoutBuilder(
            text=text, font_size=font_size, font_family="Arial"
        )
        if node.position is not None:
            label.position = node.position
        node.label = label
    return node


def make_arc(cls, points):
    cls = momapy.builder.get_or_make_builder_cls(cls)
    arc = cls()
    previous_point = points[0]
    for point in points[1:]:
        segment = momapy.geometry.Segment(point, previous_point)
        arc.segments.append(segment)
    return arc


layout = make_node(
    momapy.sbgn.pd.SBGNPDLayout, position=(500, 500), width=1000, height=1000
)

aa1 = make_node(
    momapy.sbgn.pd.SimpleChemicalLayout,
    position=(100, 500),
    text="AA",
)

n_aa1 = make_node(
    momapy.sbgn.pd.UnitOfInformationLayout,
    position=aa1.north(),
    width=24.0,
    height=10.0,
    text="N:n-1",
    font_size=8.0,
)
aa1.add_element(n_aa1)

aa2 = make_node(
    momapy.sbgn.pd.SimpleChemicalLayout,
    position=momapy.positioning.right_of(aa1, 40),
    text="AA",
)

trna1 = make_node(
    momapy.sbgn.pd.SimpleChemicalLayout,
    position=momapy.positioning.below_of(aa2, 30),
    text="tRNA",
)

prot1 = make_node(
    momapy.sbgn.pd.MacromoleculeLayout,
)
momapy.positioning.set_fit(prot1, [aa1, aa2, trna1], xsep=5.0, ysep=5.0)

mrna1 = make_node(
    momapy.sbgn.pd.NucleicAcidFeatureLayout,
    position=(trna1.x, prot1.south().y + 10),
    text="mRNA",
    anchor="north",
)


prot2 = make_node(
    momapy.sbgn.pd.MacromoleculeLayout,
    position=(prot1.x, mrna1.south().y + 10),
    anchor="north",
    width=prot1.width,
    text="ribosome",
)

comp1 = make_node(
    momapy.sbgn.pd.ComplexLayout,
)
momapy.positioning.set_fit(
    comp1, [prot1, mrna1, trna1, prot2], xsep=5.0, ysep=5.0
)

trna2 = make_node(
    momapy.sbgn.pd.SimpleChemicalLayout,
    position=momapy.positioning.above_of(aa2, 100),
    text="tRNA",
)

aa3 = make_node(
    momapy.sbgn.pd.SimpleChemicalLayout,
    position=momapy.positioning.above_of(trna2, 30),
    text="AA",
)

sim1 = make_node(
    momapy.sbgn.pd.SimpleChemicalLayout,
)
momapy.positioning.set_fit(sim1, [trna2, aa3], xsep=10.0, ysep=10.0)

log1 = make_arc(momapy.sbgn.pd.LogicArcLayout, [aa1.east(), aa2.west()])

log2 = make_arc(momapy.sbgn.pd.LogicArcLayout, [aa2.south(), trna1.north()])

log3 = make_arc(momapy.sbgn.pd.LogicArcLayout, [aa3.south(), trna2.north()])

p1 = make_node(
    momapy.sbgn.pd.GenericProcessLayout,
    position=momapy.positioning.right_of(comp1, 100),
)


cons1 = make_arc(
    momapy.sbgn.pd.ConsumptionLayout, [comp1.border(p1.west()), p1.west()]
)

cons2 = make_arc(
    momapy.sbgn.pd.ConsumptionLayout, [sim1.border(p1.west()), p1.west()]
)


aa1_2 = make_node(
    momapy.sbgn.pd.SimpleChemicalLayout,
    position=momapy.positioning.right_of(aa1, 300),
    text="AA",
)

n_aa1_2 = make_node(
    momapy.sbgn.pd.UnitOfInformationLayout,
    position=aa1_2.north(),
    width=24.0,
    height=10.0,
    text="N:n-1",
    font_size=8.0,
)
aa1_2.add_element(n_aa1_2)

aa2_2 = make_node(
    momapy.sbgn.pd.SimpleChemicalLayout,
    position=momapy.positioning.right_of(aa1_2, 40),
    text="AA",
)

trna1_2 = make_node(
    momapy.sbgn.pd.SimpleChemicalLayout,
    position=momapy.positioning.below_of(aa2_2, 30),
    text="tRNA",
)

prot1_2 = make_node(
    momapy.sbgn.pd.MacromoleculeLayout,
)
momapy.positioning.set_fit(prot1_2, [aa1_2, aa2_2, trna1_2], xsep=5.0, ysep=5.0)


trna2_2 = make_node(
    momapy.sbgn.pd.SimpleChemicalLayout,
    position=momapy.positioning.right_of(trna1_2, 60),
    text="tRNA",
)

aa3_2 = make_node(
    momapy.sbgn.pd.SimpleChemicalLayout,
    position=momapy.positioning.above_of(trna2_2, 30),
    text="AA",
)

sim1_2 = make_node(
    momapy.sbgn.pd.SimpleChemicalLayout,
)
momapy.positioning.set_fit(sim1_2, [trna2_2, aa3_2], xsep=10.0, ysep=10.0)

mrna1_2 = make_node(
    momapy.sbgn.pd.NucleicAcidFeatureLayout,
    position=(
        0.5 * (trna1_2.west().x + trna2_2.east().x),
        prot1_2.south().y + 10,
    ),
    anchor="north",
    text="mRNA",
    width=trna2_2.east().x - trna1_2.west().x,
)
prot2_2 = make_node(
    momapy.sbgn.pd.MacromoleculeLayout,
    position=(
        0.5 * (prot1_2.west().x + sim1_2.east().x),
        mrna1_2.south().y + 10,
    ),
    anchor="north",
    width=sim1_2.east().x - prot1_2.west().x,
    text="ribosome",
)

comp1_2 = make_node(
    momapy.sbgn.pd.ComplexLayout,
)
momapy.positioning.set_fit(
    comp1_2, [prot1_2, mrna1_2, trna1_2, prot2_2, sim1_2], xsep=5.0, ysep=5.0
)

log1_2 = make_arc(momapy.sbgn.pd.LogicArcLayout, [aa1_2.east(), aa2_2.west()])

log2_2 = make_arc(
    momapy.sbgn.pd.LogicArcLayout, [aa2_2.south(), trna1_2.north()]
)

log3_2 = make_arc(
    momapy.sbgn.pd.LogicArcLayout, [aa3_2.south(), trna2_2.north()]
)

aa1_3 = make_node(
    momapy.sbgn.pd.SimpleChemicalLayout,
    position=momapy.positioning.right_of(aa1_2, 300),
    text="AA",
)

n_aa1_3 = make_node(
    momapy.sbgn.pd.UnitOfInformationLayout,
    position=aa1_3.north(),
    width=24.0,
    height=10.0,
    text="N:n-1",
    font_size=8.0,
)
aa1_3.add_element(n_aa1_3)

aa2_3 = make_node(
    momapy.sbgn.pd.SimpleChemicalLayout,
    position=momapy.positioning.right_of(aa1_3, 40),
    text="AA",
)

trna1_3 = make_node(
    momapy.sbgn.pd.SimpleChemicalLayout,
    position=momapy.positioning.below_of(aa2_3, 30),
    text="tRNA",
)

aa3_3 = make_node(
    momapy.sbgn.pd.SimpleChemicalLayout,
    position=momapy.positioning.right_of(aa2_3, 40),
    text="AA",
)
trna2_3 = make_node(
    momapy.sbgn.pd.SimpleChemicalLayout,
    position=momapy.positioning.below_of(aa3_3, 30),
    text="tRNA",
)

prot1_3 = make_node(
    momapy.sbgn.pd.MacromoleculeLayout,
)
momapy.positioning.set_fit(
    prot1_3, [aa1_3, aa2_3, trna1_3, aa3_3, trna2_3], xsep=5.0, ysep=5.0
)


mrna1_3 = make_node(
    momapy.sbgn.pd.NucleicAcidFeatureLayout,
    position=(
        0.5 * (trna1_3.west().x + trna2_3.east().x),
        prot1_3.south().y + 10,
    ),
    anchor="north",
    text="mRNA",
    width=trna2_3.east().x - trna1_3.west().x,
)
prot2_3 = make_node(
    momapy.sbgn.pd.MacromoleculeLayout,
    position=(
        0.5 * (prot1_3.west().x + prot1_3.east().x),
        mrna1_3.south().y + 10,
    ),
    anchor="north",
    width=prot1_3.width,
    text="ribosome",
)

comp1_3 = make_node(
    momapy.sbgn.pd.ComplexLayout,
)
momapy.positioning.set_fit(
    comp1_3, [prot1_3, mrna1_3, trna1_3, prot2_3], xsep=5.0, ysep=5.0
)

log1_3 = make_arc(momapy.sbgn.pd.LogicArcLayout, [aa1_3.east(), aa2_3.west()])

log2_3 = make_arc(
    momapy.sbgn.pd.LogicArcLayout, [aa2_3.south(), trna1_3.north()]
)

log3_3 = make_arc(
    momapy.sbgn.pd.LogicArcLayout, [aa3_3.south(), trna2_3.north()]
)

log4_3 = make_arc(momapy.sbgn.pd.LogicArcLayout, [aa2_3.east(), aa3_3.west()])


layout.add_element(comp1)
layout.add_element(prot1)
layout.add_element(mrna1)
layout.add_element(prot2)
layout.add_element(aa1)
layout.add_element(aa2)
layout.add_element(trna1)
layout.add_element(sim1)
layout.add_element(aa3)
layout.add_element(trna2)

layout.add_element(log1)
layout.add_element(log2)
layout.add_element(log3)
layout.add_element(cons1)
layout.add_element(cons2)

layout.add_element(p1)

layout.add_element(comp1_2)
layout.add_element(prot1_2)
layout.add_element(mrna1_2)
layout.add_element(prot2_2)
layout.add_element(aa1_2)
layout.add_element(aa2_2)
layout.add_element(trna1_2)
layout.add_element(sim1_2)
layout.add_element(aa3_2)
layout.add_element(trna2_2)

layout.add_element(log1_2)
layout.add_element(log2_2)
layout.add_element(log3_2)
# layout.add_element(cons1)
# layout.add_element(cons2)

layout.add_element(comp1_3)
layout.add_element(prot1_3)
layout.add_element(mrna1_3)
layout.add_element(prot2_3)
layout.add_element(aa1_3)
layout.add_element(aa2_3)
layout.add_element(trna1_3)
layout.add_element(aa3_3)
layout.add_element(trna2_3)

layout.add_element(log1_3)
layout.add_element(log2_3)
layout.add_element(log3_3)
layout.add_element(log4_3)

renderer = momapy.rendering.skia.SkiaRenderer.from_file(
    "v2.pdf", 1000, 1000, "pdf"
)
renderer.begin_session()
renderer.render_layout_element(layout)
renderer.end_session()
