"""Bygger ELTON service-manual (liggande A4 PDF) via xelatex.
Sätter ihop WireViz-diagrammen (PNG) + beskrivande text till en prydlig manual.

Kör:  python build_manual.py
Kräver: MiKTeX (xelatex) på PATH. Diagrammen ska vara genererade (PNG) i wireviz_v8.0/.
Ut:   ELTON_manual.pdf  (i docs/)
"""
import subprocess, os, sys, shutil
from PIL import Image
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
WV = os.path.join(HERE, "wireviz_v8.0")
SLICEDIR = os.path.join(HERE, "_manual_build")
DATE = "2026-06-17"   # stamp manually (Date.now not available in the script environment)

# Breda scheman (chains i sidled) blir oläsliga pressade till A4-bredd → dela i sidor.
# VIKTIGT: klipp BARA i mellanrummen mellan boxarna (kolumner med minst bläck = bara kablar),
# aldrig genom box/text.
SLICE_ASPECT = 3.0       # dela om bredd/höjd > detta (med TB-layout behövs sällan delning)
SLICE_TARGET_PX = 1900   # mål-bredd per del (ger ~2.2mm text vid full sidbredd)
NO_SLICE = {"pi_1_ribbon"}  # ribbon-pinouten får vara bred på en sida

def page_images(png):
    """Returnerar [(bildväg, del-etikett)]. Delar breda scheman vid tomma kolumner."""
    im = Image.open(png).convert("RGB")
    w, h = im.size
    if os.path.splitext(os.path.basename(png))[0] in NO_SLICE or w / h <= SLICE_ASPECT:
        return [(png, "")]
    n = max(2, round(w / SLICE_TARGET_PX))
    # bläck per kolumn (mörka/färgade pixlar) → boxar/text = högt, mellanrum = lågt
    gray = np.asarray(im.convert("L"))
    ink = (gray < 200).sum(axis=0)
    # hitta snitt nära varje mål-gräns, i kolumnen med MINST bläck inom ett fönster
    cuts = [0]
    for i in range(1, n):
        target = int(i * w / n)
        win = max(40, int(w / (3 * n)))
        lo, hi = max(1, target - win), min(w - 1, target + win)
        cuts.append(lo + int(np.argmin(ink[lo:hi])))
    cuts.append(w)
    os.makedirs(SLICEDIR, exist_ok=True)
    base = os.path.splitext(os.path.basename(png))[0]
    out = []
    OV = 12  # liten överlapp så kabelstumpen vid snittet syns på båda sidor
    for i in range(n):
        x0 = max(0, cuts[i] - (OV if i else 0))
        x1 = min(w, cuts[i + 1] + (OV if i < n - 1 else 0))
        p = os.path.join(SLICEDIR, f"{base}_p{i+1}.png").replace("\\", "/")
        im.crop((x0, 0, x1, h)).save(p)
        out.append((p, f" (part {i+1}/{n})"))
    return out

