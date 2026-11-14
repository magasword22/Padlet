import re, sys, collections

src, dst, droplog = sys.argv[1:4]
text = open(src, encoding="utf-8").read()
pages = text.split("\f")

LOW = "a-zàâäçéèêëîïôöûùüÿœæ"
WORD = re.compile(rf"[A-Za-z{LOW}ÀÂÄÇÉÈÊËÎÏÔÖÛÙÜŸŒÆ]+")
vocab = collections.Counter(w for w in WORD.findall(text))
lower_vocab = collections.Counter(w.lower() for w in WORD.findall(text))
DICT = set(w.strip().lower() for w in open("/usr/share/dict/french", encoding="utf-8"))
def known(t):
    t = t.lower()
    return t in DICT or lower_vocab[t] >= 5

stats = collections.Counter()

def fix_line(l):
    # Majuscules parasites au milieu d'une phrase : "associer Les salariés" -> "les"
    def art(m):
        stats["article"] += 1
        return m.group(1) + m.group(2).lower()
    l = re.sub(rf"([{LOW},;:’'] )(La|Les|Le)(?= [{LOW}])", art, l)
    # "ILpeut" -> "Il peut", "ILs" -> "Ils"
    def il(m):
        stats["IL"] += 1
        rest = m.group(1)
        return "Ils" if rest == "s" else "Il " + rest
    l = re.sub(rf"\bIL([{LOW}]+)", il, l)
    # "Vemployeur" -> "l'employeur" (apostrophe lue comme un V)
    def v(m):
        w, rest = m.group(0), m.group(1)
        if rest.lower() in DICT and ("v" + rest.lower()) not in DICT:
            stats["V->l'"] += 1
            return "l’" + rest
        return w
    l = re.sub(rf"\bV([aeiouyhéèêàâîôû][{LOW}]+)", v, l)
    # Accents mal reconnus
    for a, b in [(r"\bprés\b", "près"), (r"\baprés\b", "après"), (r"\bAprés\b", "Après"),
                 (r"\bétre\b", "être"), (r"(?<=[lL][’'])Age\b", "âge"),
                 (r"\bfinanciére\b", "financière")]:
        l, n = re.subn(a, b, l)
        stats["accents"] += n
    return l

def is_garbage(l):
    s = l.strip()
    if not s:
        return False
    if re.search(r"https?://|www\.|\d+ ?%", s):
        return False
    toks = WORD.findall(s)
    if len(toks) == 1 and len(toks[0]) >= 4:
        return False  # titre ou mot isolé, on garde
    if not toks:
        # que des symboles / chiffres isolés type "| |", "@", "="
        return not re.search(r"\d{2,}", s)
    longs = [t for t in toks if len(t) > 2]
    if not longs:
        return len(s) <= 6 and not re.search(r"\d", s)
    k = [t for t in longs if known(t)]
    if any(len(t) >= 6 for t in k):
        return False
    return len(k) / len(longs) <= 0.25

out, dropped = [], []
for i, p in enumerate(pages, 1):
    lines = []
    for l in p.split("\n"):
        if is_garbage(l):
            dropped.append(f"p{i}: {l}")
            stats["lignes parasites supprimées"] += 1
            continue
        lines.append(fix_line(l).rstrip())
    body = "\n".join(lines)
    def xl(m):
        stats["article"] += 1
        return m.group(1) + m.group(2).lower() + m.group(3)
    body = re.sub(rf"([{LOW},;:’'] )(La|Les|Le)(\n+[{LOW}])", xl, body)
    lines = body.split("\n")
    body = re.sub(r"\n{3,}", "\n\n", "\n".join(lines)).strip()
    out.append(f"===== Page {i} =====\n\n{body}\n")

open(dst, "w", encoding="utf-8").write("\n".join(out))
open(droplog, "w", encoding="utf-8").write("\n".join(dropped))
for k, n in stats.items():
    print(f"{k}: {n}")
