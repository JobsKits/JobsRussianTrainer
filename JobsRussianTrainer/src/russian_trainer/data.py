"""拼读课程数据；不把系统合成声音伪装成专业音素录音。"""

from dataclasses import dataclass, field

VOWELS = tuple("аоуыэяёюие")
CONSONANTS = tuple("бвгджзйклмнпрстфхцчшщ")
SOFT_VOWELS = frozenset("яёюие")
ALWAYS_HARD = frozenset("жшц")
ALWAYS_SOFT = frozenset("йчщ")


def uncommon(consonant: str, vowel: str) -> bool:
    """标注不适合作为常规入门拼读的组合，并非判定绝对不存在。"""
    return (
        consonant == "й"
        or (consonant in "гкхжшчщ" and vowel == "ы")
        or (consonant in "жшчщц" and vowel in "яю")
        or (consonant in "чщ" and vowel == "э")
    )


def note(consonant: str, vowel: str) -> str:
    parts = []
    if uncommon(consonant, vowel):
        parts.append("少见／非典型拼写，仅作组合试听；不作为常规拼写范例。")
    if consonant in ALWAYS_HARD:
        parts.append(f"{consonant.upper()} 通常读硬辅音，不能看到软化类元音就机械软化。")
        if vowel == "и":
            parts.append("这里的 и 读音接近 ы。")
    elif consonant in ALWAYS_SOFT:
        parts.append(f"{consonant.upper()} 属于通常恒软的辅音。")
    elif vowel in SOFT_VOWELS:
        parts.append("通常练习软辅音：发辅音时舌中部向硬腭抬起。")
    else:
        parts.append("通常练习硬辅音，与后面的元音连成一个音节。")
    parts.append("系统合成音仅供辅助；孤立组合可能被引擎读作字母名，实际词语还受重音影响。")
    return " ".join(parts)


RUSSIAN_ROMAN_CONSONANTS = {
    "б": "b", "в": "v", "г": "g", "д": "d", "ж": "zh", "з": "z", "й": "y",
    "к": "k", "л": "l", "м": "m", "н": "n", "п": "p", "р": "r", "с": "s",
    "т": "t", "ф": "f", "х": "kh", "ц": "ts", "ч": "ch", "ш": "sh", "щ": "shch",
}
RUSSIAN_ROMAN_VOWELS = {
    "а": "a", "я": "ya", "о": "o", "ё": "yo", "у": "u", "ю": "yu",
    "ы": "y", "и": "i", "э": "e", "е": "e",
}
RUSSIAN_IPA_CONSONANTS = {
    "б": "b", "в": "v", "г": "ɡ", "д": "d", "ж": "ʐ", "з": "z", "й": "j",
    "к": "k", "л": "l", "м": "m", "н": "n", "п": "p", "р": "r", "с": "s",
    "т": "t", "ф": "f", "х": "x", "ц": "t͡s", "ч": "t͡ɕ", "ш": "ʂ", "щ": "ɕː",
}
RUSSIAN_IPA_VOWELS = {
    "а": "a", "я": "a", "о": "o", "ё": "o", "у": "u", "ю": "u",
    "ы": "ɨ", "и": "i", "э": "e", "е": "e",
}
FRENCH_IPA_VOWELS = {"a": "a", "e": "ə~ɛ", "i": "i", "o": "o", "u": "y", "y": "i"}
FRENCH_IPA_CONSONANTS = {
    "b": "b", "d": "d", "f": "f", "k": "k", "l": "l", "m": "m", "n": "n",
    "p": "p", "s": "s", "t": "t", "v": "v", "z": "z",
}
SPANISH_IPA_VOWELS = {"a": "a", "e": "e", "i": "i", "o": "o", "u": "u"}
SPANISH_IPA_CONSONANTS = {
    "b": "b", "d": "d", "f": "f", "k": "k", "l": "l", "m": "m", "n": "n",
    "ñ": "ɲ", "p": "p", "s": "s", "t": "t", "v": "b", "w": "w", "y": "ʝ",
}
GERMAN_IPA_VOWELS = {
    "a": "aː~a", "ä": "ɛː~ɛ", "e": "eː~ɛ", "i": "iː~ɪ",
    "o": "oː~ɔ", "ö": "øː~œ", "u": "uː~ʊ", "ü": "yː~ʏ", "y": "i~y",
}
GERMAN_IPA_CONSONANTS = {
    "b": "b", "c": "k~ts", "d": "d", "f": "f", "g": "ɡ", "h": "h",
    "j": "j", "k": "k", "l": "l", "m": "m", "n": "n", "p": "p",
    "q": "kv", "r": "ʁ", "s": "z~s", "t": "t", "v": "f~v", "w": "v",
    "x": "ks", "z": "ts", "ch": "ç~x", "sch": "ʃ", "sp": "ʃp",
    "st": "ʃt", "pf": "pf", "tsch": "tʃ",
}


