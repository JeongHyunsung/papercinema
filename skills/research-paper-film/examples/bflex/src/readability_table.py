"""docs/readability_audit_table.md: every v3 label under 2.5 s, and its v4 fate."""
import json, re
v3 = json.load(open('../docs/audit_v3.json')); v4 = json.load(open('../docs/audit_v4.json'))
dyn = lambda k: k.startswith(("(D, CK) =", "s0 s1 s2 =")) or k in ("Q = ¬s2 = 0", "Q = ¬s2 = 1")
def tc(t):
    if t is None: return "—"
    m, s = divmod(t, 60); return f"{int(m)}:{s:05.2f}"
rows = sorted(((a['at'] if a['at'] is not None else (a['first'] or -1)), k, a['best'], v4.get(k))
              for k, a in v3.items() if a['best'] < 2.5 and not re.fullmatch(r"[\d,.\s×]+", k))
out = ["| v3 time | label | v3 readable | v4 time | v4 readable | status |", "|---|---|---|---|---|---|"]
cnt = {}
for t, k, b3, b in rows:
    if b is None or b['best'] == 0:
        st, t4, b4 = "removed (narration / step marker carries it)", "—", "—"
    else:
        t4 = tc(b['at'] if b['at'] is not None else b['first']); b4 = f"{b['best']:.2f} s"
        st = "fixed" if b['best'] >= 2.5 else ("dynamic readout (by design)" if dyn(k) else "still < 2.5 s")
    cnt[st] = cnt.get(st, 0) + 1
    kk = k.replace('|', '\\|').replace('^{', '^').replace('}', '')
    out.append(f"| {tc(t)} | `{kk[:72]}` | {b3:.2f} s | {t4} | {b4} | {st} |")
open('../docs/readability_audit_table.md', 'w').write("\n".join(out) + "\n")
print(len(rows), cnt)
