import momapy.sbgn.io
import momapy.rendering.skia
import momapy.rendering.cairo
import momapy.rendering.core

style_sheet = []
# style_sheet.append("../../momapy/sbgn/styling/default.css")
style_sheet.append("../../momapy/sbgn/styling/vanted.css")

style_sheet.append("../../momapy/sbgn/styling/default_colorscheme.css")

# style_sheet.append("../../momapy/sbgn/styling/shadows.css")

files = [
    {
        "input_file": "all_pd.sbgn",
        "svg_file": "all_pd.svg",
        "pdf_file": "all_pd.pdf",
    },
    {
        "input_file": "all_af.sbgn",
        "svg_file": "all_af.svg",
        "pdf_file": "all_af.pdf",
    },
]

for file in files:
    input_file = file["input_file"]
    svg_file = file["svg_file"]
    pdf_file = file["pdf_file"]
    m1 = momapy.sbgn.io.read_file(
        input_file, tidy=False, style_sheet=style_sheet, return_builder=True
    )
    momapy.rendering.core.render_map(
        m1, pdf_file, to_top_left=True, renderer="skia", format_="pdf"
    )
