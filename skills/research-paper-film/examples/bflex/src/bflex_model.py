"""
Faithful re-implementation of the B-Flex formalism (DAC'26, Sec. 3) used to
generate and *verify* every algorithmic structure shown in the film.

Encodings
  input  i  = 2*D + CK               (so (D,CK)=(0,1) -> 1)
  state  s  = sum s_k * 2^(n-1-k)    (s0 is the MSB, as in Fig. 8f: 4*s0+2*s1+s2)
  output Q  = lambda(s) = NOT(last state bit)   (Q = ~s1 for 2-bit, ~s2 for 3-bit)
"""
from itertools import permutations

INPUTS = [0, 1, 2, 3]


def D(i): return i >> 1
def CK(i): return i & 1
def ibits(i): return f"{D(i)}{CK(i)}"


# --- Reference behaviour (Sec. 3.1.1) --------------------------------------
# Admissible transitions A: exactly one input pin changes (Gray-code ring).
A = {(0, 1), (1, 0), (1, 3), (3, 1), (3, 2), (2, 3), (2, 0), (0, 2)}
assert len(A) == 8


def nexts(i):
    return [j for j in INPUTS if (i, j) in A]


def R(o, i, j):
    """Expected next output: MSB(i') (= D) if the LSB (= CK) rises, else hold."""
    return D(j) if (CK(i) == 0 and CK(j) == 1) else o


def rbg():
    """Reference Behaviour Graph: nodes (i,o), edges per A and R."""
    nodes = [(i, o) for i in INPUTS for o in (0, 1)]
    edges = [((i, o), (j, R(o, i, j))) for (i, o) in nodes for j in nexts(i)]
    return nodes, edges


# --- Candidate AFSM (Sec. 3.1.2) -------------------------------------------
def lam(s): return 1 - (s & 1)


def stable_succ(delta, j, s, maxsteps=64):
    """Iterate s <- delta(j,s) until fixed point. Returns (s', path) or
    (None, reason)."""
    path = [s]
    seen = {s}
    cur = s
    for _ in range(maxsteps):
        if (j, cur) not in delta:
            return None, "undefined"
        nxt = delta[(j, cur)]
        if nxt == cur:
            return cur, path
        if nxt in seen:
            return None, "non-convergence"
        seen.add(nxt)
        path.append(nxt)
        cur = nxt
    return None, "non-convergence"


def validate(delta, init=(1, 3)):
    """Sec. 3.1.3 validation over the reachable ESTG. Returns (ok, info)."""
    i0, s0 = init
    if delta.get((i0, s0)) != s0:
        return False, "initial pair not stable"
    seen = {init}
    stack = [init]
    estg_edges = []
    while stack:
        i, s = stack.pop()
        for j in nexts(i):
            s2, p = stable_succ(delta, j, s)
            if s2 is None:
                return False, f"{p} at (i={ibits(i)},s={s})->i'={ibits(j)}"
            if lam(s2) != R(lam(s), i, j):
                return False, (f"wrong output at (i={ibits(i)},s={s})->"
                               f"i'={ibits(j)}: got Q={lam(s2)}")
            estg_edges.append(((i, s), (j, s2)))
            if (j, s2) not in seen:
                seen.add((j, s2))
                stack.append((j, s2))
    return True, {"nodes": sorted(seen), "edges": estg_edges}


def onebit_ok(delta):
    return all(bin(a ^ b).count("1") <= 1 for (_, a), b in delta.items())


# --- Pruning-based generative search (Sec. 3.2) ----------------------------
def geodesic_paths(a, b, n):
    """All shortest one-bit-flip paths a -> b (len = Hamming distance)."""
    diff = [k for k in range(n) if (a ^ b) >> k & 1]
    out = []
    for order in permutations(diff):
        cur, p = a, [a]
        for k in order:
            cur ^= 1 << k
            p.append(cur)
        out.append(p)
    return out


def simple_paths(a, b, n):
    """All simple one-bit-flip paths a -> b on the n-cube."""
    out = []

    def rec(p):
        c = p[-1]
        if c == b:
            out.append(list(p))
            return
        for k in range(n):
            q = c ^ (1 << k)
            if q not in p:
                p.append(q)
                rec(p)
                p.pop()
    rec([a])
    return out


