import momapy.core

l = momapy.core.TextLayout(
    text="Ajkfd fdjkjfdlk fdkjfdl\nfjdkfjdk fjdkfjdkf djkfjdkf\nfjdkfjdkf jdfkjkfdj jkfdjkfd",
    font_family="Arial",
    font_size=16.0,
    position=momapy.geometry.Point(0, 0),
)

for i in range(100000):
    de = l.drawing_elements()
    bbox = l.ink_bbox()