def german_consonant_ipa(consonant: str, vowel: str) -> str:
    if consonant == "c":
        return "ts" if vowel in "eiyäöü" else "k"
    if consonant == "ch":
        return "ç~x"
    return GERMAN_IPA_CONSONANTS.get(consonant, consonant)


GERMAN_VOWELS = tuple("aäeioöuüy")
GERMAN_CONSONANTS = tuple("bcdfghjklmnpqrstvwxz") + (
    "ch", "sch", "sp", "st", "pf", "tsch",
)
ARABIC_VOWELS = ("َ", "ِ", "ُ")
ARABIC_CONSONANTS = tuple("ءبتثجحخدذرزسشصضطظعغفقكلمنهوي")
ARABIC_ROMAN_VOWELS = {"َ": "a", "ِ": "i", "ُ": "u"}
ARABIC_IPA_VOWELS = {"َ": "a", "ِ": "i", "ُ": "u"}
ARABIC_ROMAN_CONSONANTS = {
    "ء": "ʾ", "ب": "b", "ت": "t", "ث": "th", "ج": "j", "ح": "ḥ", "خ": "kh",
    "د": "d", "ذ": "dh", "ر": "r", "ز": "z", "س": "s", "ش": "sh", "ص": "ṣ",
    "ض": "ḍ", "ط": "ṭ", "ظ": "ẓ", "ع": "ʿ", "غ": "gh", "ف": "f", "ق": "q",
    "ك": "k", "ل": "l", "م": "m", "ن": "n", "ه": "h", "و": "w", "ي": "y",
}
ARABIC_IPA_CONSONANTS = {
    "ء": "ʔ", "ب": "b", "ت": "t", "ث": "θ", "ج": "d͡ʒ", "ح": "ħ", "خ": "x",
    "د": "d", "ذ": "ð", "ر": "r", "ز": "z", "س": "s", "ش": "ʃ", "ص": "sˤ",
    "ض": "dˤ", "ط": "tˤ", "ظ": "ðˤ", "ع": "ʕ", "غ": "ɣ", "ف": "f", "ق": "q",
    "ك": "k", "ل": "l", "م": "m", "ن": "n", "ه": "h", "و": "w", "ي": "j",
}
KOREAN_ROMAN_INITIALS = {
    "ㄱ": "g", "ㄲ": "kk", "ㄴ": "n", "ㄷ": "d", "ㄸ": "tt", "ㄹ": "r", "ㅁ": "m",
    "ㅂ": "b", "ㅃ": "pp", "ㅅ": "s", "ㅆ": "ss", "ㅇ": "", "ㅈ": "j", "ㅉ": "jj",
    "ㅊ": "ch", "ㅋ": "k", "ㅌ": "t", "ㅍ": "p", "ㅎ": "h",
}
KOREAN_IPA_INITIALS = {
    "ㄱ": "k", "ㄲ": "k͈", "ㄴ": "n", "ㄷ": "t", "ㄸ": "t͈", "ㄹ": "ɾ", "ㅁ": "m",
    "ㅂ": "p", "ㅃ": "p͈", "ㅅ": "s", "ㅆ": "s͈", "ㅇ": "", "ㅈ": "t͡ɕ", "ㅉ": "t͡ɕ͈",
    "ㅊ": "t͡ɕʰ", "ㅋ": "kʰ", "ㅌ": "tʰ", "ㅍ": "pʰ", "ㅎ": "h",
}
KOREAN_ROMAN_VOWELS = {
    "ㅏ": "a", "ㅐ": "ae", "ㅑ": "ya", "ㅒ": "yae", "ㅓ": "eo", "ㅔ": "e", "ㅕ": "yeo",
    "ㅖ": "ye", "ㅗ": "o", "ㅘ": "wa", "ㅙ": "wae", "ㅚ": "oe", "ㅛ": "yo", "ㅜ": "u",
    "ㅝ": "wo", "ㅞ": "we", "ㅟ": "wi", "ㅠ": "yu", "ㅡ": "eu", "ㅢ": "ui", "ㅣ": "i",
}
KOREAN_IPA_VOWELS = {
    "ㅏ": "a", "ㅐ": "ɛ~e", "ㅑ": "ja", "ㅒ": "jɛ~je", "ㅓ": "ʌ", "ㅔ": "e", "ㅕ": "jʌ",
    "ㅖ": "je", "ㅗ": "o", "ㅘ": "wa", "ㅙ": "wɛ~we", "ㅚ": "we", "ㅛ": "jo", "ㅜ": "u",
    "ㅝ": "wʌ", "ㅞ": "we", "ㅟ": "wi", "ㅠ": "ju", "ㅡ": "ɯ", "ㅢ": "ɯi", "ㅣ": "i",
}
KOREAN_ROMAN_CODAS = {
    "": "", "ㄱ": "g", "ㄲ": "kk", "ㄳ": "gs", "ㄴ": "n", "ㄵ": "nj", "ㄶ": "nh",
    "ㄷ": "d", "ㄹ": "l", "ㄺ": "lg", "ㄻ": "lm", "ㄼ": "lb", "ㄽ": "ls", "ㄾ": "lt",
    "ㄿ": "lp", "ㅀ": "lh", "ㅁ": "m", "ㅂ": "b", "ㅄ": "bs", "ㅅ": "s", "ㅆ": "ss",
    "ㅇ": "ng", "ㅈ": "j", "ㅊ": "ch", "ㅋ": "k", "ㅌ": "t", "ㅍ": "p", "ㅎ": "h",
}
KOREAN_IPA_CODAS = {
    "": "", "ㄱ": "k̚", "ㄲ": "k̚", "ㄳ": "k̚", "ㄴ": "n", "ㄵ": "n", "ㄶ": "n",
    "ㄷ": "t̚", "ㄹ": "l", "ㄺ": "k̚", "ㄻ": "m", "ㄼ": "p̚", "ㄽ": "l", "ㄾ": "l",
    "ㄿ": "p̚", "ㅀ": "l", "ㅁ": "m", "ㅂ": "p̚", "ㅄ": "p̚", "ㅅ": "t̚", "ㅆ": "t̚",
    "ㅇ": "ŋ", "ㅈ": "t̚", "ㅊ": "t̚", "ㅋ": "k̚", "ㅌ": "t̚", "ㅍ": "p̚", "ㅎ": "t̚",
}


