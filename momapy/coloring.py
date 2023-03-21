from dataclasses import dataclass, replace


@dataclass(frozen=True)
class Color(object):
    red: float
    green: float
    blue: float
    alpha: float = 1.0

    def __or__(self, alpha: float) -> "Color":
        if alpha < 0 or alpha > 100:
            raise ValueError("alpha should be a number between 0 and 100")
        return replace(self, alpha=alpha / 100)

    def to_rgba(self, rgb_range=(0, 255), alpha_range=(0, 1), rgba_range=None):
        if rgba_range is not None:
            rgb_range = rgba_range
            alpha_range = rgba_range
        rgb_width = rgb_range[1] - rgb_range[0]
        alpha_width = alpha_range[1] - alpha_range[0]
        red = rgb_range[0] + (self.red / 255) * rgb_width
        green = rgb_range[0] + (self.green / 255) * rgb_width
        blue = rgb_range[0] + (self.blue / 255) * rgb_width
        alpha = alpha_range[0] + self.alpha * alpha_width
        return (red, green, blue, alpha)

    def to_rgb(self, rgb_range=(0, 255)):
        width = rgb_range[1] - rgb_range[0]
        red = rgb_range[0] + (self.red / 255) * width
        green = rgb_range[0] + (self.green / 255) * width
        blue = rgb_range[0] + (self.blue / 255) * width
        return (red, green, blue)

    def with_alpha(self, alpha, alpha_range=(0, 1)):
        alpha_width = alpha_range[1] - alpha_range[0]
        return replace(self, alpha=alpha_range[0] + alpha * alpha_width)

    @classmethod
    def from_rgba(cls, red, green, blue, alpha):
        return cls(red, green, blue, alpha)

    @classmethod
    def from_rgb(cls, red, green, blue):
        return cls(red, green, blue)

    @classmethod
    def from_hex(cls, string):
        string.lstrip("#")
        if len(string) != 6:
            raise ValueError("invalid hexadecimal RBG value")
        red = int(string[:2], 16)
        green = int(string[2:4], 16)
        blue = int(string[4:6], 16)
        return cls(red, green, blue)

    @classmethod
    def from_hexa(cls, string):
        if string.startswith("#"):
            string = string[1:]
        if len(string) != 8:
            raise ValueError("invalid hexadecimal RBGA value")
        red = int(string[:2], 16)
        green = int(string[2:4], 16)
        blue = int(string[4:6], 16)
        alpha = int(string[6:], 16) / 255
        return cls(red, green, blue, alpha)


def list_colors():
    for color_name, color in globals().items():
        if isinstance(color, Color):
            print(
                f"\x1b[38;2;{color.red};{color.green};{color.blue}m{color_name}"
            )


def has_color(color_name):
    for color_name2, color in globals().items():
        if isinstance(color, Color) and color_name2 == color_name:
            return True
    return False


