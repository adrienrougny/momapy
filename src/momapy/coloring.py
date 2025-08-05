"""Classes and objects for defining colors"""

import dataclasses
import typing


@dataclasses.dataclass(frozen=True)
class Color(object):
    """Class for colors"""

    red: int = dataclasses.field(
        metadata={"description": "The red component of the color"}
    )
    green: int = dataclasses.field(
        metadata={"description": "The green component of the color"}
    )
    blue: int = dataclasses.field(
        metadata={"description": "The blue component of the color"}
    )
    alpha: float = dataclasses.field(
        default=1.0,
        metadata={"description": "The alpha component of the color"},
    )

    def __or__(self, alpha: float) -> "Color":
        if alpha < 0 or alpha > 100:
            raise ValueError("alpha should be a number between 0 and 100")
        return dataclasses.replace(self, alpha=alpha / 100)

    def to_rgba(
        self,
        rgb_range: tuple[float, float] | tuple[int, int] = (0, 255),
        alpha_range: tuple[float, float] = (0.0, 1.0),
        rgba_range: tuple[float, float] | None = None,
    ) -> tuple[int, int, int, float]:
        """Return the color in the RBGA format"""
        if rgba_range is not None:
            rgb_range = rgba_range
            alpha_range = rgba_range
        rgb_width = rgb_range[1] - rgb_range[0]
        alpha_width = alpha_range[1] - alpha_range[0]
        red = rgb_range[0] + (self.red / 255) * rgb_width
        green = rgb_range[0] + (self.green / 255) * rgb_width
        blue = rgb_range[0] + (self.blue / 255) * rgb_width
        alpha = alpha_range[0] + self.alpha * alpha_width
        if isinstance(rgb_range[0], int):
            red = int(round(red))
            green = int(round(green))
            blue = int(round(blue))
        return (red, green, blue, alpha)

    def to_rgb(
        self, rgb_range: tuple[float, float] | tuple[int, int] = (0, 255)
    ) -> tuple[int, int, int]:
        """Return the color in the RBG format"""
        width = int(rgb_range[1] - rgb_range[0])
        red = rgb_range[0] + (self.red / 255) * width
        green = rgb_range[0] + (self.green / 255) * width
        blue = rgb_range[0] + (self.blue / 255) * width
        if isinstance(rgb_range[0], int):
            red = int(round(red))
            green = int(round(green))
            blue = int(round(blue))
        return (red, green, blue)

    def to_hex(self) -> str:
        """Return the color in the HEX format"""
        color_str = f"#{format(self.red, '02x')}{format(self.green, '02x')}{format(self.blue, '02x')}"
        return color_str

    def to_hexa(self) -> str:
        """Return the color in the HEXA format"""
        color_str = f"{self.to_hex()}{format(int(self.alpha * 255), '02x')}"
        return color_str

    def with_alpha(
        self, alpha: float, alpha_range: tuple[float, float] = (0, 1)
    ) -> typing.Self:
        """Return the a copy of the color with its alpha component set to the given number"""
        alpha_width = alpha_range[1] - alpha_range[0]
        return dataclasses.replace(
            self, alpha=alpha_range[0] + alpha * alpha_width
        )

    @classmethod
    def from_rgba(
        cls, red: int, green: int, blue: int, alpha: float
    ) -> typing.Self:
        """Return a color from its RGBA components"""
        return cls(red, green, blue, alpha)

    @classmethod
    def from_rgb(cls, red: int, green: int, blue: int):
        """Return a color from its RGB components"""
        return cls(red, green, blue)

    @classmethod
    def from_hex(cls, color_str: str):
        """Return a color from its HEX value"""
        color_str = color_str.lstrip("#")
        if len(color_str) != 6:
            raise ValueError(f"invalid hexadecimal RBG value {color_str}")
        red = int(color_str[:2], 16)
        green = int(color_str[2:4], 16)
        blue = int(color_str[4:6], 16)
        return cls(red, green, blue)

    @classmethod
    def from_hexa(cls, color_str):
        """Return a color from its HEXA value"""
        color_str = color_str.lstrip("#")
        if len(color_str) != 8:
            raise ValueError(f"invalid hexadecimal RBGA value {color_str}")
        red = int(color_str[:2], 16)
        green = int(color_str[2:4], 16)
        blue = int(color_str[4:6], 16)
        alpha = int(color_str[6:], 16) / 255
        return cls(red, green, blue, alpha)


