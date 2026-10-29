"""Make Inter Regular selectable by name for cairo's toy font API.

On this system fontconfig resolves the family name "Inter" to the Medium face
(Inter-Medium.otf also lists the style "Regular"), so text meant to be Regular
came out Medium. This writes a copy of Inter-Regular.otf whose only family name
is "Inter Regular" into ~/.fonts and refreshes the font cache. The glyphs are
unchanged; only the name table differs.

    python3 setup_fonts.py [path/to/Inter-Regular.otf]
"""
import os, subprocess, sys
from fontTools.ttLib import TTFont

SRC = sys.argv[1] if len(sys.argv) > 1 else \
    "/usr/share/fonts/opentype/inter/Inter-Regular.otf"
DST = os.path.expanduser("~/.fonts/InterRegular-Fig.otf")

f = TTFont(SRC)
name = f["name"]
for rec in list(name.names):
    if rec.nameID in (16, 17, 21, 22):            # typographic family/style
        name.removeNames(nameID=rec.nameID)
for pid, eid, lid in ((3, 1, 0x409), (1, 0, 0)):
    name.setName("Inter Regular", 1, pid, eid, lid)
    name.setName("Regular", 2, pid, eid, lid)
    name.setName("Inter Regular", 4, pid, eid, lid)
    name.setName("Inter-Regular", 6, pid, eid, lid)
os.makedirs(os.path.dirname(DST), exist_ok=True)
f.save(DST)
subprocess.run(["fc-cache", "-f", os.path.dirname(DST)], check=True)
print("wrote", DST)