def generate(n=2, init=(1, 3), paths="geodesic", record_tree=False,
             tree_limit=None):
    """Enumerate all valid AFSMs. Returns (valid_tables, tree, stats).

    The search grows the ESTG one stable edge at a time. For the current
    (node, i') job group it enumerates destinations s' (Transition Destination
    Discovery), and for each a settling path whose delta entries are inferred
    (Transition Instantiation). Pruning reasons are exactly the paper's:
      wrong output  - lambda(s') != R(lambda(s), i, i')
      entry conflict- an inferred delta entry contradicts an existing one
      non-convergence - forced existing entries never settle (cycle)
    """
    S = range(2 ** n)
    pathfn = geodesic_paths if paths == "geodesic" else simple_paths
    valid = set()
    stats = {"wrong output": 0, "entry conflict": 0,
             "non-convergence": 0, "valid": 0, "branches": 0}
    tree = {"id": 0, "label": "root", "children": [], "status": "open"}
    counter = [1]

    def node(parent, label, status, extra=None):
        if not record_tree:
            return None
        if tree_limit and counter[0] >= tree_limit:
            return None
        nd = {"id": counter[0], "label": label, "children": [],
              "status": status}
        if extra:
            nd.update(extra)
        counter[0] += 1
        parent["children"].append(nd)
        return nd

    def rec(delta, estg, queue, tnode):
        # pop pending edges whose outcome is already forced by delta
        queue = list(queue)
        while queue:
            (i, s), j = queue[0]
            o2 = R(lam(s), i, j)
            s2, info = stable_succ(delta, j, s)
            if s2 is not None:
                if lam(s2) != o2:
                    stats["wrong output"] += 1
                    if tnode is not None:
                        node(tnode, "forced", "wrong output")
                    return
                queue.pop(0)
                if (j, s2) not in estg:
                    estg = estg | {(j, s2)}
                    queue += [((j, s2), k) for k in nexts(j)]
                continue
            if info == "non-convergence":
                stats["non-convergence"] += 1
                if tnode is not None:
                    node(tnode, "forced", "non-convergence")
                return
            break  # undefined -> must branch here
        if not queue:
            key = tuple(sorted(delta.items()))
            if key not in valid:
                valid.add(key)
                stats["valid"] += 1
                if tnode is not None:
                    tnode["status"] = "valid"
                    tnode["table"] = [list(k) + [v] for k, v in key]
            elif tnode is not None:
                tnode["status"] = "duplicate"
            return
        (i, s), j = queue[0]
        o2 = R(lam(s), i, j)
        # Destination discovery: every internal state is a candidate s'
        for s2 in S:
            if lam(s2) != o2:
                stats["wrong output"] += 1
                if tnode is not None:
                    node(tnode, f"s'={s2}", "wrong output",
                         {"edge": [i, s, j, s2]})
                continue
            for p in pathfn(s, s2, n):
                stats["branches"] += 1
                inferred = {(j, p[k]): p[k + 1] for k in range(len(p) - 1)}
                inferred[(j, s2)] = s2
                bad = any(k in delta and delta[k] != v
                          for k, v in inferred.items())
                # a state may not be both transient and stable under same input
                if bad:
                    stats["entry conflict"] += 1
                    if tnode is not None:
                        node(tnode, f"s'={s2}", "entry conflict",
                             {"edge": [i, s, j, s2], "path": p})
                    continue
                nd = dict(delta)
                nd.update(inferred)
                child = None
                if tnode is not None:
                    child = node(tnode, f"s'={s2}", "open",
                                 {"edge": [i, s, j, s2], "path": p,
                                  "inferred": [[a, b, v] for (a, b), v
                                               in inferred.items()
                                               if (a, b) not in delta]})
                rec(nd, estg, queue, child)

    i0, s0 = init
    delta0 = {(i0, s0): s0}
    q0 = [((i0, s0), j) for j in nexts(i0)]
    rec(delta0, {init}, q0, tree if record_tree else None)
    tables = [dict(((a, b), v) for (a, b), v in t) for t in valid]
    return tables, tree, stats


# --- Paper data --------------------------------------------------------------
# Fig. 2: SeGen-20 transition table, rows (D,CK,s0,s1) -> (s0n,s1n)
SEGEN20_NEXT = ["00", "01", "00", "01", "01", "11", "10", "11",
                "10", "01", "10", "01", "00", "00", "10", "11"]


def segen20():
    d = {}
    for r, nx in enumerate(SEGEN20_NEXT):
        i, s = r >> 2, r & 3
        d[(i, s)] = int(nx, 2)
    return d