# --- Manual contents: (folder, file, title, description) -----------------------
SECTIONS = [
    ("Connectors", [
        ("1_kontakter", "kontakt_A_inputs",  "Connector A — Inputs (GREY)",
         "All input signals: levers, switches and senders. Switch-to-ground unless otherwise noted. "
         "Grey housing. Pin number on the left, cable in the middle (cross-section + actual color), consumer on the right."),
        ("1_kontakter", "kontakt_B_outputs", "Connector B — Outputs (BLACK)",
         "Outputs: low beam, left turn signal, horn 1, wiper low, blower, washer pump, starter motor, reversing light, USB."),
        ("1_kontakter", "kontakt_C_kraft_can", "Connector C — Power / CAN / sensors (GREEN)",
         "Control feed (C3), chassis ground, CAN to the Pi, ignition/cranking, ignition coil, alternator field excitation, "
         "signal busbar and the 5V reference distribution point."),
        ("1_kontakter", "kontakt_D_outputs", "Connector D — Outputs (BROWN)",
         "Outputs: high beam, parking light, brake light, right turn signal, fuel pump (2 parallel to the same pin), "
         "wiper high, horn 2."),
    ]),
    ("Power supply", [
        ("2_kraft", "kraft_busbar", "+12V power busbar (always-on loads)",
         "The busbar (battery-fed via a 10A ceramic fuse) supplies the always-on loads: radio and Raspberry Pi. "
         "The PDM control feed C3 has its own graph (next page)."),
        ("2_kraft", "kraft_c3", "PDM control feed C3 — ignition + hazard wake",
         "Two paths to C3 from the busbar: normally via the ignition switch (RUN), and as a wake via the hazard switch "
         "through a blocking diode. Vertical layout."),
        ("2_kraft", "kraft_5v", "5V reference — analog inputs",
         "C10 (5V REF, max 100 mA) feeds, via a distribution point, five SEPARATE pull-ups to the analog "
         "inputs (wiper/blower/turn mux plus coolant and fuel). Total load ~37 mA. "
         "Each input has its own pull-up — never shared."),
    ]),
    ("Circuits", [
        ("3_kretsar", "mux_torkare_brytare", "Mux — wiper + washer (I9): switch + resistors",
         "The resistor coding for the wiper+washer mux. Washer 10k, low 4.7k, high 22k on the switch outputs "
         "→ chassis ground; each position gives a unique node voltage. Feed/sensing (5.6k pull-up → 5V REF) "
         "is shown in the 5V-reference diagram."),
        ("3_kretsar", "mux_flakt_brytare", "Mux — blower low/high (I1): knob + resistors",
         "The blower knob's resistor coding. Low 10k, high 2.2k → chassis ground. Feed via pull-up to 5V REF: "
         "see the 5V-reference diagram. Two speeds come from O11's PWM — no power resistor."),
        ("3_kretsar", "vattentemp", "Coolant temperature — NTC (I10)",
         "NTC sender as a voltage divider against an external pull-up to 5V REF (~470-680Ω). "
         "High temperature = low resistance = low voltage. Ground via the sender thread in the engine block."),
        ("3_kretsar", "oljetryck", "Oil-pressure switch (I14)",
         "Simple switch-to-ground (F1). Internal pull-up to VBat. Low pressure / engine off = 0V (warning), "
         "engine running + pressure OK = high."),
        ("3_kretsar", "handbroms", "Handbrake warning (I16)",
         "Mechanical switch-to-ground (F9), grounds when the handbrake is applied. Internal pull-up, a copy of the brake-light input."),
        ("3_kretsar", "motor_tandspole_1_matning", "Ignition coil (1/2): feed O3 → N6 → coil",
         "Original VW, but fed by O3 instead of the ignition switch. O3 → N6 ballast resistor → coil Term. 15."),
        ("3_kretsar", "motor_tandspole_2_fordelare", "Ignition coil (2/2): coil → distributor",
         "Coil Term. 1 → distributor breaker points → ground. The points break the primary circuit → HT is induced "
         "(Term. 4 → distributor cap → spark plug, not drawn)."),
        ("3_kretsar", "generator_1_excitering", "Alternator (1/2): field excitation",
         "O2 → 82Ω power resistor → blocking diode → alternator D+. The resistor supplies field current; the diode stops "
         "D+ (~14V) back-feeding the PDM."),
        ("3_kretsar", "generator_2_laddstatus", "Alternator (2/2): charge status",
         "Charge status is tapped AFTER the diode to a spare PDM input (charging ~14V = high, not charging ~1V = low) "
         "→ CAN → charge warning lamp in the dashboard."),
    ]),
    ("Dashboard", [
        ("4_dash", "pi_1_ribbon", "Dashboard (1/2): Pi → GX16 rainbow ribbon",
         "Pi 5 → GX16 10-pin ribbon in fixed color order. Canonical GPIO source: DRIVER-DASH.md §7."),
        ("4_dash", "pi_2_displays", "Dashboard (2/2): GX16 → 3× ST7789 (SPI0)",
         "Pins 1-7 (GND/3V3/SCLK/MOSI/RST/DC/BLK) are daisy-chained to all three displays (shown as a shared bus); "
         "only CS is unique: orange→S1, red→S2, brown→S3."),
    ]),
]

INTRO = (
    r"This is the physical wiring and service manual for the conversion of a VW LT31 (1976, JSN~398) "
    r"to a Hardwire PDM25 V2 + Raspberry Pi dashboard. Each diagram shows the PDM connector on the left, "
    r"the cable in the middle (cross-section + actual color) and the consumer on the right.\\[6pt]"
    r"\textbf{Conventions:} The connectors' title bar carries the housing's physical color (A grey, B black, "
    r"C green, D brown). Cross-sections are given in mm\textsuperscript{2}. Ground is shown as a GND pin on the "
    r"consumer rather than as a drawn cable. Wire colors reflect the wiring as physically inspected in the vehicle."
)

