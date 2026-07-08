import re
from typing import Dict, Tuple

__all__ = ["normalize"]

_STRESS_MARK = re.compile(r"\u0301")
_PLUS_MARK = re.compile(r"\+([а-яё])")

_MONTHS_GEN = ["января", "февраля", "марта", "апреля", "мая", "июня",
               "июля", "августа", "сентября", "октября", "ноября", "декабря"]

_ONES_M = ["", "один", "два", "три", "четыре", "пять", "шесть", "семь", "восемь", "девять"]
_ONES_F = ["", "одна", "две", "три", "четыре", "пять", "шесть", "семь", "восемь", "девять"]
_ONES_N = ["", "одно", "два", "три", "четыре", "пять", "шесть", "семь", "восемь", "девять"]

_ORD_ONES_M = ["", "первый", "второй", "третий", "четвёртый",
               "пятый", "шестой", "седьмой", "восьмой", "девятый"]
_ORD_ONES_F = ["", "первая", "вторая", "третья", "четвёртая",
               "пятая", "шестая", "седьмая", "восьмая", "девятая"]
_ORD_ONES_N = ["", "первое", "второе", "третье", "четвёртое",
               "пятое", "шестое", "седьмое", "восьмое", "девятое"]

_TEENS = ["десять", "одиннадцать", "двенадцать", "тринадцать", "четырнадцать",
          "пятнадцать", "шестнадцать", "семнадцать", "восемнадцать", "девятнадцать"]
_TENS = ["", "", "двадцать", "тридцать", "сорок", "пятьдесят",
         "шестьдесят", "семьдесят", "восемьдесят", "девяносто"]
_HUNDREDS = ["", "сто", "двести", "триста", "четыреста",
             "пятьсот", "шестьсот", "семьсот", "восемьсот", "девятьсот"]

_ORD_TEENS = ["десятый", "одиннадцатый", "двенадцатый", "тринадцатый", "четырнадцатый",
              "пятнадцатый", "шестнадцатый", "семнадцатый", "восемнадцатый", "девятнадцатый"]
_ORD_TENS = ["", "", "двадцатый", "тридцатый", "сороковой", "пятидесятый",
             "шестидесятый", "семидесятый", "восьмидесятый", "девяностый"]

_THOUSAND_FORMS = ("тысяча", "тысячи", "тысяч")
_MILLION_FORMS = ("миллион", "миллиона", "миллионов")
_BILLION_FORMS = ("миллиард", "миллиарда", "миллиардов")

_ORD_TEENS_N = ["десятое", "одиннадцатое", "двенадцатое", "тринадцатое", "четырнадцатое",
                "пятнадцатое", "шестнадцатое", "семнадцатое", "восемнадцатое", "девятнадцатое"]
_ORD_TENS_N = ["", "", "двадцатое", "тридцатое", "сороковое", "пятидесятое",
               "шестидесятое", "семидесятое", "восьмидесятое", "девяностое"]


def _plural_form(n: int, forms: Tuple[str, str, str]) -> str:
    n = abs(n) % 100
    if 11 <= n <= 19:
        return forms[2]
    n %= 10
    if n == 1:
        return forms[0]
    if 2 <= n <= 4:
        return forms[1]
    return forms[2]