maroon = Color.from_rgb(128, 0, 0)
darkred = Color.from_rgb(139, 0, 0)
brown = Color.from_rgb(165, 42, 42)
firebrick = Color.from_rgb(178, 34, 34)
crimson = Color.from_rgb(220, 20, 60)
red = Color.from_rgb(255, 0, 0)
tomato = Color.from_rgb(255, 99, 71)
coral = Color.from_rgb(255, 127, 80)
indianred = Color.from_rgb(205, 92, 92)
lightcoral = Color.from_rgb(240, 128, 128)
darksalmon = Color.from_rgb(233, 150, 122)
salmon = Color.from_rgb(250, 128, 114)
lightsalmon = Color.from_rgb(255, 160, 122)
orangered = Color.from_rgb(255, 69, 0)
darkorange = Color.from_rgb(255, 140, 0)
orange = Color.from_rgb(255, 165, 0)
gold = Color.from_rgb(255, 215, 0)
darkgoldenrod = Color.from_rgb(184, 134, 11)
goldenrod = Color.from_rgb(218, 165, 32)
palegoldenrod = Color.from_rgb(238, 232, 170)
darkkhaki = Color.from_rgb(189, 183, 107)
khaki = Color.from_rgb(240, 230, 140)
olive = Color.from_rgb(128, 128, 0)
yellow = Color.from_rgb(255, 255, 0)
yellowgreen = Color.from_rgb(154, 205, 50)
darkolivegreen = Color.from_rgb(85, 107, 47)
olivedrab = Color.from_rgb(107, 142, 35)
lawngreen = Color.from_rgb(124, 252, 0)
chartreuse = Color.from_rgb(127, 255, 0)
greenyellow = Color.from_rgb(173, 255, 47)
darkgreen = Color.from_rgb(0, 100, 0)
green = Color.from_rgb(0, 128, 0)
forestgreen = Color.from_rgb(34, 139, 34)
lime = Color.from_rgb(0, 255, 0)
limegreen = Color.from_rgb(50, 205, 50)
lightgreen = Color.from_rgb(144, 238, 144)
palegreen = Color.from_rgb(152, 251, 152)
darkseagreen = Color.from_rgb(143, 188, 143)
mediumspringgreen = Color.from_rgb(0, 250, 154)
springgreen = Color.from_rgb(0, 255, 127)
seagreen = Color.from_rgb(46, 139, 87)
mediumaquamarine = Color.from_rgb(102, 205, 170)
mediumseagreen = Color.from_rgb(60, 179, 113)
lightseagreen = Color.from_rgb(32, 178, 170)
darkslategray = Color.from_rgb(47, 79, 79)
teal = Color.from_rgb(0, 128, 128)
darkcyan = Color.from_rgb(0, 139, 139)
aqua = Color.from_rgb(0, 255, 255)
cyan = Color.from_rgb(0, 255, 255)
lightcyan = Color.from_rgb(224, 255, 255)
darkturquoise = Color.from_rgb(0, 206, 209)
turquoise = Color.from_rgb(64, 224, 208)
mediumturquoise = Color.from_rgb(72, 209, 204)
paleturquoise = Color.from_rgb(175, 238, 238)
aquamarine = Color.from_rgb(127, 255, 212)
powderblue = Color.from_rgb(176, 224, 230)
cadetblue = Color.from_rgb(95, 158, 160)
steelblue = Color.from_rgb(70, 130, 180)
cornflowerblue = Color.from_rgb(100, 149, 237)
deepskyblue = Color.from_rgb(0, 191, 255)
dodgerblue = Color.from_rgb(30, 144, 255)
lightblue = Color.from_rgb(173, 216, 230)
skyblue = Color.from_rgb(135, 206, 235)
lightskyblue = Color.from_rgb(135, 206, 250)
midnightblue = Color.from_rgb(25, 25, 112)
navy = Color.from_rgb(0, 0, 128)
darkblue = Color.from_rgb(0, 0, 139)
mediumblue = Color.from_rgb(0, 0, 205)
blue = Color.from_rgb(0, 0, 255)
royalblue = Color.from_rgb(65, 105, 225)
blueviolet = Color.from_rgb(138, 43, 226)
indigo = Color.from_rgb(75, 0, 130)
darkslateblue = Color.from_rgb(72, 61, 139)
slateblue = Color.from_rgb(106, 90, 205)
mediumslateblue = Color.from_rgb(123, 104, 238)
mediumpurple = Color.from_rgb(147, 112, 219)
darkmagenta = Color.from_rgb(139, 0, 139)
darkviolet = Color.from_rgb(148, 0, 211)
darkorchid = Color.from_rgb(153, 50, 204)
mediumorchid = Color.from_rgb(186, 85, 211)
purple = Color.from_rgb(128, 0, 128)
thistle = Color.from_rgb(216, 191, 216)
plum = Color.from_rgb(221, 160, 221)
violet = Color.from_rgb(238, 130, 238)
magenta = Color.from_rgb(255, 0, 255)
fuchsia = Color.from_rgb(255, 0, 255)
orchid = Color.from_rgb(218, 112, 214)
mediumvioletred = Color.from_rgb(199, 21, 133)
palevioletred = Color.from_rgb(219, 112, 147)
deeppink = Color.from_rgb(255, 20, 147)
hotpink = Color.from_rgb(255, 105, 180)
lightpink = Color.from_rgb(255, 182, 193)
pink = Color.from_rgb(255, 192, 203)
antiquewhite = Color.from_rgb(250, 235, 215)
beige = Color.from_rgb(245, 245, 220)
bisque = Color.from_rgb(255, 228, 196)
blanchedalmond = Color.from_rgb(255, 235, 205)
wheat = Color.from_rgb(245, 222, 179)
cornsilk = Color.from_rgb(255, 248, 220)
lemonchiffon = Color.from_rgb(255, 250, 205)
lightgoldenrodyellow = Color.from_rgb(250, 250, 210)
lightyellow = Color.from_rgb(255, 255, 224)
saddlebrown = Color.from_rgb(139, 69, 19)
sienna = Color.from_rgb(160, 82, 45)
chocolate = Color.from_rgb(210, 105, 30)
peru = Color.from_rgb(205, 133, 63)
sandybrown = Color.from_rgb(244, 164, 96)
burlywood = Color.from_rgb(222, 184, 135)
tan = Color.from_rgb(210, 180, 140)
rosybrown = Color.from_rgb(188, 143, 143)
moccasin = Color.from_rgb(255, 228, 181)
navajowhite = Color.from_rgb(255, 222, 173)
peachpuff = Color.from_rgb(255, 218, 185)
mistyrose = Color.from_rgb(255, 228, 225)
lavenderblush = Color.from_rgb(255, 240, 245)
linen = Color.from_rgb(250, 240, 230)
oldlace = Color.from_rgb(253, 245, 230)
papayawhip = Color.from_rgb(255, 239, 213)
seashell = Color.from_rgb(255, 245, 238)
mintcream = Color.from_rgb(245, 255, 250)
slategray = Color.from_rgb(112, 128, 144)
lightslategray = Color.from_rgb(119, 136, 153)
lightsteelblue = Color.from_rgb(176, 196, 222)
lavender = Color.from_rgb(230, 230, 250)
floralwhite = Color.from_rgb(255, 250, 240)
aliceblue = Color.from_rgb(240, 248, 255)
ghostwhite = Color.from_rgb(248, 248, 255)
honeydew = Color.from_rgb(240, 255, 240)
ivory = Color.from_rgb(255, 255, 240)
azure = Color.from_rgb(240, 255, 255)
snow = Color.from_rgb(255, 250, 250)
black = Color.from_rgb(0, 0, 0)
dimgray = Color.from_rgb(105, 105, 105)
dimgrey = Color.from_rgb(105, 105, 105)
gray = Color.from_rgb(128, 128, 128)
grey = Color.from_rgb(128, 128, 128)
darkgray = Color.from_rgb(169, 169, 169)
darkgrey = Color.from_rgb(169, 169, 169)
silver = Color.from_rgb(192, 192, 192)
lightgray = Color.from_rgb(211, 211, 211)
lightgrey = Color.from_rgb(211, 211, 211)
gainsboro = Color.from_rgb(220, 220, 220)
whitesmoke = Color.from_rgb(245, 245, 245)
white = Color.from_rgb(255, 255, 255)