# --- Reference appendices (lifted from the VW LT factory manual, Fig 13.77 4-cyl) ----
# Only components that actually exist on the converted car are listed.
APP_COMPONENTS = [
    ("A", "Battery (12 V)"),
    ("B", "Starter motor"),
    ("C", "Alternator"),
    ("D", "Ignition / start switch"),
    ("E2", "Turn-signal stalk"),
    ("E4", "High-beam / headlight-flasher stalk"),
    ("E9", "Blower (fresh-air fan) switch"),
    ("E22", "Wiper / washer stalk"),
    ("F", "Brake-light switch"),
    ("F1", "Oil-pressure switch"),
    ("F4", "Reversing-light switch"),
    ("F9", "Handbrake warning switch"),
    ("G", "Fuel-gauge sender"),
    ("G2", "Coolant-temperature sender"),
    ("G6", "Electric fuel pump"),
    ("H1", "Horn"),
    ("H2", "Horn 2 (additional)"),
    ("L1", "Headlight, left (twin-filament)"),
    ("L2", "Headlight, right (twin-filament)"),
    ("M5", "Turn signal, front left"),
    ("M6", "Turn signal, rear left"),
    ("M7", "Turn signal, front right"),
    ("M8", "Turn signal, rear right"),
    ("M9", "Brake light, left"),
    ("M10", "Brake light, right"),
    ("M16", "Reversing light, left"),
    ("M17", "Reversing light, right"),
    ("N", "Ignition coil"),
    ("N6", "Series (ballast) resistor"),
    ("O", "Distributor (breaker points)"),
]
APP_TERMINALS = [
    ("1", "Ignition coil primary, to distributor"),
    ("4", "Ignition coil HT output (to distributor cap)"),
    ("15", "Switched ignition + (live with ignition on)"),
    ("30", "Battery + (permanent, unswitched)"),
    ("31", "Ground (chassis earth return)"),
    ("50", "Starter control (solenoid, cranking only)"),
    ("53", "Wiper, normal speed"),
    ("53a", "Wiper, fast speed"),
    ("53b", "Wiper park / return"),
    ("56a", "High beam"),
    ("56b", "Low beam"),
    ("58", "Parking / side lights"),
]
APP_EARTH = [
    ("1", "Battery earth strap to body"),
    ("3", "Engine-to-body earth strap"),
    ("10", "Instrument-panel insert"),
    ("11", "Behind instrument panel"),
    ("12", "Under instrument panel (former fuse-box area)"),
    ("13", "At rear door"),
    ("14", "Roof cross-member, passenger side"),
    ("15", "Rear, on longitudinal member"),
    ("17", "At steering gear"),
    ("18", "Longitudinal member, rear left"),
    ("19", "Longitudinal member, rear right"),
    ("20", "In engine bay"),
]

def esc(s):
    """Escape LaTeX-specialtecken i brödtext (ej i råa LaTeX-strängar)."""
    for a, b in [('\\', r'\textbackslash{}'), ('&', r'\&'), ('%', r'\%'), ('$', r'\$'),
                 ('#', r'\#'), ('_', r'\_'), ('{', r'\{'), ('}', r'\}'), ('~', r'\textasciitilde{}'),
                 ('^', r'\textasciicircum{}')]:
        s = s.replace(a, b)
    return s

def two_col_table(rows, descw="78mm"):
    """Render (id, description) pairs as a wide 4-column table (two panels)."""
    half = (len(rows) + 1) // 2
    left, right = rows[:half], rows[half:]
    out = [r"\begin{center}\small",
           r"\begin{tabular}{|l|p{" + descw + r"}|l|p{" + descw + r"}|}", r"\hline",
           r"\textbf{ID} & \textbf{Description} & \textbf{ID} & \textbf{Description} \\ \hline"]
    for i in range(half):
        li, ld = left[i]
        ri, rd = right[i] if i < len(right) else ("", "")
        out.append(esc(li) + " & " + esc(ld) + " & " + esc(ri) + " & " + esc(rd) + r" \\ \hline")
    out += [r"\end{tabular}", r"\end{center}"]
    return out

