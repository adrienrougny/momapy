from momapy.sbgn.io import read_file
from momapy.rendering import render_map

file_1 = "p1.sbgn"
file_2 = "p2.sbgn"

map1 = read_file(file_1)
map2 = read_file(file_2)

assert map1.model == map2.model
assert map1.layout != map2.layout

render_map(map1, "p1.pdf")
render_map(map2, "p2.pdf")
