import momapy.sbgn.pd
import momapy.sbgn.io
import momapy.rendering
import momapy.styling
import momapy.core
import momapy.coloring

style_sheet = {
    momapy.styling.ClassSelector(momapy.core.MapLayout): {
        "stroke_width": 2,
        "fill": momapy.coloring.colors.white,
    },
    momapy.styling.ClassSelector(momapy.sbgn.pd.CompartmentLayout): {
        "stroke_width": 7,
        "fill": momapy.coloring.colors.blanched_almond,
    },
    momapy.styling.ClassSelector(momapy.sbgn.pd.GenericProcessLayout): {
        "stroke": momapy.coloring.colors.gray,
    },
    momapy.styling.ClassSelector(momapy.sbgn.pd.MacromoleculeLayout): {
        "fill": momapy.coloring.colors.light_blue,
    },
    momapy.styling.ClassSelector(momapy.sbgn.pd.MacromoleculeMultimerLayout): {
        "fill": momapy.coloring.colors.light_blue,
    },
    momapy.styling.ClassSelector(momapy.sbgn.pd.ComplexLayout): {
        "fill": momapy.coloring.colors.yellow,
    },
    momapy.styling.ClassSelector(momapy.sbgn.pd.ComplexMultimerLayout): {
        "fill": momapy.coloring.colors.yellow,
    },
    momapy.styling.ClassSelector(momapy.sbgn.pd.SimpleChemicalLayout): {
        "fill": momapy.coloring.colors.orange,
    },
    momapy.styling.ClassSelector(momapy.sbgn.pd.SimpleChemicalMultimerLayout): {
        "fill": momapy.coloring.colors.orange,
    },
    momapy.styling.ClassSelector(momapy.sbgn.pd.NucleicAcidFeatureLayout): {
        "fill": momapy.coloring.colors.pale_green,
    },
    momapy.styling.ClassSelector(
        momapy.sbgn.pd.NucleicAcidFeatureMultimerLayout
    ): {
        "fill": momapy.coloring.colors.pale_green,
    },
    momapy.styling.ClassSelector(momapy.sbgn.pd.PhenotypeLayout): {
        "fill": momapy.coloring.colors.medium_purple,
    },
    momapy.styling.ClassSelector(momapy.sbgn.pd.ProductionLayout): {
        "shorten": 2
    },
    momapy.styling.ParentSelector(
        momapy.styling.ClassSelector(momapy.sbgn.pd.MacromoleculeLayout),
        momapy.styling.ClassSelector(momapy.core.TextLayout),
    ): {
        "font_description": "Arial 22",
    },
}

m = momapy.sbgn.io.read_file("all.sbgn", tidy=True)
momapy.rendering.render_map(m, "styling.pdf", style_sheet=style_sheet)
