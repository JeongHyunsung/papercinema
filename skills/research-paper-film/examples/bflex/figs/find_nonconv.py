"""Find real non-convergence prunes in the 3-bit B-Flex search (re-implementation).
Runs the same generative search as bflex_model.generate (geodesic settling
paths), records the first K non-convergence events with full context, stops."""
import sys, json
sys.path.insert(0, "../src")
from bflex_model import R, lam, nexts, geodesic_paths, ibits

def walk(delta, j, s, maxsteps=64):
    path, seen, cur = [s], {s}, s
    for _ in range(maxsteps):
        if (j, cur) not in delta: return None, path, "undefined"
        nxt = delta[(j, cur)]
        if nxt == cur: return cur, path, "ok"
        path.append(nxt)
        if nxt in seen: return None, path, "non-convergence"
        seen.add(nxt); cur = nxt
    return None, path, "non-convergence"

def search(n=3, init=(1, 3), K=40, budget=3_000_000):
    found, cnt = [], [0]
    class Stop(Exception): pass
    def rec(delta, estg, queue, hist):
        cnt[0] += 1
        if cnt[0] > budget: raise Stop
        queue = list(queue)
        while queue:
            (i, s), j = queue[0]
            s2, path, info = walk(delta, j, s)
            if info == "ok":
                if lam(s2) != R(lam(s), i, j): return
                queue.pop(0)
                if (j, s2) not in estg:
                    estg = estg | {(j, s2)}; queue += [((j, s2), k) for k in nexts(j)]
                continue
            if info == "non-convergence":
                found.append(dict(delta=[[a, b, v] for (a, b), v in sorted(delta.items())],
                                  node=[i, s], next_input=j, cycle=path, hist=hist,
                                  n_entries=len(delta)))
                if len(found) >= K: raise Stop
                return
            break
        if not queue: return
        (i, s), j = queue[0]
        o2 = R(lam(s), i, j)
        for s2 in range(2 ** n):
            if lam(s2) != o2: continue
            for p in geodesic_paths(s, s2, n):
                inf = {(j, p[k]): p[k + 1] for k in range(len(p) - 1)}; inf[(j, s2)] = s2
                if any(k in delta and delta[k] != v for k, v in inf.items()): continue
                nd = dict(delta); nd.update(inf)
                rec(nd, estg, queue, hist + [[i, s, j, s2, p]])
    i0, s0 = init
    try:
        rec({(i0, s0): s0}, {init}, [((i0, s0), j) for j in nexts(i0)], [])
    except Stop:
        pass
    return found, cnt[0]

if __name__ == "__main__":
    f, c = search()
    print("visited", c, "found", len(f))
    f.sort(key=lambda x: (x["n_entries"], len(x["hist"])))
    for x in f[:5]:
        print(x["n_entries"], "entries; depth", len(x["hist"]), "node (i,s)=", ibits(x["node"][0]), format(x["node"][1], "03b"),
              "-> i'=", ibits(x["next_input"]), "cycle", [format(c, "03b") for c in x["cycle"]])
    json.dump(f[:5], open("nonconv_cases.json", "w"), indent=1)
