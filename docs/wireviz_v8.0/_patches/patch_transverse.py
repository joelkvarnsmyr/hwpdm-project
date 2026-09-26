"""Lokal, reversibel patch till installerade WireViz: tvärgående ringmärken på kablar.

En kabel vars `notes` innehåller [[tvar]] OCH har en tvåfärgad ledare (t.ex. BUYE) ritas
med basfärgen + periodiska tvärgående märken i andrafärgen (ringmärkning), i stället för
de vanliga längsgående ränderna. [[tvar]] döljs i den visade noten.

  python patch_transverse.py          # applicera (idempotent, backup .elton.bak)
  python patch_transverse.py --revert # återställ från backup

OBS: skrivs över vid `pip install --upgrade wireviz` — kör om patchen då.
"""
import sys, os, shutil, importlib.util

spec = importlib.util.find_spec("wireviz")
H = os.path.join(os.path.dirname(spec.origin), "Harness.py")
BAK = H + ".elton.bak"
MARK = "ELTON_TRANSVERSE_PATCH"

OLD_WIRE = """                wirehtml.append('     <table cellspacing="0" cellborder="0" border="0">')
                for j, bgcolor in enumerate(bgcolors[::-1]):  # Reverse to match the curved wires when more than 2 colors
                    wirehtml.append(f'      <tr><td colspan="3" cellpadding="0" height="2" bgcolor="{bgcolor if bgcolor != "" else wv_colors.default_color}" border="0"></td></tr>')
                wirehtml.append("     </table>")"""

NEW_WIRE = """                _cols = get_color_hex(connection_color, pad=pad)  # ELTON_TRANSVERSE_PATCH
                _tv = isinstance(cable.notes, str) and ('[[tvar]]' in cable.notes) and len(_cols) >= 2
                if _tv:
                    _h = max(7, 2 * len(bgcolors))
                    wirehtml.append('     <table cellspacing="0" cellborder="0" border="0"><tr>')
                    for _k in range(16):
                        wirehtml.append(f'<td height="{_h}" width="10" bgcolor="{_cols[0]}" border="0"></td>')
                        wirehtml.append(f'<td height="{_h}" width="4" bgcolor="{_cols[1]}" border="0"></td>')
                    wirehtml.append('</tr></table>')
                else:
                    wirehtml.append('     <table cellspacing="0" cellborder="0" border="0">')
                    for j, bgcolor in enumerate(bgcolors[::-1]):  # Reverse to match the curved wires when more than 2 colors
                        wirehtml.append(f'      <tr><td colspan="3" cellpadding="0" height="2" bgcolor="{bgcolor if bgcolor != "" else wv_colors.default_color}" border="0"></td></tr>')
                    wirehtml.append("     </table>")"""

OLD_NOTE = "            rows.append([html_line_breaks(cable.notes)])"
NEW_NOTE = ("            rows.append([html_line_breaks(cable.notes.replace('[[tvar]]', '').strip() "
            "if isinstance(cable.notes, str) else cable.notes)])  # ELTON_TRANSVERSE_PATCH")


def revert():
    if os.path.exists(BAK):
        shutil.copy(BAK, H)
        print("Återställt från backup.")
    else:
        print("Ingen backup hittad.")


OLD_RANK = '            rankdir="LR",'
NEW_RANK = '            rankdir=os.environ.get("WIREVIZ_RANKDIR", "LR"),  # ELTON_RANKDIR_PATCH'

# Minimal kabel-rutor: bara tråden (färg + etikett), inga tjocklek/typ-rader → kompakt.
OLD_MIN = "            html.extend(nested_html_table(rows, html_bgcolor_attr(cable.bgcolor)))"
NEW_MIN = ("            if os.environ.get(\"WIREVIZ_MINIMAL_CABLES\"):  # ELTON_MINIMAL_PATCH\n"
           "                rows = ['<!-- wire table -->']\n"
           "            html.extend(nested_html_table(rows, html_bgcolor_attr(cable.bgcolor)))")


def apply():
    src = open(H, encoding="utf-8").read()
    if MARK in src and "ELTON_RANKDIR_PATCH" in src and "ELTON_MINIMAL_PATCH" in src:
        print("Redan patchad (transverse + rankdir + minimal).")
        return
    if not os.path.exists(BAK):
        shutil.copy(H, BAK)
    # 1) import os (för rankdir-env)
    if "\nimport os\n" not in src:
        src = src.replace("import re\n", "import os\nimport re\n", 1)
    # 2) rankdir via miljövariabel (per-diagram TB/LR)
    if "ELTON_RANKDIR_PATCH" not in src:
        assert OLD_RANK in src, "Hittar inte rankdir-raden."
        src = src.replace(OLD_RANK, NEW_RANK)
    # 3) tvärgående ringmärken
    if MARK not in src:
        assert OLD_WIRE in src, "Hittar inte wire-renderingsblocket (WireViz-version?)."
        assert OLD_NOTE in src, "Hittar inte cable.notes-raden."
        src = src.replace(OLD_WIRE, NEW_WIRE).replace(OLD_NOTE, NEW_NOTE)
    # 4) minimal kabel-rutor (env WIREVIZ_MINIMAL_CABLES)
    if "ELTON_MINIMAL_PATCH" not in src:
        assert OLD_MIN in src, "Hittar inte cable-tabellraden."
        src = src.replace(OLD_MIN, NEW_MIN)
    open(H, "w", encoding="utf-8").write(src)
    print(f"Patchad (transverse + rankdir-env): {H}\nBackup: {BAK}")


if __name__ == "__main__":
    revert() if "--revert" in sys.argv else apply()