# Fig. 8f: transition tables of the 20 synthesized FFs (columns = (D,CK)
# 00,01,10,11; each string lists next state for current state 0..7)
FIG8F = {
    "FF1": ["4xx76767", "0xx3xx73", "4xx74545", "0xx304xx"],
    "FF2": ["xx236723", "xx334xxx", "xx674545", "xxx344xx"],
    "FF3": ["23230xxx", "xx334xxx", "01010xxx", "40x34xxx"],
    "FF4": ["2x27x7x7", "03330xx3", "050x05x5", "41x144xx"],
    "FF5": ["x1x16763", "x1334x2x", "x5xx454x", "x1x144xx"],
    "FF6": ["23230xxx", "xx334xxx", "01010xxx", "45x344xx"],
    "FF7": ["01x101xx", "13x34xxx", "45x145xx", "xxx344xx"],
    "FF8": ["2363xx6x", "0xx3xx73", "0101xx2x", "00x3xxxx"],
    "FF9": ["xx236723", "x3334xxx", "450145xx", "x1x144xx"],
    "FF10": ["232301xx", "xx334xx3", "xx674545", "xxx744x7"],
    "FF11": ["xx236723", "xx336x6x", "450145xx", "xxx3444x"],
    "FF12": ["43x36x6x", "0x33xx2x", "41x14x4x", "00x30xxx"],
    "FF13": ["01x10145", "11x3xx6x", "2367xx67", "x3x3xx66"],
    "FF14": ["232301xx", "xx334xxx", "450145xx", "xxx344xx"],
    "FF15": ["232301xx", "0x330xxx", "xx674545", "4xx344xx"],
    "FF16": ["23230xxx", "xx634x73", "01010xxx", "40x34xxx"],
    "FF17": ["23230xxx", "xx634x73", "01010xxx", "45x344xx"],
    "FF18": ["23230xxx", "xx334xxx", "01014xxx", "45x344xx"],
    "FF19": ["01x70145", "11x34x4x", "2367xx67", "x3x36x66"],
    "FF20": ["xxx76x67", "xx334x23", "xxx76x67", "xxx34445"],
}


def fig8f_table(name):
    d = {}
    for i, col in enumerate(FIG8F[name]):
        for s, c in enumerate(col):
            if c != "x":
                d[(i, s)] = int(c)
    return d


def sop_complexity(delta, n):
    """C_FF = literal count + product-term count of minimum SOP per state bit
    (don't-cares used). Exact minimisation via Quine-McCluskey + exhaustive
    cover (fine for <=5 variables)."""
    nvar = n + 2
    total = 0
    for bit in range(n):
        shift = n - 1 - bit
        on, dc = [], []
        for i in INPUTS:
            for s in range(2 ** n):
                m = (i << n) | s
                if (i, s) in delta:
                    if delta[(i, s)] >> shift & 1:
                        on.append(m)
                else:
                    dc.append(m)
        total += _min_sop_cost(on, dc, nvar)
    return total


def _min_sop_cost(on, dc, nvar):
    if not on:
        return 0
    from itertools import combinations
    terms = {(m, 0) for m in on + dc}   # (value, mask of eliminated vars)
    primes = set()
    while terms:
        nxt, used = set(), set()
        tl = list(terms)
        for a in range(len(tl)):
            for b in range(a + 1, len(tl)):
                (v1, m1), (v2, m2) = tl[a], tl[b]
                if m1 == m2:
                    x = v1 ^ v2
                    if x and not x & (x - 1):
                        nxt.add((v1 & ~x, m1 | x))
                        used.add(tl[a]); used.add(tl[b])
        primes |= terms - used
        terms = nxt
    full = (1 << nvar) - 1

    def covers(t, m):
        v, msk = t
        return (m & ~msk & full) == (v & ~msk & full)
    primes = [p for p in primes if any(covers(p, m) for m in on)]

    def cost(p):
        return nvar - bin(p[1]).count("1")
    if len(primes) == 1 and cost(primes[0]) == 0:
        return 1   # constant-1: count one (empty) product term
    best = None
    for k in range(1, len(primes) + 1):
        for combo in combinations(primes, k):
            if all(any(covers(p, m) for p in combo) for m in on):
                c = sum(cost(p) for p in combo) + k
                if best is None or c < best:
                    best = c
        if best is not None:
            # a larger cover can still be cheaper only if fewer literals;
            # continue one more size to be safe, then stop
            pass
    return best
