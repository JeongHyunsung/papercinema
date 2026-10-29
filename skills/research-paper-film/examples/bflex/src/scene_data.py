"""Builds every data-driven structure the film draws, from bflex_model and the
paper's published tables. Output: data/scene_data.json"""
import json, math, os
from bflex_model import (rbg, generate, validate, fig8f_table, stable_succ,
                         lam, R, nexts, ibits, segen20)

OUT = os.path.join(os.path.dirname(__file__), "..", "data")
os.makedirs(OUT, exist_ok=True)

# ---- RBG (Fig. 1A layout: Q=0 row, Q=1 row) -------------------------------
nodes, edges = rbg()
top = [(0, 0), (1, 0), (3, 0), (2, 0)]
bot = [(2, 1), (3, 1), (1, 1), (0, 1)]
pos = {n: (k, 0) for k, n in enumerate(top)}
pos.update({n: (k, 1) for k, n in enumerate(bot)})
rbg_json = {
    "nodes": [{"i": i, "o": o, "col": pos[(i, o)][0], "row": pos[(i, o)][1]}
              for (i, o) in nodes],
    "edges": [{"a": [a[0], a[1]], "b": [b[0], b[1]],
               "changes_q": a[1] != b[1],
               "rising": (a[0] & 1) == 0 and (b[0] & 1) == 1}
              for a, b in edges],
}

# ---- Full 2-bit search tree with radial layout -----------------------------
tables, tree, stats = generate(2, paths="geodesic", record_tree=True)
order = []        # DFS order
leaves = [0]


def lay(n, d, parent=None):
    n["depth"] = d
    n["parent"] = parent
    order.append(n)
    if not n["children"]:
        n["leaf"] = leaves[0]
        leaves[0] += 1
        n["span"] = (n["leaf"], n["leaf"])
    else:
        for c in n["children"]:
            lay(c, d + 1, n["id"])
        n["span"] = (n["children"][0]["span"][0], n["children"][-1]["span"][1])


lay(tree, 0)
NL = leaves[0]
maxd = max(n["depth"] for n in order)
flat = []
for k, n in enumerate(order):
    a = (n["span"][0] + n["span"][1]) / 2
    flat.append({"id": n["id"], "parent": n["parent"], "depth": n["depth"],
                 "theta": a / NL * 2 * math.pi, "status": n["status"],
                 "dfs": k})
tree_json = {"nodes": flat, "n_leaves": NL, "max_depth": maxd, "stats": stats,
             "n_valid": len(tables)}

# ---- Walkthrough (Fig. 4) --------------------------------------------------
root = tree
X = [c for c in root["children"]]   # first job group: i'=00 from (01,11)
walk = {
    "init": {"i": 1, "s": 3},
    "group_input": X[0]["edge"][2] if "edge" in X[0] else 0,
    "candidates": [{"s2": c["edge"][3], "status": c["status"],
                    "path": c.get("path"), "inferred": c.get("inferred")}
                   for c in X],
}
# expand: per open candidate show its sub-branches (X1 / X2 like Fig. 4)
branches = []
for c in X:
    if c["status"] != "wrong output":
        for p in [cc for cc in [c]]:
            branches.append({"s2": p["edge"][3], "path": p["path"],
                             "inferred": p["inferred"]})
walk["branches"] = branches


# shallowest real entry conflict + the delta it collides with
def find_conflict(n, delta, depth, chain=()):
    best = None
    for c in n["children"]:
        if c["status"] == "entry conflict":
            i, s, j, s2 = c["edge"]
            p = c["path"]
            inferred = {(j, p[k]): p[k + 1] for k in range(len(p) - 1)}
            inferred[(j, s2)] = s2
            clash = [(k, v, delta[k]) for k, v in inferred.items()
                     if k in delta and delta[k] != v]
            cand = (depth, {"edge": c["edge"], "path": p,
                            "clash": [[k[0], k[1], v, old]
                                      for k, v, old in clash],
                            "delta": [[a, b, v] for (a, b), v in delta.items()],
                            "chain": list(chain)})
            if best is None or cand[0] < best[0]:
                best = cand
    for c in n["children"]:
        if c["status"] in ("open", "valid") and "inferred" in c:
            nd = dict(delta)
            nd.update({(a, b): v for a, b, v in c["inferred"]})
            link = {"edge": c["edge"], "path": c["path"],
                    "inferred": c["inferred"]}
            r = find_conflict(c, nd, depth + 1, chain + (link,))
            if r and (best is None or r[0] < best[0]):
                best = r
    return best