def _num_to_words(n: int, fem: bool = False, neut: bool = False, ordinal: bool = False) -> str:
    if n == 0:
        return "нулевой" if ordinal else "ноль"
    if n < 0:
        return "минус " + _num_to_words(-n, fem, neut, ordinal)

    def _hundreds(num: int, is_fem: bool, is_neut: bool, is_ord: bool) -> str:
        parts = []
        h = num // 100
        if h:
            parts.append(_HUNDREDS[h])
        t = num % 100
        if 10 <= t <= 19:
            if is_ord:
                parts.append(_ORD_TEENS_N[t - 10] if is_neut else _ORD_TEENS[t - 10])
            else:
                parts.append(_TEENS[t - 10])
        else:
            d = t // 10
            if d:
                if is_ord and t % 10 == 0:
                    parts.append(_ORD_TENS_N[d] if is_neut else _ORD_TENS[d])
                else:
                    parts.append(_TENS[d])
            o = t % 10
            if o:
                if is_ord:
                    if is_neut:
                        parts.append(_ORD_ONES_N[o])
                    elif is_fem:
                        parts.append(_ORD_ONES_F[o])
                    else:
                        parts.append(_ORD_ONES_M[o])
                elif is_fem:
                    parts.append(_ONES_F[o])
                elif is_neut:
                    parts.append(_ONES_N[o])
                else:
                    parts.append(_ONES_M[o])
        return " ".join(parts)

    billions = n // 1000000000
    rem = n % 1000000000
    millions = rem // 1000000
    rem %= 1000000
    thousands = rem // 1000
    rem %= 1000

    result = []
    if billions:
        result.append(_hundreds(billions, False, False, False))
        result.append(_plural_form(billions, _BILLION_FORMS))
    if millions:
        result.append(_hundreds(millions, False, False, False))
        result.append(_plural_form(millions, _MILLION_FORMS))
    if thousands:
        result.append(_hundreds(thousands, True, False, False))
        result.append(_plural_form(thousands, _THOUSAND_FORMS))
    if rem:
        if ordinal and not any([billions, millions, thousands]):
            result.append(_hundreds(rem, fem, neut, True))
        else:
            result.append(_hundreds(rem, fem, neut, False))
    return " ".join(result)


_DATE_RE = re.compile(
    r"(?<!\d)(\d{1,2})[./](0?[1-9]|1[012])[./](\d{4})(?!\d)"
)
_DATE_NOYEAR_RE = re.compile(
    r"(?<!\d)(\d{1,2})[./](0?[1-9]|1[012])(?!\d)"
)
_TIME_RE = re.compile(r"(?<!\d)(\d{1,2}):(\d{2})(?!\d)")

_ORDINAL_SUFFIX_RE = re.compile(r"(\d+)[-‐](?:й|я|е|го|му|м|йся|яся|ееся)")
_PHONE_RE = re.compile(
    r"(?<!\w)(?:\+7|8)\s*\(?\d{3}\)?\s*\d{3}\s*-?\s*\d{2}\s*-?\s*\d{2}(?!\w)"
)

_URL_RE = re.compile(
    r"https?://[^\s<>\"'()]+"
    r"|www\.[^\s<>\"'()]+"
    r"|(?<!\w)[a-zA-Z0-9][a-zA-Z0-9.-]*\.[a-zA-Z]{2,}(?:/[^\s<>\"'()]*)?(?!\w)"
)
_EMAIL_RE = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")

_ABBR_MAP: Dict[str, str] = {
    "и т.д.": "и так далее",
    "и т.п.": "и тому подобное",
    "т.д.": "так далее",
    "т.п.": "тому подобное",
    "т.е.": "то есть",
    "т.к.": "так как",
    "т.н.": "так называемый",
    "др.": "другие",
    "пр.": "прочее",
    "см.": "смотри",
    "напр.": "например",
}
_ABBR_RE = re.compile(
    r"(?<!\w)(" + "|".join(sorted(_ABBR_MAP, key=len, reverse=True)) + r")(?!\w)",
    re.IGNORECASE
)

_UNITS_MAP: Dict[str, str] = {
    "кг": "килограмм",
    "г": "грамм",
    "мг": "миллиграмм",
    "км": "километров",
    "м": "метров",
    "дм": "дециметров",
    "см": "сантиметров",
    "мм": "миллиметров",
    "л": "литров",
    "мл": "миллилитров",
    "т": "тонн",
    "га": "гектаров",
    "вт": "ватт",
    "квт": "киловатт",
    "а": "ампер",
    "в": "вольт",
    "гц": "герц",
    "ккал": "килокалорий",
    "кал": "калорий",
    "шт": "штук",
    "экз": "экземпляров",
    "чел": "человек",
    "м/с": "метров в секунду",
    "км/ч": "километров в час",
    "об/мин": "оборотов в минуту",
    "об/с": "оборотов в секунду",
}

_SLASH_UNIT_RE = re.compile(
    r"(?<!\w)(" + "|".join(sorted(
        [k for k in _UNITS_MAP if "/" in k],
        key=len, reverse=True
    )) + r")(?!\w)",
    re.IGNORECASE
)

