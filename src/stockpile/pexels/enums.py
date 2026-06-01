"""
Enums for constrained Pexels API parameters.

These provide type-safe parameter values and IDE autocomplete support.
"""

from enum import Enum


class Orientation(str, Enum):
    """Photo/video orientation filter."""

    LANDSCAPE = "landscape"
    PORTRAIT = "portrait"
    SQUARE = "square"


class Size(str, Enum):
    """Minimum photo size filter."""

    LARGE = "large"    # 24MP+
    MEDIUM = "medium"  # 12MP+
    SMALL = "small"    # 4MP+


class Color(str, Enum):
    """Color filter for photo search.

    Supports both named colors and hex values.
    """

    RED = "red"
    ORANGE = "orange"
    YELLOW = "yellow"
    GREEN = "green"
    TURQUOISE = "turquoise"
    BLUE = "blue"
    VIOLET = "violet"
    PINK = "pink"
    BROWN = "brown"
    BLACK = "black"
    GRAY = "gray"
    WHITE = "white"

    @classmethod
    def hex(cls, hex_code: str) -> str:
        """Create a hex color filter (e.g., '#ff0000').

        Args:
            hex_code: A valid hex color string like '#ffffff' or 'ffffff'.
        """
        if not hex_code.startswith("#"):
            hex_code = f"#{hex_code}"
        return hex_code


class Locale(str, Enum):
    """Locale filter for search results."""

    EN_US = "en-US"
    PT_BR = "pt-BR"
    ES_ES = "es-ES"
    CA_ES = "ca-ES"
    DE_DE = "de-DE"
    IT_IT = "it-IT"
    FR_FR = "fr-FR"
    SV_SE = "sv-SE"
    ID_ID = "id-ID"
    PL_PL = "pl-PL"
    JA_JP = "ja-JP"
    ZH_TW = "zh-TW"
    ZH_CN = "zh-CN"
    KO_KR = "ko-KR"
    TH_TH = "th-TH"
    NL_NL = "nl-NL"
    HU_HU = "hu-HU"
    VI_VN = "vi-VN"
    CS_CZ = "cs-CZ"
    DA_DK = "da-DK"
    FI_FI = "fi-FI"
    UK_UA = "uk-UA"
    EL_GR = "el-GR"
    RO_RO = "ro-RO"
    NB_NO = "nb-NO"
    SK_SK = "sk-SK"
    TR_TR = "tr-TR"
    RU_RU = "ru-RU"


class CollectionType(str, Enum):
    """Type of media to retrieve from a collection."""

    PHOTOS = "photos"
    VIDEOS = "videos"


class SortOrder(str, Enum):
    """Sort order for collection media."""

    ASC = "asc"
    DESC = "desc"
