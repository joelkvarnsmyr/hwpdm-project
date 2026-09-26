"""Renderar alla WireViz-scheman med rätt riktning per diagram.
Kedjor/träd → TB (vertikalt, kompakt). Kontakter/fläktar → LR (horisontellt).
Kräver: ELTON-patchen applicerad (rankdir-env), Graphviz. Kör: python render_all.py
"""
import os, subprocess, glob, sys
from os.path import join, dirname, abspath, basename, splitext

HERE = dirname(abspath(__file__))
GV = r"C:\Program Files\Graphviz\bin"

# Vertikala (kedjor/träd) — allt annat blir LR (default)
TB = {
    "kraft_c3", "kraft_busbar",
    "mux_torkare_brytare", "mux_flakt_brytare", "vattentemp", "oljetryck", "handbroms",
    "bransleniva",
    "motor_tandspole_1_matning", "motor_tandspole_2_fordelare",
    "generator_1_excitering", "generator_2_laddstatus",
    # pi_1_ribbon, pi_2_displays = LR (Joel: pi bättre horisontell)
}
# Explicit LR (fläktar/översikter): kontakt_*, kraft_5v — hanteras som default

def main():
    env_base = os.environ.copy()
    if GV not in env_base.get("PATH", ""):
        env_base["PATH"] = env_base.get("PATH", "") + os.pathsep + GV
    n_ok = n_fail = 0
    for folder in ("1_kontakter", "2_kraft", "3_kretsar", "4_dash"):
        d = join(HERE, folder)
        if not os.path.isdir(d):
            continue
        for yml in sorted(glob.glob(join(d, "*.yml"))):
            name = splitext(basename(yml))[0]
            env = env_base.copy()
            env["WIREVIZ_RANKDIR"] = "TB" if name in TB else "LR"
            tmp = join(d, name + ".tmp")
            if os.path.exists(tmp):
                os.remove(tmp)
            r = subprocess.run(["wireviz", basename(yml)], cwd=d, env=env,
                               capture_output=True, text=True)
            ok = r.returncode == 0 and "error" not in (r.stderr + r.stdout).lower()
            print(f"  [{env['WIREVIZ_RANKDIR']}] {'OK ' if ok else 'FAIL'} {folder}/{name}")
            n_ok += ok; n_fail += (not ok)
            if not ok:
                print(r.stderr[-400:])
    print(f"\nKlart: {n_ok} OK, {n_fail} fel.")

if __name__ == "__main__":
    main()