_UNIT_RE = re.compile(
    r"(?<!\w)(\d+(?:[.,]\d+)?)\s*(" + "|".join(sorted(
        [k for k in _UNITS_MAP if "/" not in k],
        key=len, reverse=True
    )) + r")(?!\w)",
    re.IGNORECASE
)

_SYM_MAP: Dict[str, str] = {
    "%": "процентов",
    "№": "номер",
    "$": "долларов",
    "€": "евро",
    "₽": "рублей",
    "°C": "градусов по Цельсию",
    "°": "градусов",
    "+": "плюс",
    "±": "плюс минус",
    "×": "на",
    "≈": "примерно",
    "≠": "не равно",
    "≤": "меньше или равно",
    "≥": "больше или равно",
}

_SYM_NUM_RE = re.compile(
    r"(-?\d+)\s*(" + "|".join(
        re.escape(s) for s in sorted(
            [k for k in _SYM_MAP if any(c in k for c in "%$€₽°")],
            key=len, reverse=True
        )
    ) + r")(?!\w)"
)

_SYM_SIMPLE_RE = re.compile(
    "(" + "|".join(re.escape(s) for s in sorted(_SYM_MAP, key=len, reverse=True)) + ")"
)

_EN_RU_MAP: Dict[str, str] = {
    "hello": "хэллоу", "world": "уорлд", "ok": "окей", "yes": "йес", "no": "ноу",
    "stop": "стоп", "start": "старт", "menu": "меню", "file": "файл", "edit": "эдит",
    "view": "вью", "help": "хэлп", "exit": "эксит", "save": "сейв", "open": "оупен",
    "new": "нью", "print": "принт", "page": "пэйдж", "home": "хоум", "user": "юзер",
    "admin": "админ", "login": "логин", "password": "пароль", "email": "имейл",
    "phone": "телефон", "name": "нэйм", "type": "тайп", "code": "код", "data": "дата",
    "info": "инфо", "text": "текст", "list": "лист", "link": "линк", "site": "сайт",
    "chat": "чат", "bot": "бот", "click": "клик", "push": "пуш", "error": "ошибка",
    "okay": "окей", "next": "некст", "back": "бэк", "top": "топ", "time": "тайм",
    "example": "эксэмпэл", "google": "гугл", "youtube": "ютуб", "mail": "мэйл",
    "gmail": "джимэйл", "yandex": "яндэкс", "vk": "вэ-ка", "telegram": "тэлеграм",
    "github": "гитхаб", "gitlab": "гитлаб", "docs": "докс", "maps": "карты",
    "privet": "привет", "test": "тэст", "api": "апи",
    "ru": "ру", "su": "су", "com": "ком", "org": "орг", "net": "нет",
    "gov": "гов", "edu": "эду", "рф": "рф",
}

_ENGLISH_PATTERNS: Dict[re.Pattern, str] = {
    re.compile(r"\bhttps?\b", re.IGNORECASE): "эйч-ти-ти-пи-эс",
    re.compile(r"\bftp\b", re.IGNORECASE): "эф-тэ-пэ",
    re.compile(r"\bwww\b", re.IGNORECASE): "дабл-ю-дабл-ю-дабл-ю",
    re.compile(r"\bcom\b", re.IGNORECASE): "ком",
    re.compile(r"\borg\b", re.IGNORECASE): "орг",
    re.compile(r"\bnet\b", re.IGNORECASE): "нет",
}

_ENGLISH_WORD_RE = re.compile(r"(?<!\w)[a-zA-Z]{2,}(?:'[a-zA-Z]+)?(?!\w)")

