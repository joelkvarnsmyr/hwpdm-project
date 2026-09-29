# -*- coding: utf-8 -*-
"""Redigering av utgångarnas logikträd — exakt port av konfiguratorns egen kod.

Att skriva logik med script är farligare än att skriva värden: ett felformat
uttryck upptäcks inte av något, det bara beter sig fel i bilen. Därför är detta
inte en egen tolkning utan en rad-för-rad-port av app.asar 1.3.1:

    src/configOutputFunction.js
        cleanUpOutputFunction()          -> cleanup_infix()
        FunctionLinesToSerialFunction()  -> infix_to_function()

BEVISET att porten stämmer är `roundtrip_check()`: den bygger om `function` ur
`functionInfix` för VARJE utgång i filen och kräver exakt likhet med det appen
själv skrev. Går den igenom vet vi att vår förståelse av formatet är korrekt.
Kör den alltid före och efter en logikändring.

FORMAT (utläst ur porten ovan)
  functionInfix ar en lista av rader:
      [1, var, 2, op, markor, varde]   villkorsrad (langd 6)
      ['2','1']                        AND
      ['2','2']                        OR
      [0]                              tom plats ("..." i GUI:t)
  function ar raderna hopslagna till en platt lista, med totallangden forst.

  En gren avslutas med AND + tom plats. Den tomma platsen FORE ett OR ar
  grenens lediga AND-lucka — det ar den man fyller. Den sista tomma platsen i
  hela arrayen ar i stallet "lagg till ny OR-gren" och far INTE fyllas.
"""

AND_ROW = ['2', '1']
OR_ROW = ['2', '2']
GAP_ROW = [0]


def _is(row, pattern):
    return [str(t) for t in row] == pattern


def is_and(row):
    return len(row) == 2 and _is(row, AND_ROW)


def is_or(row):
    return len(row) == 2 and _is(row, OR_ROW)


def is_gap(row):
    return len(row) == 1 and str(row[0]) == '0'


def is_term(row):
    return len(row) > 2


def term(var, value, op=10, marker=1):
    """Bygg en villkorsrad. op 10 = Equals, 6 = '>'. value 1 = True, 2 = False."""
    return [1, int(var), 2, int(op), int(marker), int(value)]


# ── normalisering till LAGRAD form ───────────────────────────────────────────
def split_branches(infix):
    """Plocka ut villkoren per OR-gren. Kopplingar och tomma platser ignoreras."""
    branches, cur = [], []
    for r in infix:
        if is_or(r):
            branches.append(cur)
            cur = []
        elif is_term(r):
            cur.append(list(r))
    branches.append(cur)
    return [b for b in branches if b]


def cleanup_infix(infix):
    """Normalisera till den form konfiguratorn SJALV lagrar i filen.

    ⚠ Detta ar avsiktligt INTE en rak port av cleanUpOutputFunction(). Den
    funktionen kor pa GUI:ts arbetskopia och lamnar `[term, AND, OR]` utan tomma
    platser. Men den form som faktiskt STAR i filen har alltid en tom plats efter
    varje grens avslutande AND och en sist i arrayen — det ar de platserna GUI:t
    ritar som "..." och som man klickar for att lagga till ett villkor.
    Och `infix_to_function()` forlitar sig pa dem: den tar bara bort ett OR som
    foljs av nagot, sa ett OR SIST i listan overlever och hamnar i den platta
    arrayen. Det gav en funktion med ett hangande OR (hittat 2026-09-27).

    Formen per gren:  villkor AND villkor AND [tom]      grenar skiljs av OR
    Sist i arrayen:   ... OR [tom]
    """
    branches = split_branches([list(r) for r in infix])
    if not branches:
        return [list(GAP_ROW)]      # tom logik lagras som en ensam tom plats
    rows = []
    for bi, branch in enumerate(branches):
        if bi:
            rows.append(list(OR_ROW))
        for ti, t in enumerate(branch):
            if ti:
                rows.append(list(AND_ROW))
            rows.append(list(t))
        rows.append(list(AND_ROW))      # grenens lediga AND-lucka
        rows.append(list(GAP_ROW))
    rows.append(list(OR_ROW))           # "lagg till ny gren"-luckan
    rows.append(list(GAP_ROW))
    return rows


