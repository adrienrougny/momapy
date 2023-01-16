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


def rgba(red, green, blue, alpha):
    return Color(red, green, blue, alpha)


def rgb(red, green, blue):
    return Color(red, green, blue)


def hex(string):
    string.lstrip("#")
    if len(string) != 6:
        raise ValueError("invalid hexadecimal RBG value")
    red = int(string[:2], 16)
    green = int(string[2:4], 16)
    blue = int(string[4:6], 16)
    return rgb(red, green, blue)


def hexa(string):
    if string.startswith("#"):
        string = string[1:]
    if len(string) != 8:
        raise ValueError("invalid hexadecimal RBGA value")
    red = int(string[:2], 16)
    green = int(string[2:4], 16)
    blue = int(string[4:6], 16)
    alpha = int(string[6:], 16) / 255
    return rgba(red, green, blue, alpha)


def list_colors():
    for color_name in dir(colors):
        if not color_name.startswith("__"):
            color = getattr(colors, color_name)
            print(
                f"\x1b[38;2;{color.red};{color.green};{color.blue}m{color_name}"
            )


class colors(object):
    maroon = rgb(128, 0, 0)
    darkred = rgb(139, 0, 0)
    brown = rgb(165, 42, 42)
    firebrick = rgb(178, 34, 34)
    crimson = rgb(220, 20, 60)
    red = rgb(255, 0, 0)
    tomato = rgb(255, 99, 71)
    coral = rgb(255, 127, 80)
    indianred = rgb(205, 92, 92)
    lightcoral = rgb(240, 128, 128)
    darksalmon = rgb(233, 150, 122)
    salmon = rgb(250, 128, 114)
    lightsalmon = rgb(255, 160, 122)
    orangered = rgb(255, 69, 0)
    darkorange = rgb(255, 140, 0)
    orange = rgb(255, 165, 0)
    gold = rgb(255, 215, 0)
    darkgoldenrod = rgb(184, 134, 11)
    goldenrod = rgb(218, 165, 32)
    palegoldenrod = rgb(238, 232, 170)
    darkkhaki = rgb(189, 183, 107)
    khaki = rgb(240, 230, 140)
    olive = rgb(128, 128, 0)
    yellow = rgb(255, 255, 0)
    yellowgreen = rgb(154, 205, 50)
    darkolivegreen = rgb(85, 107, 47)
    olivedrab = rgb(107, 142, 35)
    lawngreen = rgb(124, 252, 0)
    chartreuse = rgb(127, 255, 0)
    greenyellow = rgb(173, 255, 47)
    darkgreen = rgb(0, 100, 0)
    green = rgb(0, 128, 0)
    forestgreen = rgb(34, 139, 34)
    lime = rgb(0, 255, 0)
    limegreen = rgb(50, 205, 50)
    lightgreen = rgb(144, 238, 144)
    palegreen = rgb(152, 251, 152)
    darkseagreen = rgb(143, 188, 143)
    mediumspringgreen = rgb(0, 250, 154)
    springgreen = rgb(0, 255, 127)
    seagreen = rgb(46, 139, 87)
    mediumaquamarine = rgb(102, 205, 170)
    mediumseagreen = rgb(60, 179, 113)
    lightseagreen = rgb(32, 178, 170)
    darkslategray = rgb(47, 79, 79)
    teal = rgb(0, 128, 128)
    darkcyan = rgb(0, 139, 139)
    aqua = rgb(0, 255, 255)
    cyan = rgb(0, 255, 255)
    lightcyan = rgb(224, 255, 255)
    darkturquoise = rgb(0, 206, 209)
    turquoise = rgb(64, 224, 208)
    mediumturquoise = rgb(72, 209, 204)
    paleturquoise = rgb(175, 238, 238)
    aquamarine = rgb(127, 255, 212)
    powderblue = rgb(176, 224, 230)
    cadetblue = rgb(95, 158, 160)
    steelblue = rgb(70, 130, 180)
    cornflowerblue = rgb(100, 149, 237)
    deepskyblue = rgb(0, 191, 255)
    dodgerblue = rgb(30, 144, 255)
    lightblue = rgb(173, 216, 230)
    skyblue = rgb(135, 206, 235)
    lightskyblue = rgb(135, 206, 250)
    midnightblue = rgb(25, 25, 112)
    navy = rgb(0, 0, 128)
    darkblue = rgb(0, 0, 139)
    mediumblue = rgb(0, 0, 205)
    blue = rgb(0, 0, 255)
    royalblue = rgb(65, 105, 225)
    blueviolet = rgb(138, 43, 226)
    indigo = rgb(75, 0, 130)
    darkslateblue = rgb(72, 61, 139)
    slateblue = rgb(106, 90, 205)
    mediumslateblue = rgb(123, 104, 238)
    mediumpurple = rgb(147, 112, 219)
    darkmagenta = rgb(139, 0, 139)
    darkviolet = rgb(148, 0, 211)
    darkorchid = rgb(153, 50, 204)
    mediumorchid = rgb(186, 85, 211)
    purple = rgb(128, 0, 128)
    thistle = rgb(216, 191, 216)
    plum = rgb(221, 160, 221)
    violet = rgb(238, 130, 238)
    magenta = rgb(255, 0, 255)
    fuchsia = rgb(255, 0, 255)
    orchid = rgb(218, 112, 214)
    mediumvioletred = rgb(199, 21, 133)
    palevioletred = rgb(219, 112, 147)
    deeppink = rgb(255, 20, 147)
    hotpink = rgb(255, 105, 180)
    lightpink = rgb(255, 182, 193)
    pink = rgb(255, 192, 203)
    antiquewhite = rgb(250, 235, 215)
    beige = rgb(245, 245, 220)
    bisque = rgb(255, 228, 196)
    blanchedalmond = rgb(255, 235, 205)
    wheat = rgb(245, 222, 179)
    cornsilk = rgb(255, 248, 220)
    lemonchiffon = rgb(255, 250, 205)
    lightgoldenrodyellow = rgb(250, 250, 210)
    lightyellow = rgb(255, 255, 224)
    saddlebrown = rgb(139, 69, 19)
    sienna = rgb(160, 82, 45)
    chocolate = rgb(210, 105, 30)
    peru = rgb(205, 133, 63)
    sandybrown = rgb(244, 164, 96)
    burlywood = rgb(222, 184, 135)
    tan = rgb(210, 180, 140)
    rosybrown = rgb(188, 143, 143)
    moccasin = rgb(255, 228, 181)
    navajowhite = rgb(255, 222, 173)
    peachpuff = rgb(255, 218, 185)
    mistyrose = rgb(255, 228, 225)
    lavenderblush = rgb(255, 240, 245)
    linen = rgb(250, 240, 230)
    oldlace = rgb(253, 245, 230)
    papayawhip = rgb(255, 239, 213)
    seashell = rgb(255, 245, 238)
    mintcream = rgb(245, 255, 250)
    slategray = rgb(112, 128, 144)
    lightslategray = rgb(119, 136, 153)
    lightsteelblue = rgb(176, 196, 222)
    lavender = rgb(230, 230, 250)
    floralwhite = rgb(255, 250, 240)
    aliceblue = rgb(240, 248, 255)
    ghostwhite = rgb(248, 248, 255)
    honeydew = rgb(240, 255, 240)
    ivory = rgb(255, 255, 240)
    azure = rgb(240, 255, 255)
    snow = rgb(255, 250, 250)
    black = rgb(0, 0, 0)
    dimgray = rgb(105, 105, 105)
    dimgrey = rgb(105, 105, 105)
    gray = rgb(128, 128, 128)
    grey = rgb(128, 128, 128)
    darkgray = rgb(169, 169, 169)
    darkgrey = rgb(169, 169, 169)
    silver = rgb(192, 192, 192)
    lightgray = rgb(211, 211, 211)
    lightgrey = rgb(211, 211, 211)
    gainsboro = rgb(220, 220, 220)
    whitesmoke = rgb(245, 245, 245)
    white = rgb(255, 255, 255)

    @classmethod
    def has_color(cls, color: str) -> bool:
        return hasattr(cls, color)
