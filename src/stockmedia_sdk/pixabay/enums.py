"""
Enums for constrained Pixabay API parameters.

These provide type-safe parameter values and IDE autocomplete support.
"""

from enum import Enum


class ImageType(str, Enum):
    """Filter results by image type."""

    ALL = "all"
    PHOTO = "photo"
    ILLUSTRATION = "illustration"
    VECTOR = "vector"


class VideoType(str, Enum):
    """Filter results by video type."""

    ALL = "all"
    FILM = "film"
    ANIMATION = "animation"


class Orientation(str, Enum):
    """Image/video orientation filter."""

    ALL = "all"
    HORIZONTAL = "horizontal"
    VERTICAL = "vertical"


class Order(str, Enum):
    """Sort order for search results."""

    POPULAR = "popular"
    LATEST = "latest"


class Category(str, Enum):
    """Category filter for images and videos."""

    BACKGROUNDS = "backgrounds"
    FASHION = "fashion"
    NATURE = "nature"
    SCIENCE = "science"
    EDUCATION = "education"
    FEELINGS = "feelings"
    HEALTH = "health"
    PEOPLE = "people"
    RELIGION = "religion"
    PLACES = "places"
    ANIMALS = "animals"
    INDUSTRY = "industry"
    COMPUTER = "computer"
    FOOD = "food"
    SPORTS = "sports"
    TRANSPORTATION = "transportation"
    TRAVEL = "travel"
    BUILDINGS = "buildings"
    BUSINESS = "business"
    MUSIC = "music"


class Color(str, Enum):
    """Color filter for images. A comma-separated list of values may be used."""

    GRAYSCALE = "grayscale"
    TRANSPARENT = "transparent"
    RED = "red"
    ORANGE = "orange"
    YELLOW = "yellow"
    GREEN = "green"
    TURQUOISE = "turquoise"
    BLUE = "blue"
    LILAC = "lilac"
    PINK = "pink"
    WHITE = "white"
    GRAY = "gray"
    BLACK = "black"
    BROWN = "brown"


class Language(str, Enum):
    """Language code for search results."""

    CS = "cs"
    DA = "da"
    DE = "de"
    EN = "en"
    ES = "es"
    FR = "fr"
    ID = "id"
    IT = "it"
    HU = "hu"
    NL = "nl"
    NO = "no"
    PL = "pl"
    PT = "pt"
    RO = "ro"
    SK = "sk"
    FI = "fi"
    SV = "sv"
    TR = "tr"
    VI = "vi"
    TH = "th"
    BG = "bg"
    RU = "ru"
    EL = "el"
    JA = "ja"
    KO = "ko"
    ZH = "zh"