# ── port av FunctionLinesToSerialFunction() ──────────────────────────────────
def infix_to_function(infix):
    """Bygg den platta `function`-arrayen ur infix. Exakt appens ordning."""
    rows = [list(r) for r in infix]

    # ta bort AND som inte foljs av en villkorsrad
    i = 0
    while i < len(rows):
        if is_and(rows[i]) and i < len(rows) - 1 and not is_term(rows[i + 1]):
            del rows[i]
        else:
            i += 1

    # ta bort OR som inte foljs av en villkorsrad
    i = 0
    while i < len(rows):
        if is_or(rows[i]) and i < len(rows) - 1 and not is_term(rows[i + 1]):
            del rows[i]
        else:
            i += 1

    # ta bort tomma platser
    rows = [r for r in rows if not is_gap(r)]

    flat = []
    for r in rows:
        flat.extend(r)
    return [len(flat) + 1] + flat


# ── bevis att porten stämmer ────────────────────────────────────────────────
def roundtrip_check(cfg, verbose=True):
    """Bygg om function ur functionInfix för varje utgång. Kräv exakt likhet."""
    bad = []
    n = 0
    for section in ('OutputHS', 'OutputLS'):
        for i, out in enumerate(cfg.get(section) or []):
            inf = out.get('functionInfix')
            fn = out.get('function')
            if not inf or not fn:
                continue
            n += 1
            rebuilt = infix_to_function(inf)
            if [str(t) for t in rebuilt] != [str(t) for t in fn]:
                bad.append(f'{section}[{i}] {out.get("label")!r}\n'
                           f'      i fil : {fn}\n'
                           f'      ombyggd: {rebuilt}')
    if bad:
        raise AssertionError(
            'Rundgangen stammer INTE — formatforstaelsen ar fel, VAGRA skriva:\n  '
            + '\n  '.join(bad))
    if verbose:
        print(f'  Rundgang OK — {n} logiktrad byggdes om identiskt ur infix')
    return True


# ── redigeringen ─────────────────────────────────────────────────────────────
def add_and_term_to_all_branches(out, new_term):
    """Lägg `new_term` som ett AND-villkor i VARJE OR-gren.

    Fyller grenarnas lediga AND-luckor (de tomma platser som följs av ett OR).
    Den sista tomma platsen i arrayen är "ny OR-gren" och lämnas orörd — att
    fylla den skulle skapa en gren som står ensam och alltid kan göra utgången
    sann.

    Returnerar antalet grenar som fick termen.
    """
    rows = [list(r) for r in (out.get('functionInfix') or [])]
    if not rows:
        raise ValueError('utgangen saknar functionInfix')

    filled = 0
    i = 0
    while i < len(rows):
        if is_gap(rows[i]) and i + 1 < len(rows) and is_or(rows[i + 1]):
            rows[i] = list(new_term)
            filled += 1
            i += 1
        i += 1

    if filled == 0:
        raise ValueError('hittade ingen ledig AND-lucka — grenarna ar redan fulla')

    rows = cleanup_infix(rows)
    out['functionInfix'] = rows
    out['function'] = infix_to_function(rows)
    return filled


def set_and_chain(out, terms):
    """Ersätt utgångens logik med EN gren: term AND term AND ...

    Anvands nar en utgangs logik ska byggas om fran grunden. Foljer samma
    normalisering som GUI:t, sa resultatet blir identiskt med att klicka ihop
    det for hand.
    """
    if not terms:
        raise ValueError('minst en term kravs')
    rows = []
    for i, t in enumerate(terms):
        if i:
            rows.append(list(AND_ROW))
        rows.append(list(t))
    rows = cleanup_infix(rows)
    out['functionInfix'] = rows
    out['function'] = infix_to_function(rows)
    return len(terms)


def describe(out, names=None):
    """Läsbar form av en utgångs logik — för utskrift och granskning."""
    names = names or {}
    VAL = {1: 'True', 2: 'False'}
    OPS = {1: 'AND', 2: 'OR', 3: 'XOR', 4: 'NOR', 5: 'NAND',
           6: '>', 7: '>=', 8: '<', 9: '<=', 10: '==', 11: '!='}
    parts = []
    for r in (out.get('functionInfix') or []):
        if is_term(r):
            var, op, marker, val = int(r[1]), int(r[3]), int(r[4]), int(r[5])
            name = names.get(var, f'var{var}')
            shown = VAL.get(val, val) if marker == 1 else val
            parts.append(f'{name} {OPS.get(op, op)} {shown}')
        elif is_and(r):
            parts.append('AND')
        elif is_or(r):
            parts.append('ELLER')
    while parts and parts[-1] in ('AND', 'ELLER'):
        parts.pop()
    return ' '.join(parts)


def count_branches(out):
    """Antal OR-grenar (= antal villkorsgrupper)."""
    rows = out.get('functionInfix') or []
    return sum(1 for r in rows if is_or(r)) or 1