cf = find_conflict(tree, {(1, 3): 3}, 1)
walk["conflict"] = cf[1]
walk["conflict"]["depth"] = cf[0]

# ---- ids of the walkthrough path inside the real search tree -------------
def child_match(n, edge, path, status=None):
    for c in n["children"]:
        if c.get("edge") == edge and c.get("path") == path and \
                (status is None or c["status"] == status):
            return c
    raise KeyError((edge, path, status))


chain = walk["conflict"]["chain"]
cur = child_match(tree, chain[0]["edge"], chain[0]["path"])
chain_ids = [cur["id"]]
for L in chain[1:]:
    cur = child_match(cur, L["edge"], L["path"])
    chain_ids.append(cur["id"])
conf_node = child_match(cur, walk["conflict"]["edge"], walk["conflict"]["path"],
                        "entry conflict")
tree_json["walk_ids"] = {
    "root": tree["id"],
    "cands": [c["id"] for c in tree["children"]],
    "chain": chain_ids,
    "conflict": conf_node["id"],
}
assert chain_ids[0] == tree["children"][3]["id"]          # X1 = s'=11

# ---- SeGen-20 counterexample (Fig. 2) ---------------------------------------
sg = segen20()


def run(seq):
    s, prev, q, e, states = 3, 1, [lam(3)], [lam(3)], [3]
    for j in seq:
        e.append(R(e[-1], prev, j))
        s, _ = stable_succ(sg, j, s)
        q.append(lam(s)); states.append(s); prev = j
    return {"inputs": [1] + seq, "q": q, "expected": e, "states": states}


segen = {"original": run([0, 1, 3, 2, 3, 2]),
         "modified": run([0, 1, 3, 2, 3, 1])}

# ---- FF1 (Fig. 8f) trajectory on the 3-bit cube -----------------------------
ff1 = fig8f_table("FF1")
ok, info = validate(ff1)
assert ok
seq = [0, 1, 3, 2, 3, 2, 0, 1, 0]   # capture 1 at 5th edge, then capture 0
s, prev, traj = 3, 1, []
for j in seq:
    s2, path = stable_succ(ff1, j, s)
    traj.append({"input": j, "path": path, "q_before": lam(s),
                 "q_after": lam(s2),
                 "q_expected": R(lam(s), prev, j)})
    assert lam(s2) == R(lam(s), prev, j)
    s, prev = s2, j
ff1_json = {"table": [[a, b, v] for (a, b), v in ff1.items()],
            "estg_nodes": info["nodes"], "traj": traj}

# ---- Results (Table 2 @0.9 V, Fig. 5) --------------------------------------
t2 = [  # name, group, seq overhead [ps], energy [fJ]
    ("FF1", "bflex", 19.1, 2.26), ("FF6", "bflex", 33.1, 1.62),
    ("FF9", "bflex", 60.6, 0.59), ("FF11", "bflex", 40.9, 1.62),
    ("FF20", "bflex", 31.5, 1.97), ("TGFF", "tgff", 48.2, 1.53),
    ("S2CFF", "prior", 63.6, 1.03), ("TCFF*", "prior", 68.9, 0.49),
    ("CSFF*", "prior", 61.6, 0.62), ("18TSPC*", "prior", 61.4, 0.86),
    ("STPL", "prior", 22.0, 2.69), ("REFF", "prior", 57.0, 0.59),
    ("DCPL", "prior", 31.7, 1.91), ("LCFF", "prior", 68.7, 0.57),
    ("LiRFF", "prior", 57.2, 0.68), ("SeGen", "auto", 31.3, 2.25),
    ("SeGen", "auto", 46.9, 0.64), ("SeGen", "auto", 19.2, 2.63)]
hist = {"cff": list(range(12, 21)), "count": [1, 1, 10, 7, 23, 24, 76, 101, 225]}
assert sum(hist["count"]) == 468

json.dump({"rbg": rbg_json, "tree": tree_json, "walk": walk, "segen": segen,
           "ff1": ff1_json, "table2": t2, "hist": hist},
          open(os.path.join(OUT, "scene_data.json"), "w"), indent=1)
print("stats", stats, "leaves", NL, "maxdepth", maxd)
print("conflict", walk["conflict"]["edge"], walk["conflict"]["clash"],
      "depth", cf[0])
print("X candidates", [(c["s2"], c["status"]) for c in walk["candidates"]])
print("FF1 traj", [(ibits(t["input"]), t["path"], t["q_after"]) for t in traj])
print("segen", segen)