HANGUL_INITIALS = tuple("ㄱㄲㄴㄷㄸㄹㅁㅂㅃㅅㅆㅇㅈㅉㅊㅋㅌㅍㅎ")
HANGUL_VOWELS = tuple("ㅏㅑㅓㅕㅗㅛㅜㅠㅡㅣㅐㅒㅔㅖㅘㅙㅚㅝㅞㅟㅢ")
HANGUL_UNICODE_VOWELS = tuple("ㅏㅐㅑㅒㅓㅔㅕㅖㅗㅘㅙㅚㅛㅜㅝㅞㅟㅠㅡㅢㅣ")
HANGUL_CODAS = (
    "", "ㄱ", "ㄲ", "ㄳ", "ㄴ", "ㄵ", "ㄶ", "ㄷ", "ㄹ", "ㄺ", "ㄻ", "ㄼ",
    "ㄽ", "ㄾ", "ㄿ", "ㅀ", "ㅁ", "ㅂ", "ㅄ", "ㅅ", "ㅆ", "ㅇ", "ㅈ", "ㅊ",
    "ㅋ", "ㅌ", "ㅍ", "ㅎ",
)


@dataclass(frozen=True)
class SyllableCourse:
    key: str
    title: str
    locale: str
    vowels: tuple[str, ...]
    consonants: tuple[str, ...]
    notice: str
    kind: str = "alphabetic"
    codas: tuple[str, ...] = ()
    rare_consonants: frozenset[str] = frozenset()
    unavailable: frozenset[tuple[str, str]] = frozenset()
    overrides: dict[tuple[str, str], str] = field(default_factory=dict)

    @property
    def is_hangul(self) -> bool:
        return self.kind == "hangul"

    def display_vowel(self, vowel: str) -> str:
        return f"◌{vowel}" if self.key == "ar" else vowel

    def syllable(self, consonant: str, vowel: str, coda: str = "") -> str | None:
        if (consonant, vowel) in self.unavailable:
            return None
        if self.kind == "hangul":
            initial = HANGUL_INITIALS.index(consonant)
            medial = HANGUL_UNICODE_VOWELS.index(vowel)
            final = HANGUL_CODAS.index(coda)
            codepoint = 0xAC00 + ((initial * 21 + medial) * 28) + final
            return chr(codepoint)
        return self.overrides.get((consonant, vowel), consonant + vowel)

    def is_rare(self, consonant: str) -> bool:
        return consonant in self.rare_consonants

    def pronunciation_hint_for_vowel(self, vowel: str) -> str:
        if self.key == "ar":
            return f"{ARABIC_ROMAN_VOWELS[vowel]} /{ARABIC_IPA_VOWELS[vowel]}/"
        if self.key == "ru":
            return f"{RUSSIAN_ROMAN_VOWELS[vowel]} /{RUSSIAN_IPA_VOWELS[vowel]}/"
        if self.key == "fr":
            return f"/{FRENCH_IPA_VOWELS[vowel]}/"
        if self.key == "es":
            return f"/{SPANISH_IPA_VOWELS[vowel]}/"
        if self.key == "de":
            return f"{vowel} /{GERMAN_IPA_VOWELS[vowel]}/"
        return f"{KOREAN_ROMAN_VOWELS[vowel]} /{KOREAN_IPA_VOWELS[vowel]}/"

    def pronunciation_hint_for_consonant(self, consonant: str) -> str:
        if self.key == "ar":
            return f"{ARABIC_ROMAN_CONSONANTS[consonant]} /{ARABIC_IPA_CONSONANTS[consonant]}/"
        if self.key == "ru":
            return f"{RUSSIAN_ROMAN_CONSONANTS[consonant]} /{RUSSIAN_IPA_CONSONANTS[consonant]}/"
        if self.key == "ko":
            roman = KOREAN_ROMAN_INITIALS[consonant]
            ipa = KOREAN_IPA_INITIALS[consonant]
            return f"{roman or '—'} /{ipa or '∅'}/"
        if self.key == "fr":
            return {
                "c": "/k~s/", "g": "/ɡ~ʒ/", "h": "不发音 /∅/", "q": "/k/",
                "ch": "/ʃ/", "gn": "/ɲ/", "ph": "/f/", "r": "/ʁ/",
                "w": "/w~v/", "x": "/ks/",
            }.get(consonant, self.pronunciation_hint(consonant, self.vowels[0]))
        if self.key == "es":
            return {
                "c": "/k~θ/", "g": "/ɡ~x/", "h": "不发音 /∅/", "q": "/k/",
                "r": "词首颤音 /r/", "v": "/b/", "ch": "/tʃ/", "j": "/x/",
                "x": "/ks/", "y": "/ʝ/", "ll": "/ʝ/", "z": "/θ/",
            }.get(consonant, self.pronunciation_hint(consonant, self.vowels[0]))
        if self.key == "de":
            return f"/{GERMAN_IPA_CONSONANTS.get(consonant, consonant)}/"
        return self.pronunciation_hint(consonant, self.vowels[0])

    def pronunciation_hint(self, consonant: str, vowel: str, coda: str = "") -> str:
        if self.key == "ar":
            roman = ARABIC_ROMAN_CONSONANTS[consonant] + ARABIC_ROMAN_VOWELS[vowel]
            ipa = ARABIC_IPA_CONSONANTS[consonant] + ARABIC_IPA_VOWELS[vowel]
            return f"{roman} /{ipa}/"
        if self.key == "ru":
            roman = RUSSIAN_ROMAN_CONSONANTS[consonant] + RUSSIAN_ROMAN_VOWELS[vowel]
            ipa = RUSSIAN_IPA_CONSONANTS[consonant]
            if vowel in SOFT_VOWELS and consonant not in "жшцйчщ":
                ipa += "ʲ"
            ipa_vowel = "ɨ" if consonant in "жшц" and vowel == "и" else RUSSIAN_IPA_VOWELS[vowel]
            return f"{roman} /{ipa}{ipa_vowel}/"
        if self.key == "ko":
            roman = KOREAN_ROMAN_INITIALS[consonant] + KOREAN_ROMAN_VOWELS[vowel] + KOREAN_ROMAN_CODAS[coda]
            ipa = KOREAN_IPA_INITIALS[consonant] + KOREAN_IPA_VOWELS[vowel] + KOREAN_IPA_CODAS[coda]
            return f"{roman or '∅'} /{ipa or '∅'}/"
        if self.key == "fr":
            initial = {
                "c": "s" if vowel in "eiy" else "k", "g": "ʒ" if vowel in "eiy" else "ɡ",
                "ch": "ʃ", "gn": "ɲ", "ph": "f", "h": "", "j": "ʒ", "q": "k",
                "r": "ʁ", "w": "w~v", "x": "ks",
            }.get(consonant, FRENCH_IPA_CONSONANTS.get(consonant, consonant))
            ipa_vowel = "ə" if consonant == "q" and vowel == "e" else FRENCH_IPA_VOWELS[vowel]
            return f"/{initial}{ipa_vowel}/"
        if self.key == "es":
            initial = {
                "c": "θ" if vowel in "ei" else "k", "g": "x" if vowel in "ei" else "ɡ",
                "ch": "tʃ", "h": "", "j": "x", "q": "k", "r": "r",
                "v": "b", "x": "ks", "y": "ʝ", "ll": "ʝ", "z": "θ",
            }.get(consonant, SPANISH_IPA_CONSONANTS.get(consonant, consonant))
            return f"/{initial}{SPANISH_IPA_VOWELS[vowel]}/"
        if self.key == "de":
            initial = german_consonant_ipa(consonant, vowel)
            vowel_ipa = GERMAN_IPA_VOWELS[vowel]
            if consonant == "ch":
                sound_sequence = f"{initial} {vowel_ipa}"
            else:
                sound_sequence = f"{initial}{vowel_ipa}"
            return f"{consonant}{vowel} /{sound_sequence}/"
        return ""

    def hint(self, consonant: str, vowel: str, coda: str = "") -> str:
        if self.key == "ru":
            return note(consonant, vowel)
        if self.key == "ar":
            return "简化拉丁转写与 IPA 按常见现代标准阿拉伯语入门音值标注；不同地区读音会有差异。"
        return self.notice


