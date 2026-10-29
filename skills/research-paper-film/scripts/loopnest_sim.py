"""Cycle-level loop-nest simulator: the domain model behind every accelerator diagram
(references/16 §0: understand before drawing).

Given a kernel (dims, operand index functions), a mapping (ordered outer -> inner loops:
(dim, factor, 'S' | 'T')), the hardware branching factors per level and the storage
placements (level -> operands), it produces, for every cycle:
  * which PE (spatial coordinate) computes which MAC (full index tuple),
  * what every storage instance holds (operand elements), what it newly loads (fills),
  * what each storage reads and to which PEs it sends each element (data paths).
Everything a film shows about occupancy, per-PE order, refills and multicast is read from
this trace, and the paper's own numbers are asserted against it.

    from loopnest_sim import LoopNest
    L = LoopNest(dims, idx, mapping, branching, storage={1: ("I", "O"), 2: ("W",), ...})
    L.cycles            -> number of temporal steps
    L.macs(c)           -> [(pe, {dim: index})] at cycle c
    L.tile(level, o, c) -> elements of o held at `level` (one instance; see instances())
    L.fills(level, o)   -> [(cycle, new elements)] for one instance at `level`
    L.reads(level, o, c)-> {element: set(pe)} sent from that storage at cycle c
    L.utilization()     -> (active PEs, total PEs)

Conventions (Timeloop-style unified hierarchy, 1-based levels): a storage at level j
holds the footprint of loops j+1..L for the current iteration of loops 1..j (the loop at level
j itself iterates outside it for temporal levels); one instance per combination of the
spatial loops above j. (`data_kit.loop_nest_tile(..., j, ...)` counts from the first wrapped
loop, so its j equals this level + 1.) Temporal loops are nested in mapping order; the innermost temporal
loop advances every cycle.
"""
import itertools, math


class LoopNest:
    def __init__(self, dims, idx, mapping, branching, storage=None):
        self.dims, self.idx = dict(dims), idx
        self.map = [tuple(m) for m in mapping]
        self.b = list(branching)
        self.storage = storage or {}
        for d, n in self.dims.items():
            assert math.prod(f for dd, f, _ in self.map if dd == d) == n, (d, n)
        for (d, f, t), b in zip(self.map, self.b):
            assert t == "T" or f <= b, ("spatial factor exceeds branching", d, f, b)
        self.st = [math.prod(ff for dd, ff, _ in self.map[i + 1:] if dd == d) for i, (d, _, _) in enumerate(self.map)]
        self.T = [i for i, m in enumerate(self.map) if m[2] == "T"]
        self.S = [i for i, m in enumerate(self.map) if m[2] == "S"]
        self.cycles = math.prod(self.map[i][1] for i in self.T)

    # -- iteration bookkeeping ------------------------------------------------
    def titer(self, c):
        """Temporal loop values at cycle c (innermost temporal loop fastest)."""
        vals, rem = {}, c
        for i in reversed(self.T):
            vals[i] = rem % self.map[i][1]
            rem //= self.map[i][1]
        return vals

    def index(self, it):
        """Full dim index from loop values {position: value}."""
        ix = {d: 0 for d in self.dims}
        for i, v in it.items():
            ix[self.map[i][0]] += v * self.st[i]
        return ix

    def element(self, o, ix):
        return tuple(sum(ix[d] for d in expr) for expr in self.idx[o])

    def pes(self):
        """Every spatial coordinate (one value per spatial loop, padded to the branching)."""
        return list(itertools.product(*[range(self.b[i]) for i in self.S]))

    def utilization(self):
        act = math.prod(self.map[i][1] for i in self.S)
        tot = math.prod(self.b[i] for i in self.S) * math.prod(b for i, b in enumerate(self.b) if i not in self.S)
        return act, tot

    def macs(self, c):
        it = self.titer(c)
        out = []
        for pe in itertools.product(*[range(self.map[i][1]) for i in self.S]):
            full = dict(it)
            full.update({i: v for i, v in zip(self.S, pe)})
            out.append((pe, self.index(full)))
        return out

    # -- storage ----------------------------------------------------------------
    def tile(self, level, o, c, inst=None):
        """Elements of o held by the storage instance at `level` during cycle c.
        inst: values of the spatial loops above `level` (default all 0)."""
        it = self.titer(c)
        above = {i: it[i] for i in self.T if i < level}
        sp_above = [i for i in self.S if i < level]
        above.update({i: v for i, v in zip(sp_above, inst or [0] * len(sp_above))})
        inner = [i for i in range(level, len(self.map))]
        cells = set()
        for vals in itertools.product(*[range(self.map[i][1]) for i in inner]):
            full = dict(above)
            full.update(dict(zip(inner, vals)))
            cells.add(self.element(o, self.index(full)))
        return cells

    def fills(self, level, o, inst=None):
        """[(cycle, newly needed elements)] for one instance: a fill whenever the tile changes."""
        out, prev = [], None
        for c in range(self.cycles):
            cur = self.tile(level, o, c, inst)
            if cur != prev:
                out.append((c, cur - (prev or set())))
                prev = cur
        return out

    def reads(self, level, o, c, inst=None):
        """{element: set(pe)}: which PE needs which element of the storage's tile at cycle c."""
        tile = self.tile(level, o, c, inst)
        sp_above = [i for i in self.S if i < level]
        need = {}
        for pe, ix in self.macs(c):
            if any(pe[self.S.index(i)] != v for i, v in zip(sp_above, inst or [0] * len(sp_above))):
                continue
            e = self.element(o, ix)
            if e in tile:
                need.setdefault(e, set()).add(pe)
        return need