def build_appendices(L):
    L.append(r"\section{Appendix A — Component reference}")
    L.append(r"{\small Components on the converted vehicle, by their VW designation as used in the "
             r"diagrams. From the VW LT workshop manual (Fig.\ 13.77, 4-cyl).}\\[6pt]")
    L += two_col_table(APP_COMPONENTS)
    L.append(r"\clearpage")
    L.append(r"\section{Appendix B — Terminal designations (DIN 72552)}")
    L.append(r"{\small Standard terminal numbers used throughout the diagrams.}\\[6pt]")
    L += two_col_table(APP_TERMINALS)
    L.append(r"\vspace{6pt}\par{\footnotesize\color{gray} Terminal numbers follow the DIN 72552 "
             r"standard and are common to all VW / Bosch wiring.}")
    L.append(r"\clearpage")
    L.append(r"\section{Appendix C — Earth points \& grounding}")
    L.append(r"{\small In the diagrams, ground is shown as a GND pin on each consumer rather than as a "
             r"drawn cable. The physical chassis earth points below are where those grounds terminate. "
             r"\textbf{All ground wires are brown.}}\\[6pt]")
    L += two_col_table(APP_EARTH, descw="70mm")
    L.append(r"\vspace{4pt}\par{\footnotesize\color{gray} Earth-point locations are per the VW LT factory "
             r"manual for the donor vehicle and should be confirmed on the actual car. Common gauges: "
             r"0.5 mm\textsuperscript{2} (lamps, senders), 1.0 mm\textsuperscript{2} (motors, brake lights), "
             r"4.0 mm\textsuperscript{2} and heavier (battery, engine and gearbox straps).}")
    L.append(r"\clearpage")

def build_tex():
    L = []
    L.append(r"\documentclass[11pt]{article}")
    L.append(r"\usepackage[a4paper,landscape,margin=15mm,top=18mm,bottom=16mm]{geometry}")
    L.append(r"\usepackage{fontspec}")
    L.append(r"\setmainfont{Arial}")
    L.append(r"\usepackage{graphicx}")
    L.append(r"\usepackage{xcolor}")
    L.append(r"\usepackage{fancyhdr}")
    L.append(r"\usepackage{sectsty}")
    L.append(r"\usepackage{hyperref}")
    # Dashboard-DNA: mörk yta + guld (från ELTON-logon) + röd accent (gauge-needle)
    L.append(r"\definecolor{eltongold}{RGB}{169,138,87}")    # #a98a57 logo
    L.append(r"\definecolor{eltongold2}{RGB}{208,174,120}")  # #d0ae78 logo ljus
    L.append(r"\definecolor{eltondark}{RGB}{15,15,15}")      # #0f0f0f surface
    L.append(r"\definecolor{eltonred}{RGB}{255,51,51}")      # #ff3333 gauge/varning
    L.append(r"\hypersetup{colorlinks=true,linkcolor=eltongold!80!black}")
    L.append(r"\renewcommand{\contentsname}{Contents}")
    L.append(r"\sectionfont{\color{eltongold!75!black}}")
    L.append(r"\subsectionfont{\color{eltondark}}")
    L.append(r"\pagestyle{fancy}\fancyhf{}")
    L.append(r"\fancyhead[L]{\small\color{eltongold!75!black}\textbf{ELTON} \color{gray}PDM25 V2 — Wiring manual}")
    L.append(r"\fancyhead[R]{\small\color{gray}" + DATE + r"}")
    L.append(r"\fancyfoot[C]{\small\color{gray}\thepage}")
    L.append(r"\renewcommand{\headrulewidth}{1pt}")
    L.append(r"\renewcommand{\headrule}{\hbox to\headwidth{\color{eltongold}\leaders\hrule height 1pt\hfill}}")
    L.append(r"\begin{document}")
    # --- Titelsida (mörk, dashboard-stil, med LT-logon) ---
    logo = os.path.join(WV, "_assets", "elton-logo.png").replace("\\", "/")
    L.append(r"\thispagestyle{empty}")
    L.append(r"\pagecolor{eltondark}")
    L.append(r"\vspace*{1.4cm}\begin{center}")
    if os.path.exists(logo):
        L.append(r"\includegraphics[width=0.52\textwidth]{" + logo + r"}\\[14pt]")
    L.append(r"{\fontsize{42}{48}\selectfont\bfseries\color{eltongold2} ELTON}\\[8pt]")
    L.append(r"{\color{eltongold}\rule{60mm}{1.2pt}}\\[10pt]")
    L.append(r"{\LARGE\color{white} Electrical system \& wiring}\\[4pt]")
    L.append(r"{\large\color{white!80} Wiring diagrams — service manual}\\[12pt]")
    L.append(r"{\large\color{eltongold} PDM25 V2 \quad·\quad VW LT31 1976 \quad·\quad JSN 398}\\[14pt]")
    L.append(r"{\normalsize\color{white!75} Prepared by Joel Kvarnsmyr}\\[3pt]")
    L.append(r"{\small\color{white!55} " + DATE + r"}")
    L.append(r"\end{center}\vfill")
    L.append(r"\clearpage")
    L.append(r"\pagecolor{white}")
    # --- Innehåll ---
    L.append(r"\thispagestyle{empty}")
    L.append(r"\tableofcontents\clearpage")
    # --- Inledning ---
    L.append(r"\section{Introduction}")
    L.append(INTRO)
    L.append(r"\clearpage")
    # --- Sektioner med diagram ---
    for secname, items in SECTIONS:
        L.append(r"\section{" + esc(secname) + "}")
        for folder, fname, title, desc in items:
            png = os.path.join(WV, folder, fname + ".png").replace("\\", "/")
            if not os.path.exists(png):
                print(f"VARNING saknar {png}")
                continue
            pages = page_images(png)
            for idx, (img, suffix) in enumerate(pages):
                if idx == 0:
                    L.append(r"\subsection{" + esc(title) + (esc(suffix) if suffix else "") + "}")
                    L.append(r"{\small " + esc(desc) + r"}")
                    if suffix:
                        L.append(r"\\[2pt]{\footnotesize\color{gray} Wide diagram — split across "
                                 + str(len(pages)) + r" pages with overlap.}")
                    L.append(r"\\[4pt]")
                else:
                    L.append(r"\subsection*{" + esc(title) + esc(suffix) + "}")
                L.append(r"\begin{center}")
                L.append(r"\includegraphics[width=\linewidth,height=0.74\textheight,keepaspectratio]{" + img + "}")
                L.append(r"\end{center}")
                L.append(r"{\scriptsize\color{gray} Diagram: wireviz\_v8.0/" + esc(folder + "/" + fname)
                         + (esc(suffix) if suffix else "") + r"}")
                L.append(r"\clearpage")
    # --- Reference appendices ---
    build_appendices(L)
    L.append(r"\end{document}")
    return "\n".join(L)