RUSSIAN_COURSE = SyllableCourse(
    key="ru",
    title="俄语拼读",
    locale="ru-RU",
    vowels=VOWELS,
    consonants=CONSONANTS,
    notice="10 个元音与 21 个辅音，共 210 个组合。",
)

FRENCH_COURSE = SyllableCourse(
    key="fr",
    title="法语拼读",
    locale="fr-FR",
    vowels=tuple("aeiouy"),
    consonants=tuple("bcdfghjklmnpqrstvwxz") + ("ch", "gn", "ph"),
    notice=(
        "6 个元音字母与常见辅音组合可点读。法语 e、y、c、g、q、h 及 "
        "ch / gn / ph 受拼写位置影响；q 只提供 que / qui。系统 TTS 试听不等同于人工音素录音。"
    ),
    rare_consonants=frozenset({"k", "w", "x"}),
    unavailable=frozenset({("q", "a"), ("q", "o"), ("q", "u"), ("q", "y")}),
    overrides={("q", "e"): "que", ("q", "i"): "qui"},
)

SPANISH_COURSE = SyllableCourse(
    key="es",
    title="西班牙语拼读",
    locale="es-ES",
    vowels=tuple("aeiou"),
    consonants=tuple("bcdfghjklmnñpqrstvwxyz") + ("ch", "ll"),
    notice=(
        "5 个元音、22 个辅音字母及 ch / ll 拼写组合可点读。c、g 会随后接元音改变读音；"
        "h 不发音，q 通过 que / qui 拼写；b / v 同音，z 与 c 的读音因地区而异。k / w / x 多见于外来词。"
    ),
    rare_consonants=frozenset({"k", "w", "x"}),
    unavailable=frozenset({("q", "a"), ("q", "o"), ("q", "u")}),
    overrides={("q", "e"): "que", ("q", "i"): "qui"},
)