def list_colors():
    """List all available named colors"""
    return [
        (color_name, color)
        for color_name, color in globals().items()
        if isinstance(color, Color)
    ]


def print_colors():
    """Print all available named colors"""
    for color_name, color in list_colors():
        print(f"\x1b[38;2;{color.red};{color.green};{color.blue}m{color_name}")


def has_color(color_name):
    """Return `true` if a color with the given name is available, `false` otherwise"""
    for color_name2, color in globals().items():
        if isinstance(color, Color) and color_name2 == color_name:
            return True
    return False


maroon = Color.from_rgb(128, 0, 0)
"""The color <span style="color:maroon">maroon</span> | <span style="color:maroon;background-color:black">maroon</span>"""
darkred = Color.from_rgb(139, 0, 0)
"""The color <span style="color:darkred">darkred</span> | <span style="color:darkred;background-color:black">darkred</span>"""
brown = Color.from_rgb(165, 42, 42)
"""The color <span style="color:brown">brown</span> | <span style="color:brown;background-color:black">brown</span>"""
firebrick = Color.from_rgb(178, 34, 34)
"""The color <span style="color:firebrick">firebrick</span> | <span style="color:firebrick;background-color:black">firebrick</span>"""
crimson = Color.from_rgb(220, 20, 60)
"""The color <span style="color:crimson">crimson</span> | <span style="color:crimson;background-color:black">crimson</span>"""
red = Color.from_rgb(255, 0, 0)
"""The color <span style="color:red">red</span> | <span style="color:red;background-color:black">red</span>"""
tomato = Color.from_rgb(255, 99, 71)
"""The color <span style="color:tomato">tomato</span> | <span style="color:tomato;background-color:black">tomato</span>"""
coral = Color.from_rgb(255, 127, 80)
"""The color <span style="color:coral">coral</span> | <span style="color:coral;background-color:black">coral</span>"""
indianred = Color.from_rgb(205, 92, 92)
"""The color <span style="color:indianred">indianred</span> | <span style="color:indianred;background-color:black">indianred</span>"""
lightcoral = Color.from_rgb(240, 128, 128)
"""The color <span style="color:lightcoral">lightcoral</span> | <span style="color:lightcoral;background-color:black">lightcoral</span>"""
darksalmon = Color.from_rgb(233, 150, 122)
"""The color <span style="color:darksalmon">darksalmon</span> | <span style="color:darksalmon;background-color:black">darksalmon</span>"""
salmon = Color.from_rgb(250, 128, 114)
"""The color <span style="color:salmon">salmon</span> | <span style="color:salmon;background-color:black">salmon</span>"""
lightsalmon = Color.from_rgb(255, 160, 122)
"""The color <span style="color:lightsalmon">lightsalmon</span> | <span style="color:lightsalmon;background-color:black">lightsalmon</span>"""
orangered = Color.from_rgb(255, 69, 0)
"""The color <span style="color:orangered">orangered</span> | <span style="color:orangered;background-color:black">orangered</span>"""
darkorange = Color.from_rgb(255, 140, 0)
"""The color <span style="color:darkorange">darkorange</span> | <span style="color:darkorange;background-color:black">darkorange</span>"""
orange = Color.from_rgb(255, 165, 0)
"""The color <span style="color:orange">orange</span> | <span style="color:orange;background-color:black">orange</span>"""
gold = Color.from_rgb(255, 215, 0)
"""The color <span style="color:gold">gold</span> | <span style="color:gold;background-color:black">gold</span>"""
darkgoldenrod = Color.from_rgb(184, 134, 11)
"""The color <span style="color:darkgoldenrod">darkgoldenrod</span> | <span style="color:darkgoldenrod;background-color:black">darkgoldenrod</span>"""
goldenrod = Color.from_rgb(218, 165, 32)
"""The color <span style="color:goldenrod">goldenrod</span> | <span style="color:goldenrod;background-color:black">goldenrod</span>"""
palegoldenrod = Color.from_rgb(238, 232, 170)
"""The color <span style="color:palegoldenrod">palegoldenrod</span> | <span style="color:palegoldenrod;background-color:black">palegoldenrod</span>"""
darkkhaki = Color.from_rgb(189, 183, 107)
"""The color <span style="color:darkkhaki">darkkhaki</span> | <span style="color:darkkhaki;background-color:black">darkkhaki</span>"""
khaki = Color.from_rgb(240, 230, 140)
"""The color <span style="color:khaki">khaki</span> | <span style="color:khaki;background-color:black">khaki</span>"""
olive = Color.from_rgb(128, 128, 0)
"""The color <span style="color:olive">olive</span> | <span style="color:olive;background-color:black">olive</span>"""
yellow = Color.from_rgb(255, 255, 0)
"""The color <span style="color:yellow">yellow</span> | <span style="color:yellow;background-color:black">yellow</span>"""
yellowgreen = Color.from_rgb(154, 205, 50)
"""The color <span style="color:yellowgreen">yellowgreen</span> | <span style="color:yellowgreen;background-color:black">yellowgreen</span>"""
darkolivegreen = Color.from_rgb(85, 107, 47)
"""The color <span style="color:darkolivegreen">darkolivegreen</span> | <span style="color:darkolivegreen;background-color:black">darkolivegreen</span>"""
olivedrab = Color.from_rgb(107, 142, 35)
"""The color <span style="color:olivedrab">olivedrab</span> | <span style="color:olivedrab;background-color:black">olivedrab</span>"""
lawngreen = Color.from_rgb(124, 252, 0)
"""The color <span style="color:lawngreen">lawngreen</span> | <span style="color:lawngreen;background-color:black">lawngreen</span>"""
chartreuse = Color.from_rgb(127, 255, 0)
"""The color <span style="color:chartreuse">chartreuse</span> | <span style="color:chartreuse;background-color:black">chartreuse</span>"""
greenyellow = Color.from_rgb(173, 255, 47)
"""The color <span style="color:greenyellow">greenyellow</span> | <span style="color:greenyellow;background-color:black">greenyellow</span>"""
darkgreen = Color.from_rgb(0, 100, 0)
"""The color <span style="color:darkgreen">darkgreen</span> | <span style="color:darkgreen;background-color:black">darkgreen</span>"""
green = Color.from_rgb(0, 128, 0)
"""The color <span style="color:green">green</span> | <span style="color:green;background-color:black">green</span>"""
forestgreen = Color.from_rgb(34, 139, 34)
"""The color <span style="color:forestgreen">forestgreen</span> | <span style="color:forestgreen;background-color:black">forestgreen</span>"""
lime = Color.from_rgb(0, 255, 0)
"""The color <span style="color:lime">lime</span> | <span style="color:lime;background-color:black">lime</span>"""
limegreen = Color.from_rgb(50, 205, 50)
"""The color <span style="color:limegreen">limegreen</span> | <span style="color:limegreen;background-color:black">limegreen</span>"""
lightgreen = Color.from_rgb(144, 238, 144)
"""The color <span style="color:lightgreen">lightgreen</span> | <span style="color:lightgreen;background-color:black">lightgreen</span>"""
palegreen = Color.from_rgb(152, 251, 152)
"""The color <span style="color:palegreen">palegreen</span> | <span style="color:palegreen;background-color:black">palegreen</span>"""
darkseagreen = Color.from_rgb(143, 188, 143)
"""The color <span style="color:darkseagreen">darkseagreen</span> | <span style="color:darkseagreen;background-color:black">darkseagreen</span>"""
mediumspringgreen = Color.from_rgb(0, 250, 154)
"""The color <span style="color:mediumspringgreen">mediumspringgreen</span> | <span style="color:mediumspringgreen;background-color:black">mediumspringgreen</span>"""
springgreen = Color.from_rgb(0, 255, 127)
"""The color <span style="color:springgreen">springgreen</span> | <span style="color:springgreen;background-color:black">springgreen</span>"""
seagreen = Color.from_rgb(46, 139, 87)
"""The color <span style="color:seagreen">seagreen</span> | <span style="color:seagreen;background-color:black">seagreen</span>"""
mediumaquamarine = Color.from_rgb(102, 205, 170)
"""The color <span style="color:mediumaquamarine">mediumaquamarine</span> | <span style="color:mediumaquamarine;background-color:black">mediumaquamarine</span>"""
mediumseagreen = Color.from_rgb(60, 179, 113)
"""The color <span style="color:mediumseagreen">mediumseagreen</span> | <span style="color:mediumseagreen;background-color:black">mediumseagreen</span>"""
lightseagreen = Color.from_rgb(32, 178, 170)
"""The color <span style="color:lightseagreen">lightseagreen</span> | <span style="color:lightseagreen;background-color:black">lightseagreen</span>"""
darkslategray = Color.from_rgb(47, 79, 79)
"""The color <span style="color:darkslategray">darkslategray</span> | <span style="color:darkslategray;background-color:black">darkslategray</span>"""
teal = Color.from_rgb(0, 128, 128)
"""The color <span style="color:teal">teal</span> | <span style="color:teal;background-color:black">teal</span>"""
darkcyan = Color.from_rgb(0, 139, 139)
"""The color <span style="color:darkcyan">darkcyan</span> | <span style="color:darkcyan;background-color:black">darkcyan</span>"""
aqua = Color.from_rgb(0, 255, 255)
"""The color <span style="color:aqua">aqua</span> | <span style="color:aqua;background-color:black">aqua</span>"""
cyan = Color.from_rgb(0, 255, 255)
"""The color <span style="color:cyan">cyan</span> | <span style="color:cyan;background-color:black">cyan</span>"""
lightcyan = Color.from_rgb(224, 255, 255)
"""The color <span style="color:lightcyan">lightcyan</span> | <span style="color:lightcyan;background-color:black">lightcyan</span>"""
darkturquoise = Color.from_rgb(0, 206, 209)
"""The color <span style="color:darkturquoise">darkturquoise</span> | <span style="color:darkturquoise;background-color:black">darkturquoise</span>"""
turquoise = Color.from_rgb(64, 224, 208)
"""The color <span style="color:turquoise">turquoise</span> | <span style="color:turquoise;background-color:black">turquoise</span>"""
mediumturquoise = Color.from_rgb(72, 209, 204)
"""The color <span style="color:mediumturquoise">mediumturquoise</span> | <span style="color:mediumturquoise;background-color:black">mediumturquoise</span>"""
paleturquoise = Color.from_rgb(175, 238, 238)
"""The color <span style="color:paleturquoise">paleturquoise</span> | <span style="color:paleturquoise;background-color:black">paleturquoise</span>"""
aquamarine = Color.from_rgb(127, 255, 212)
"""The color <span style="color:aquamarine">aquamarine</span> | <span style="color:aquamarine;background-color:black">aquamarine</span>"""
powderblue = Color.from_rgb(176, 224, 230)
"""The color <span style="color:powderblue">powderblue</span> | <span style="color:powderblue;background-color:black">powderblue</span>"""
cadetblue = Color.from_rgb(95, 158, 160)
"""The color <span style="color:cadetblue">cadetblue</span> | <span style="color:cadetblue;background-color:black">cadetblue</span>"""
steelblue = Color.from_rgb(70, 130, 180)
"""The color <span style="color:steelblue">steelblue</span> | <span style="color:steelblue;background-color:black">steelblue</span>"""
cornflowerblue = Color.from_rgb(100, 149, 237)
"""The color <span style="color:cornflowerblue">cornflowerblue</span> | <span style="color:cornflowerblue;background-color:black">cornflowerblue</span>"""
deepskyblue = Color.from_rgb(0, 191, 255)
"""The color <span style="color:deepskyblue">deepskyblue</span> | <span style="color:deepskyblue;background-color:black">deepskyblue</span>"""
dodgerblue = Color.from_rgb(30, 144, 255)
"""The color <span style="color:dodgerblue">dodgerblue</span> | <span style="color:dodgerblue;background-color:black">dodgerblue</span>"""
lightblue = Color.from_rgb(173, 216, 230)
"""The color <span style="color:lightblue">lightblue</span> | <span style="color:lightblue;background-color:black">lightblue</span>"""
skyblue = Color.from_rgb(135, 206, 235)
"""The color <span style="color:skyblue">skyblue</span> | <span style="color:skyblue;background-color:black">skyblue</span>"""
lightskyblue = Color.from_rgb(135, 206, 250)
"""The color <span style="color:lightskyblue">lightskyblue</span> | <span style="color:lightskyblue;background-color:black">lightskyblue</span>"""
midnightblue = Color.from_rgb(25, 25, 112)
"""The color <span style="color:midnightblue">midnightblue</span> | <span style="color:midnightblue;background-color:black">midnightblue</span>"""
navy = Color.from_rgb(0, 0, 128)
"""The color <span style="color:navy">navy</span> | <span style="color:navy;background-color:black">navy</span>"""
darkblue = Color.from_rgb(0, 0, 139)
"""The color <span style="color:darkblue">darkblue</span> | <span style="color:darkblue;background-color:black">darkblue</span>"""
mediumblue = Color.from_rgb(0, 0, 205)
"""The color <span style="color:mediumblue">mediumblue</span> | <span style="color:mediumblue;background-color:black">mediumblue</span>"""
blue = Color.from_rgb(0, 0, 255)
"""The color <span style="color:blue">blue</span> | <span style="color:blue;background-color:black">blue</span>"""
royalblue = Color.from_rgb(65, 105, 225)
"""The color <span style="color:royalblue">royalblue</span> | <span style="color:royalblue;background-color:black">royalblue</span>"""
blueviolet = Color.from_rgb(138, 43, 226)
"""The color <span style="color:blueviolet">blueviolet</span> | <span style="color:blueviolet;background-color:black">blueviolet</span>"""
indigo = Color.from_rgb(75, 0, 130)
"""The color <span style="color:indigo">indigo</span> | <span style="color:indigo;background-color:black">indigo</span>"""
darkslateblue = Color.from_rgb(72, 61, 139)
"""The color <span style="color:darkslateblue">darkslateblue</span> | <span style="color:darkslateblue;background-color:black">darkslateblue</span>"""
slateblue = Color.from_rgb(106, 90, 205)
"""The color <span style="color:slateblue">slateblue</span> | <span style="color:slateblue;background-color:black">slateblue</span>"""
mediumslateblue = Color.from_rgb(123, 104, 238)
"""The color <span style="color:mediumslateblue">mediumslateblue</span> | <span style="color:mediumslateblue;background-color:black">mediumslateblue</span>"""
mediumpurple = Color.from_rgb(147, 112, 219)
"""The color <span style="color:mediumpurple">mediumpurple</span> | <span style="color:mediumpurple;background-color:black">mediumpurple</span>"""
darkmagenta = Color.from_rgb(139, 0, 139)
"""The color <span style="color:darkmagenta">darkmagenta</span> | <span style="color:darkmagenta;background-color:black">darkmagenta</span>"""
darkviolet = Color.from_rgb(148, 0, 211)
"""The color <span style="color:darkviolet">darkviolet</span> | <span style="color:darkviolet;background-color:black">darkviolet</span>"""
darkorchid = Color.from_rgb(153, 50, 204)
"""The color <span style="color:darkorchid">darkorchid</span> | <span style="color:darkorchid;background-color:black">darkorchid</span>"""
mediumorchid = Color.from_rgb(186, 85, 211)
"""The color <span style="color:mediumorchid">mediumorchid</span> | <span style="color:mediumorchid;background-color:black">mediumorchid</span>"""
purple = Color.from_rgb(128, 0, 128)
"""The color <span style="color:purple">purple</span> | <span style="color:purple;background-color:black">purple</span>"""
thistle = Color.from_rgb(216, 191, 216)
"""The color <span style="color:thistle">thistle</span> | <span style="color:thistle;background-color:black">thistle</span>"""
plum = Color.from_rgb(221, 160, 221)
"""The color <span style="color:plum">plum</span> | <span style="color:plum;background-color:black">plum</span>"""
violet = Color.from_rgb(238, 130, 238)
"""The color <span style="color:violet">violet</span> | <span style="color:violet;background-color:black">violet</span>"""
magenta = Color.from_rgb(255, 0, 255)
"""The color <span style="color:magenta">magenta</span> | <span style="color:magenta;background-color:black">magenta</span>"""
fuchsia = Color.from_rgb(255, 0, 255)
"""The color <span style="color:fuchsia">fuchsia</span> | <span style="color:fuchsia;background-color:black">fuchsia</span>"""
orchid = Color.from_rgb(218, 112, 214)
"""The color <span style="color:orchid">orchid</span> | <span style="color:orchid;background-color:black">orchid</span>"""
mediumvioletred = Color.from_rgb(199, 21, 133)
"""The color <span style="color:mediumvioletred">mediumvioletred</span> | <span style="color:mediumvioletred;background-color:black">mediumvioletred</span>"""
palevioletred = Color.from_rgb(219, 112, 147)
"""The color <span style="color:palevioletred">palevioletred</span> | <span style="color:palevioletred;background-color:black">palevioletred</span>"""
deeppink = Color.from_rgb(255, 20, 147)
"""The color <span style="color:deeppink">deeppink</span> | <span style="color:deeppink;background-color:black">deeppink</span>"""
hotpink = Color.from_rgb(255, 105, 180)
"""The color <span style="color:hotpink">hotpink</span> | <span style="color:hotpink;background-color:black">hotpink</span>"""
lightpink = Color.from_rgb(255, 182, 193)
"""The color <span style="color:lightpink">lightpink</span> | <span style="color:lightpink;background-color:black">lightpink</span>"""
pink = Color.from_rgb(255, 192, 203)
"""The color <span style="color:pink">pink</span> | <span style="color:pink;background-color:black">pink</span>"""
antiquewhite = Color.from_rgb(250, 235, 215)
"""The color <span style="color:antiquewhite">antiquewhite</span> | <span style="color:antiquewhite;background-color:black">antiquewhite</span>"""
beige = Color.from_rgb(245, 245, 220)
"""The color <span style="color:beige">beige</span> | <span style="color:beige;background-color:black">beige</span>"""
bisque = Color.from_rgb(255, 228, 196)
"""The color <span style="color:bisque">bisque</span> | <span style="color:bisque;background-color:black">bisque</span>"""
blanchedalmond = Color.from_rgb(255, 235, 205)
"""The color <span style="color:blanchedalmond">blanchedalmond</span> | <span style="color:blanchedalmond;background-color:black">blanchedalmond</span>"""
wheat = Color.from_rgb(245, 222, 179)
"""The color <span style="color:wheat">wheat</span> | <span style="color:wheat;background-color:black">wheat</span>"""
cornsilk = Color.from_rgb(255, 248, 220)
"""The color <span style="color:cornsilk">cornsilk</span> | <span style="color:cornsilk;background-color:black">cornsilk</span>"""
lemonchiffon = Color.from_rgb(255, 250, 205)
"""The color <span style="color:lemonchiffon">lemonchiffon</span> | <span style="color:lemonchiffon;background-color:black">lemonchiffon</span>"""
lightgoldenrodyellow = Color.from_rgb(250, 250, 210)
"""The color <span style="color:lightgoldenrodyellow">lightgoldenrodyellow</span> | <span style="color:lightgoldenrodyellow;background-color:black">lightgoldenrodyellow</span>"""
lightyellow = Color.from_rgb(255, 255, 224)
"""The color <span style="color:lightyellow">lightyellow</span> | <span style="color:lightyellow;background-color:black">lightyellow</span>"""
saddlebrown = Color.from_rgb(139, 69, 19)
"""The color <span style="color:saddlebrown">saddlebrown</span> | <span style="color:saddlebrown;background-color:black">saddlebrown</span>"""
sienna = Color.from_rgb(160, 82, 45)
"""The color <span style="color:sienna">sienna</span> | <span style="color:sienna;background-color:black">sienna</span>"""
chocolate = Color.from_rgb(210, 105, 30)
"""The color <span style="color:chocolate">chocolate</span> | <span style="color:chocolate;background-color:black">chocolate</span>"""
peru = Color.from_rgb(205, 133, 63)
"""The color <span style="color:peru">peru</span> | <span style="color:peru;background-color:black">peru</span>"""
sandybrown = Color.from_rgb(244, 164, 96)
"""The color <span style="color:sandybrown">sandybrown</span> | <span style="color:sandybrown;background-color:black">sandybrown</span>"""
burlywood = Color.from_rgb(222, 184, 135)
"""The color <span style="color:burlywood">burlywood</span> | <span style="color:burlywood;background-color:black">burlywood</span>"""
tan = Color.from_rgb(210, 180, 140)
"""The color <span style="color:tan">tan</span> | <span style="color:tan;background-color:black">tan</span>"""
rosybrown = Color.from_rgb(188, 143, 143)
"""The color <span style="color:rosybrown">rosybrown</span> | <span style="color:rosybrown;background-color:black">rosybrown</span>"""
moccasin = Color.from_rgb(255, 228, 181)
"""The color <span style="color:moccasin">moccasin</span> | <span style="color:moccasin;background-color:black">moccasin</span>"""
navajowhite = Color.from_rgb(255, 222, 173)
"""The color <span style="color:navajowhite">navajowhite</span> | <span style="color:navajowhite;background-color:black">navajowhite</span>"""
peachpuff = Color.from_rgb(255, 218, 185)
"""The color <span style="color:peachpuff">peachpuff</span> | <span style="color:peachpuff;background-color:black">peachpuff</span>"""
mistyrose = Color.from_rgb(255, 228, 225)
"""The color <span style="color:mistyrose">mistyrose</span> | <span style="color:mistyrose;background-color:black">mistyrose</span>"""
lavenderblush = Color.from_rgb(255, 240, 245)
"""The color <span style="color:lavenderblush">lavenderblush</span> | <span style="color:lavenderblush;background-color:black">lavenderblush</span>"""
linen = Color.from_rgb(250, 240, 230)
"""The color <span style="color:linen">linen</span> | <span style="color:linen;background-color:black">linen</span>"""
oldlace = Color.from_rgb(253, 245, 230)
"""The color <span style="color:oldlace">oldlace</span> | <span style="color:oldlace;background-color:black">oldlace</span>"""
papayawhip = Color.from_rgb(255, 239, 213)
"""The color <span style="color:papayawhip">papayawhip</span> | <span style="color:papayawhip;background-color:black">papayawhip</span>"""
seashell = Color.from_rgb(255, 245, 238)
"""The color <span style="color:seashell">seashell</span> | <span style="color:seashell;background-color:black">seashell</span>"""
mintcream = Color.from_rgb(245, 255, 250)
"""The color <span style="color:mintcream">mintcream</span> | <span style="color:mintcream;background-color:black">mintcream</span>"""
slategray = Color.from_rgb(112, 128, 144)
"""The color <span style="color:slategray">slategray</span> | <span style="color:slategray;background-color:black">slategray</span>"""
lightslategray = Color.from_rgb(119, 136, 153)
"""The color <span style="color:lightslategray">lightslategray</span> | <span style="color:lightslategray;background-color:black">lightslategray</span>"""
lightsteelblue = Color.from_rgb(176, 196, 222)
"""The color <span style="color:lightsteelblue">lightsteelblue</span> | <span style="color:lightsteelblue;background-color:black">lightsteelblue</span>"""
lavender = Color.from_rgb(230, 230, 250)
"""The color <span style="color:lavender">lavender</span> | <span style="color:lavender;background-color:black">lavender</span>"""
floralwhite = Color.from_rgb(255, 250, 240)
"""The color <span style="color:floralwhite">floralwhite</span> | <span style="color:floralwhite;background-color:black">floralwhite</span>"""
aliceblue = Color.from_rgb(240, 248, 255)
"""The color <span style="color:aliceblue">aliceblue</span> | <span style="color:aliceblue;background-color:black">aliceblue</span>"""
ghostwhite = Color.from_rgb(248, 248, 255)
"""The color <span style="color:ghostwhite">ghostwhite</span> | <span style="color:ghostwhite;background-color:black">ghostwhite</span>"""
honeydew = Color.from_rgb(240, 255, 240)
"""The color <span style="color:honeydew">honeydew</span> | <span style="color:honeydew;background-color:black">honeydew</span>"""
ivory = Color.from_rgb(255, 255, 240)
"""The color <span style="color:ivory">ivory</span> | <span style="color:ivory;background-color:black">ivory</span>"""
azure = Color.from_rgb(240, 255, 255)
"""The color <span style="color:azure">azure</span> | <span style="color:azure;background-color:black">azure</span>"""
snow = Color.from_rgb(255, 250, 250)
"""The color <span style="color:snow">snow</span> | <span style="color:snow;background-color:black">snow</span>"""
black = Color.from_rgb(0, 0, 0)
"""The color <span style="color:black">black</span> | <span style="color:black;background-color:black">black</span>"""
dimgray = Color.from_rgb(105, 105, 105)
"""The color <span style="color:dimgray">dimgray</span> | <span style="color:dimgray;background-color:black">dimgray</span>"""
dimgrey = Color.from_rgb(105, 105, 105)
"""The color <span style="color:dimgrey">dimgrey</span> | <span style="color:dimgrey;background-color:black">dimgrey</span>"""
gray = Color.from_rgb(128, 128, 128)
"""The color <span style="color:gray">gray</span> | <span style="color:gray;background-color:black">gray</span>"""
grey = Color.from_rgb(128, 128, 128)
"""The color <span style="color:grey">grey</span> | <span style="color:grey;background-color:black">grey</span>"""
darkgray = Color.from_rgb(169, 169, 169)
"""The color <span style="color:darkgray">darkgray</span> | <span style="color:darkgray;background-color:black">darkgray</span>"""
darkgrey = Color.from_rgb(169, 169, 169)
"""The color <span style="color:darkgrey">darkgrey</span> | <span style="color:darkgrey;background-color:black">darkgrey</span>"""
silver = Color.from_rgb(192, 192, 192)
"""The color <span style="color:silver">silver</span> | <span style="color:silver;background-color:black">silver</span>"""
lightgray = Color.from_rgb(211, 211, 211)
"""The color <span style="color:lightgray">lightgray</span> | <span style="color:lightgray;background-color:black">lightgray</span>"""
lightgrey = Color.from_rgb(211, 211, 211)
"""The color <span style="color:lightgrey">lightgrey</span> | <span style="color:lightgrey;background-color:black">lightgrey</span>"""
gainsboro = Color.from_rgb(220, 220, 220)
"""The color <span style="color:gainsboro">gainsboro</span> | <span style="color:gainsboro;background-color:black">gainsboro</span>"""
whitesmoke = Color.from_rgb(245, 245, 245)
"""The color <span style="color:whitesmoke">whitesmoke</span> | <span style="color:whitesmoke;background-color:black">whitesmoke</span>"""
white = Color.from_rgb(255, 255, 255)
"""The color <span style="color:white">white</span> | <span style="color:white;background-color:black">white</span>"""
