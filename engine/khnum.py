"""Khmer number words for TTS: speak('ឆ្នាំ ១៩៦២') -> 'ឆ្នាំ មួយពាន់ប្រាំបួនរយហុកសិបពីរ'."""
import re

D = ["សូន្យ", "មួយ", "ពីរ", "បី", "បួន", "ប្រាំ", "ប្រាំមួយ", "ប្រាំពីរ", "ប្រាំបី", "ប្រាំបួន"]
T = {1: "ដប់", 2: "ម្ភៃ", 3: "សាមសិប", 4: "សែសិប", 5: "ហាសិប", 6: "ហុកសិប", 7: "ចិតសិប", 8: "ប៉ែតសិប", 9: "កៅសិប"}
KD = "០១២៣៤៥៦៧៨៩"


def words(n):
    n = int(n)
    if n < 10:
        return D[n]
    if n < 100:
        t, u = divmod(n, 10)
        return T[t] + (D[u] if u else "")
    for unit, name in ((1000000, "លាន"), (100000, "សែន"), (10000, "ម៉ឺន"), (1000, "ពាន់"), (100, "រយ")):
        if n >= unit:
            q, r = divmod(n, unit)
            return words(q) + name + (words(r) if r else "")
    return str(n)


def to_ascii(s):
    return "".join(str(KD.index(c)) if c in KD else c for c in s)


def speak(text):
    t = to_ascii(text)
    while re.search(r"(\d),(\d{3})", t):
        t = re.sub(r"(\d),(\d{3})", r"\1\2", t)
    t = re.sub(r"(\d+)\.(\d+)", lambda m: words(m.group(1)) + "ចំណុច" + "".join(D[int(c)] for c in m.group(2)), t)
    t = re.sub(r"\d+", lambda m: words(m.group(0)), t)
    return t


if __name__ == "__main__":
    for x in ["ឆ្នាំ ១៩៦២", "១០០២", "៤.៦ គីឡូម៉ែត្រ", "៤២០០០", "៥៦២", "២០២៥"]:
        print(x, "->", speak(x))
