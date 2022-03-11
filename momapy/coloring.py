from dataclasses import dataclass, replace
from enum import Enum

@dataclass(frozen=True)
class Color(object):
    red: float
    green: float
    blue: float
    alpha: float = 1

    def __or__(self, alpha: float) -> "Color":
        if n < 0 or n > 100:
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
        alpha = alpha_range[0] + self.alpha * rgb_width
        return (red, green, blue, alpha)

    def to_rgb(self, rgb_range=(0, 255)):
        width = rgba_range[1] - rgba_range[0]
        red = rgba_range[0] + (self.red / 255) * width
        green = rgba_range[0] + (self.green / 255) * width
        blue = rgba_range[0] + (self.blue / 255) * width
        return (red, green, blue)

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
            print(f"\x1b[38;2;{color.red};{color.green};{color.blue}m{color_name}")

class colors(object):
    maroon = rgb(128,0,0)
    dark_red = rgb(139,0,0)
    brown = rgb(165,42,42)
    firebrick = rgb(178,34,34)
    crimson = rgb(220,20,60)
    red = rgb(255,0,0)
    tomato = rgb(255,99,71)
    coral = rgb(255,127,80)
    indian_red = rgb(205,92,92)
    light_coral = rgb(240,128,128)
    dark_salmon = rgb(233,150,122)
    salmon = rgb(250,128,114)
    light_salmon = rgb(255,160,122)
    orange_red = rgb(255,69,0)
    dark_orange = rgb(255,140,0)
    orange = rgb(255,165,0)
    gold = rgb(255,215,0)
    dark_golden_rod = rgb(184,134,11)
    golden_rod = rgb(218,165,32)
    pale_golden_rod = rgb(238,232,170)
    dark_khaki = rgb(189,183,107)
    khaki = rgb(240,230,140)
    olive = rgb(128,128,0)
    yellow = rgb(255,255,0)
    yellow_green = rgb(154,205,50)
    dark_olive_green = rgb(85,107,47)
    olive_drab = rgb(107,142,35)
    lawn_green = rgb(124,252,0)
    chartreuse = rgb(127,255,0)
    green_yellow = rgb(173,255,47)
    dark_green = rgb(0,100,0)
    green = rgb(0,128,0)
    forest_green = rgb(34,139,34)
    lime = rgb(0,255,0)
    lime_green = rgb(50,205,50)
    light_green = rgb(144,238,144)
    pale_green = rgb(152,251,152)
    dark_sea_green = rgb(143,188,143)
    medium_spring_green = rgb(0,250,154)
    spring_green = rgb(0,255,127)
    sea_green = rgb(46,139,87)
    medium_aqua_marine = rgb(102,205,170)
    medium_sea_green = rgb(60,179,113)
    light_sea_green = rgb(32,178,170)
    dark_slate_gray = rgb(47,79,79)
    teal = rgb(0,128,128)
    dark_cyan = rgb(0,139,139)
    aqua = rgb(0,255,255)
    cyan = rgb(0,255,255)
    light_cyan = rgb(224,255,255)
    dark_turquoise = rgb(0,206,209)
    turquoise = rgb(64,224,208)
    medium_turquoise = rgb(72,209,204)
    pale_turquoise = rgb(175,238,238)
    aqua_marine = rgb(127,255,212)
    powder_blue = rgb(176,224,230)
    cadet_blue = rgb(95,158,160)
    steel_blue = rgb(70,130,180)
    corn_flower_blue = rgb(100,149,237)
    deep_sky_blue = rgb(0,191,255)
    dodger_blue = rgb(30,144,255)
    light_blue = rgb(173,216,230)
    sky_blue = rgb(135,206,235)
    light_sky_blue = rgb(135,206,250)
    midnight_blue = rgb(25,25,112)
    navy = rgb(0,0,128)
    dark_blue = rgb(0,0,139)
    medium_blue = rgb(0,0,205)
    blue = rgb(0,0,255)
    royal_blue = rgb(65,105,225)
    blue_violet = rgb(138,43,226)
    indigo = rgb(75,0,130)
    dark_slate_blue = rgb(72,61,139)
    slate_blue = rgb(106,90,205)
    medium_slate_blue = rgb(123,104,238)
    medium_purple = rgb(147,112,219)
    dark_magenta = rgb(139,0,139)
    dark_violet = rgb(148,0,211)
    dark_orchid = rgb(153,50,204)
    medium_orchid = rgb(186,85,211)
    purple = rgb(128,0,128)
    thistle = rgb(216,191,216)
    plum = rgb(221,160,221)
    violet = rgb(238,130,238)
    magenta = rgb(255,0,255)
    fuchsia = rgb(255,0,255)
    orchid = rgb(218,112,214)
    medium_violet_red = rgb(199,21,133)
    pale_violet_red = rgb(219,112,147)
    deep_pink = rgb(255,20,147)
    hot_pink = rgb(255,105,180)
    light_pink = rgb(255,182,193)
    pink = rgb(255,192,203)
    antique_white = rgb(250,235,215)
    beige = rgb(245,245,220)
    bisque = rgb(255,228,196)
    blanched_almond = rgb(255,235,205)
    wheat = rgb(245,222,179)
    corn_silk = rgb(255,248,220)
    lemon_chiffon = rgb(255,250,205)
    light_golden_rod_yellow = rgb(250,250,210)
    light_yellow = rgb(255,255,224)
    saddle_brown = rgb(139,69,19)
    sienna = rgb(160,82,45)
    chocolate = rgb(210,105,30)
    peru = rgb(205,133,63)
    sandy_brown = rgb(244,164,96)
    burly_wood = rgb(222,184,135)
    tan = rgb(210,180,140)
    rosy_brown = rgb(188,143,143)
    moccasin = rgb(255,228,181)
    navajo_white = rgb(255,222,173)
    peach_puff = rgb(255,218,185)
    misty_rose = rgb(255,228,225)
    lavender_blush = rgb(255,240,245)
    linen = rgb(250,240,230)
    old_lace = rgb(253,245,230)
    papaya_whip = rgb(255,239,213)
    sea_shell = rgb(255,245,238)
    mint_cream = rgb(245,255,250)
    slate_gray = rgb(112,128,144)
    light_slate_gray = rgb(119,136,153)
    light_steel_blue = rgb(176,196,222)
    lavender = rgb(230,230,250)
    floral_white = rgb(255,250,240)
    alice_blue = rgb(240,248,255)
    ghost_white = rgb(248,248,255)
    honeydew = rgb(240,255,240)
    ivory = rgb(255,255,240)
    azure = rgb(240,255,255)
    snow = rgb(255,250,250)
    black = rgb(0,0,0)
    dim_gray = rgb(105,105,105)
    dim_grey = rgb(105,105,105)
    gray = rgb(128,128,128)
    grey = rgb(128,128,128)
    dark_gray = rgb(169,169,169)
    dark_grey = rgb(169,169,169)
    silver = rgb(192,192,192)
    light_gray = rgb(211,211,211)
    light_grey = rgb(211,211,211)
    gainsboro = rgb(220,220,220)
    white_smoke = rgb(245,245,245)
    white = rgb(255,255,255)
