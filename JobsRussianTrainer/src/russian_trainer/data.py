"""字母表及学习提示；不把拼写组合伪装成音标。"""

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