def main():
    if not shutil.which("xelatex"):
        sys.exit("xelatex saknas på PATH (MiKTeX).")
    shutil.rmtree(SLICEDIR, ignore_errors=True)
    tex = build_tex()
    texpath = os.path.join(HERE, "ELTON_manual.tex")
    with open(texpath, "w", encoding="utf-8") as f:
        f.write(tex)
    job = "ELTON_manual__build"   # bygg till temp-namn → byt, så låst PDF ej stoppar bygget
    for i in range(2):  # två körningar för TOC
        r = subprocess.run(["xelatex", "-interaction=nonstopmode", "-halt-on-error",
                            f"-jobname={job}", "ELTON_manual.tex"], cwd=HERE, capture_output=True, text=True)
        if r.returncode != 0:
            print(r.stdout[-2500:])
            sys.exit("xelatex misslyckades.")
    src = os.path.join(HERE, job + ".pdf")
    out = "ELTON_manual.pdf"
    try:
        os.replace(src, os.path.join(HERE, out))
    except PermissionError:
        out = "ELTON_manual_NEW.pdf"  # ELTON_manual.pdf låst (öppen i läsare)
        try:
            os.replace(src, os.path.join(HERE, out))
        except PermissionError:
            out = job + ".pdf"
        print("OBS: ELTON_manual.pdf är låst (öppen i läsare?) — skrev till", out)
    # städa hjälpfiler
    for base in (job, "ELTON_manual"):
        for ext in (".aux", ".log", ".out", ".toc"):
            p = os.path.join(HERE, base + ext)
            if os.path.exists(p):
                os.remove(p)
    shutil.rmtree(SLICEDIR, ignore_errors=True)
    print("KLAR:", out)

if __name__ == "__main__":
    main()