_LETTER_NAMES: Dict[str, str] = {
    "А": "а", "Б": "бэ", "В": "вэ", "Г": "гэ", "Д": "дэ",
    "Е": "е", "Ё": "ё", "Ж": "жэ", "З": "зэ", "И": "и",
    "Й": "й", "К": "ка", "Л": "эл", "М": "эм", "Н": "эн",
    "О": "о", "П": "пэ", "Р": "эр", "С": "эс", "Т": "тэ",
    "У": "у", "Ф": "эф", "Х": "ха", "Ц": "цэ", "Ч": "че",
    "Ш": "ша", "Щ": "ща", "Ъ": "твёрдый знак", "Ы": "ы",
    "Ь": "мягкий знак", "Э": "э", "Ю": "ю", "Я": "я",
    "A": "а", "B": "бэ", "C": "цэ", "D": "дэ", "E": "е",
    "F": "эф", "G": "гэ", "H": "аш", "I": "и", "J": "йот",
    "K": "ка", "L": "эл", "M": "эм", "N": "эн", "O": "о",
    "P": "пэ", "Q": "ку", "R": "эр", "S": "эс", "T": "тэ",
    "U": "у", "V": "вэ", "W": "дубль-вэ", "X": "икс", "Y": "игрек", "Z": "зэт",
}
_ABBREV_RE = re.compile(r"(?<!\w)([A-ZА-ЯЁ]{2,6})(?!\w)")

def _expand_abbrev(m: re.Match) -> str:
    word = m.group(1)
    return " ".join(_LETTER_NAMES.get(ch, ch.lower()) for ch in word)

_NUM_RE = re.compile(
    r"(?<!\w)(-?\d{1,3}(?:\s?\d{3})*(?:[.,]\d+)?)\s*([а-яёa-z]+)?(?!\w)",
    re.IGNORECASE
)

_PUNCT_SPACE_RE = re.compile(r"\s+([.,!?;:])")
_PUNCT_LEAD_RE = re.compile(r"([([])\s+")
_MULTI_SPACE_RE = re.compile(r"[ \t]+")


def _expand_url(m: re.Match) -> str:
    url = m.group(0)
    rest = url.split("://", 1)[-1]
    domain = rest.split("/")[0]
    domain = domain.split("@")[-1]
    domain = domain.split(":")[0]
    parts = [p for p in domain.replace("www.", " ").split(".") if p]
    if not parts:
        return " ссылка "
    result = " точка ".join(parts)
    slash_idx = rest.find("/")
    if slash_idx >= 0:
        path = rest[slash_idx + 1:]
        if path:
            result += " слэш " + " слэш ".join(path.split("/"))
    return " " + result + " "

def _expand_email(m: re.Match) -> str:
    return " электронный адрес "

def _expand_abbr(m: re.Match) -> str:
    return _ABBR_MAP[m.group(1).lower()]

def _expand_slash_unit(m: re.Match) -> str:
    return _UNITS_MAP[m.group(0).lower().strip()]

def _expand_unit(m: re.Match) -> str:
    num_raw = m.group(1)
    unit = m.group(2).lower()
    val = float(num_raw.replace(",", "."))
    int_val = int(val)
    plural = _plural_form(int_val, (_UNITS_MAP[unit], _UNITS_MAP[unit], _UNITS_MAP[unit]))
    result = _num_to_words(int_val)
    if val != int_val:
        frac = num_raw.split("." if "." in num_raw else ",")[1].rstrip("0")
        if frac:
            result += " запятая " + " ".join(_ONES_F[int(ch)] for ch in frac)
    return result + " " + plural

def _expand_sym_num(m: re.Match) -> str:
    raw = m.group(1)
    num_str = _num_to_words(int(raw.lstrip("-")))
    if raw.startswith("-"):
        num_str = "минус " + num_str
    return num_str + " " + _SYM_MAP[m.group(2)]

def _expand_sym_simple(m: re.Match) -> str:
    return " " + _SYM_MAP[m.group(1)] + " "

def _expand_date(m: re.Match) -> str:
    day, month, year = int(m.group(1)), int(m.group(2)), int(m.group(3))
    day_word = _num_to_words(day, neut=True, ordinal=True)
    month_word = _MONTHS_GEN[month - 1] if 1 <= month <= 12 else _num_to_words(month)
    year_word = _num_to_words(year, neut=True, ordinal=True)
    return f"{day_word} {month_word} {year_word} года"

def _expand_date_noyear(m: re.Match) -> str:
    day, month = int(m.group(1)), int(m.group(2))
    day_word = _num_to_words(day, neut=True, ordinal=True)
    month_word = _MONTHS_GEN[month - 1] if 1 <= month <= 12 else _num_to_words(month)
    return f"{day_word} {month_word}"