GERMAN_COURSE = SyllableCourse(
    key="de",
    title="德语拼读",
    locale="de-DE",
    vowels=GERMAN_VOWELS,
    consonants=GERMAN_CONSONANTS,
    notice=(
        "8 个基础元音字母、外来词元音 y 与 20 个基础辅音字母可组合点读，并提供常见 ch / sch / sp / st / pf / tsch 拼写。"
        "q 行组合自动补入 u；元音长短、c / ch / s / v 等读音受拼写位置和词源影响，注音为常见入门提示。"
    ),
    rare_consonants=frozenset({"c", "q", "x"}),
    unavailable=frozenset({("q", "ö"), ("q", "u"), ("q", "ü"), ("q", "y")}),
    overrides={("q", vowel): f"qu{vowel}" for vowel in GERMAN_VOWELS},
)

ARABIC_COURSE = SyllableCourse(
    key="ar",
    title="阿拉伯语短元音拼读",
    locale="ar-SA",
    vowels=ARABIC_VOWELS,
    consonants=ARABIC_CONSONANTS,
    notice=(
        "28 个辅音分别组合 َ a、ِ i、ُ u，并附简化拉丁注音与宽式 IPA。"
        "阿拉伯语日常书写通常省略短元音符号；本表不覆盖长元音、辅音连缀、词形变化和地区口音。"
    ),
)

KOREAN_COURSE = SyllableCourse(
    key="ko",
    title="朝鲜语拼读",
    locale="ko-KR",
    vowels=HANGUL_VOWELS,
    consonants=HANGUL_INITIALS,
    notice=(
        "19 个声母、21 个元音可组合成韩文音节块，并可选择 27 种收音或无收音。"
        "ㅇ 作声母时不发音；收音在词中会受连音和音变规则影响，系统 TTS 仅供试听。"
    ),
    kind="hangul",
    codas=HANGUL_CODAS,
)

COURSES = {
    course.key: course
    for course in (
        RUSSIAN_COURSE,
        ARABIC_COURSE,
        FRENCH_COURSE,
        SPANISH_COURSE,
        KOREAN_COURSE,
        GERMAN_COURSE,
    )
}