def _expand_time(m: re.Match) -> str:
    h, m_val = int(m.group(1)), int(m.group(2))
    words = [_num_to_words(h)]
    if m_val:
        words.append(_num_to_words(m_val))
    return " ".join(words)

def _expand_phone(m: re.Match) -> str:
    digits = re.sub(r"\D", "", m.group(0))
    if len(digits) == 11 and digits.startswith("7"):
        digits = "8" + digits[1:]
    parts = []
    for ch in digits:
        parts.append(_ONES_F[int(ch)])
    return " ".join(parts)

def _expand_ordinal(m: re.Match) -> str:
    num = int(m.group(1))
    return _num_to_words(num, ordinal=True)

def _expand_number(m: re.Match) -> str:
    raw = m.group(1)
    unit = (m.group(2) or "").lower().strip().rstrip(".")
    is_negative = raw.startswith("-")
    if is_negative:
        raw = raw[1:]

    int_str = raw.replace(" ", "")
    if "." in int_str or "," in int_str:
        sep = "." if "." in int_str else ","
        int_part, frac_part = int_str.split(sep, 1)
        int_val = int(int_part)
        frac_clean = frac_part.rstrip("0")
        words = [_num_to_words(int_val)]
        if frac_clean:
            words.append("запятая")
            words.extend(_ONES_F[int(ch)] for ch in frac_clean)
    else:
        int_val = int(int_str)
        words = [_num_to_words(int_val)]

    if is_negative:
        words.insert(0, "минус")

    _CURRENCY = {
        "руб": ("рубль", "рубля", "рублей"),
        "рубл": ("рубль", "рубля", "рублей"),
        "коп": ("копейка", "копейки", "копеек"),
        "долл": ("доллар", "доллара", "долларов"),
        "евро": ("евро", "евро", "евро"),
        "цент": ("цент", "цента", "центов"),
        "usd": ("доллар", "доллара", "долларов"),
        "eur": ("евро", "евро", "евро"),
        "дол": ("доллар", "доллара", "долларов"),
    }
    if unit in _CURRENCY:
        words.append(_plural_form(int_val, _CURRENCY[unit]))
    elif unit:
        words.append(unit)

    return " ".join(words)

def _handle_english(m: re.Match) -> str:
    word = m.group(0)
    for pat, repl in _ENGLISH_PATTERNS.items():
        if pat.fullmatch(word):
            return repl
    return _EN_RU_MAP.get(word.lower(), word)


def normalize(text: str) -> str:
    if not text:
        return text or ""

    text = _STRESS_MARK.sub("", text)
    text = _PLUS_MARK.sub(r"\1", text)

    text = _EMAIL_RE.sub(_expand_email, text)
    text = _URL_RE.sub(_expand_url, text)
    text = _ABBR_RE.sub(_expand_abbr, text)

    text = _ORDINAL_SUFFIX_RE.sub(_expand_ordinal, text)

    text = _PHONE_RE.sub(_expand_phone, text)

    text = _DATE_RE.sub(_expand_date, text)
    text = _DATE_NOYEAR_RE.sub(_expand_date_noyear, text)
    text = _TIME_RE.sub(_expand_time, text)

    text = _SLASH_UNIT_RE.sub(_expand_slash_unit, text)
    text = _SYM_NUM_RE.sub(_expand_sym_num, text)
    text = _SYM_SIMPLE_RE.sub(_expand_sym_simple, text)
    text = _UNIT_RE.sub(_expand_unit, text)

    text = _NUM_RE.sub(_expand_number, text)

    text = _ENGLISH_WORD_RE.sub(_handle_english, text)

    text = _ABBREV_RE.sub(_expand_abbrev, text)

    text = text.replace("(", " ").replace(")", " ")
    text = text.replace("[", " ").replace("]", " ")
    text = text.replace("{", " ").replace("}", " ")
    text = _PUNCT_SPACE_RE.sub(r"\1", text)
    text = _PUNCT_LEAD_RE.sub(r"\1", text)
    text = _MULTI_SPACE_RE.sub(" ", text).strip()
    return text
