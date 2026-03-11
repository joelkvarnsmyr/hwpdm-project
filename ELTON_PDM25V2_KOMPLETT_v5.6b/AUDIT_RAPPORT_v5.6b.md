# Auditrapport — ELTON PDM25 V2 Konfiguration v5.6b
**Granskad av:** GitHub Copilot  
**Datum:** 2026-03-05  
**Källdokument:** ELTON_PDM25V2_KABELMARKNING_v5.6.md + PDM15_25_35_Instruction_Manual.md v1.0  
**Status:** Ej verifierad mot .xlsx-konfig (binärt format — kan ej läsas automatiskt)

---

## ⛔ KRITISKA FEL (åtgärd krävs innan montering)

---

### K1 — O23 Starter: "start"-variabeln är odefinierad

**Plats:** Output-tabell, O23 Funktion = `GF1 AND start`

"start" förekommer **ingenstans** i input-konfigurationen (I1–I16), i Generic Functions eller i Timer-listan.  
Configuratorn kan inte bygga denna logik — fältet är tomt/ogiltigt som det ser ut nu.

**Vad saknas:**  
En input för startknapp. Trolig lösning: anslut tändningslåsets terminal 50 (startläge, momentärt) till en ledig input (t.ex. I15), konfigurera som Momentary/Active High, och uppdatera O23-funktionen till `GF1 AND I15 Status`.

---

### K2 — O23 Starter: Stay On 10 s är farligt

**Plats:** Output-tabell, O23, Stay On = 10s

Manualen förklarar: *"After an output is commanded to turn off, the output will remain switched on for the Stay On time."*  
Det betyder att startmotorn fortsätter köra i 10 sekunder efter att startkommandot försvinner — oavsett om motorn har startat eller inte.

**Risk:** Om motorn startar och sedan binder sig startmotorn mot kuggkransen i 10 sekunder → grav mekanisk skada.  
**Korrekt värde:** 0 s Stay On. Startmotorn ska stanna omedelbart när startknappen släpps.  
**Retries = 0** är korrekt (ska inte återförsöka vid felström).

---

### K3 — O7 Parkljus: kräver tändning — men ska fungera utan

**Plats:** Output-tabell, O7 Funktion = `GF1`  
**GF1** = `I16 Status = True` = tändning PÅ

Parkljus (terminal 58 i original) är per definition en **terminal 30-krets** — ska fungera med tändning AV, bil parkerad. Nutida krav, trafikförordning och VW originalschema bekräftar detta.

**Paradoxen:** I7 (`PARK`) är konfigurerad som input (Momentary, Active High) men används **inte** i O7:s funktion. Inputen finns — men kopplas aldrig in.

**Korrekt O7-funktion:** `I7 Status` (enbart). Alternativt: `I7 Status OR (GF1 AND I7 Status)` om man vill ha en extra interlock, men i grunden — parkljus ska lysa utan tändning.

---

### K4 — Tändspole (kl.15): ingen PDM-output, ingen säkring dokumenterad

**Plats:** Motorer och tillbehör, `PDM.OUT.IGNITION` — Output: **"—"**

Etiketten `PDM.OUT.IGNITION` finns i den gula listan (nr 21) men har varken Output-nummer eller pin tilldelad. Direktkabeln `PDM.ENG.COIL.N6` (ws/li, 1.0mm²) går N6 → Tändspole kl.15 utan PDM-skydd.

**Problem:**  
- Tändkretsen är oskyddad (ingen fuse, ingen PDM-strömövervakning)  
- Om kretsen kortsluts: risk för kabelbrand  
- Det är oklart varifrån kl.15-ström faktiskt tas (från tändningslås S7 direkt? Via PDM? Via busbar?)  

**Rekommendation:** Antingen tilldela en PDM-output (t.ex. O3, ledig HS/LS) för tändspolen, eller dokumentera säkringen explicit om det är en direktkrets.

---

## ⚠️ BETYDANDE BRISTER (bör åtgärdas)

---

### B1 — ~~Huvudkabel till M8-stud undersizad~~ ✅ ÅTGÄRDAT

Kabeln är uppgraderad till **32mm²** vilket överstiger manualens rekommendation om 2 AWG (≈33mm²). Godkänt.

---

### B2 — Bränslepump (O25) saknar motor-stall-skydd

**Plats:** O25 Funktion = `GF1` (tändning PÅ → pump PÅ)

Om motorn stannar i fart (bränsleavstängning, motorstopp) men tändnyckeln sitter kvar i läge II: pumpen fortsätter mata bränsle oavbrutet. För en förgasarmotor (CH) innebär detta risk för förgasarsvämning och potentiell brandrisk vid läckage.

**Best practice:** Koppla pumpen till ett oljetrycksinterlock:  
`GF1 AND (F1_OilPressure > threshold OR start_signal)`  
F1 (oljetrycksgivare) skickas redan till RPi GPIO — det behövs ett analog/digital-input på PDM:en också, eller en CAN-signal tillbaka från RPi.

Stay On = 2s är rätt idé (pumpen lever kvar 2s efter tändning av, för enklare återstart), men skyddar inte vid stopp med tändning kvar.

---

### B3 — Resetfunktion odefinierad i praktiken

**Plats:** General Settings, Reset Function = *"Manual (CAN keypad / I15 om den tilldelas)"*

I15 är dokumenterad som **RESERVE15 — Ledig**. Ingen CAN keypad installeras. Det finns alltså ingen praktisk resetmekanism för trippade outputs i nuläget.

Om O4 (broms), O5/O6 (blinkers) eller O25 (pump) trippar på överkström: **det enda sättet att återställa är att slå av och på spänningen** (starta om PDM).

**Rekommendation:** Tilldela I15 som reset-input (t.ex. ett dolt tryckknapp i kupén), konfigurera Reset Function = `I15 Status = True`.

---

### B4 — CAN-buss: RPi CAN HAT terminering oklar

**Plats:** CAN-buss sektion, "Extern 120Ω krävs **endast på RPi-sidan**"

Många Raspberry Pi CAN HATs (t.ex. Waveshare, PiCAN2, MCP2515-baserade) har en **inbyggd 120Ω jumper som är aktiverad som standard**. Om HAT-terminering är PÅ och man lägger till en extern 120Ω dessutom: bussen har 3 parallella termineringar = 40Ω totalt i stället för 60Ω. Detta ger reflektionsproblem och ökad felfrekvens vid 250 kbps.

**Åtgärd:** Verifiera om RPi CAN HAT har inbyggd terminering. Om ja: använd HAT-termineringen och montera INGEN extern 120Ω. Om HAT saknar terminering: montera extern 120Ω vid HAT-kontaktet.

---

### B5 — Starterinterlock saknas (motorn igång → startmotor disablas ej)

**Plats:** O23 STARTER, ingen RPM- eller oljetrycksinterlock

Om tändningen är PÅ (GF1=True) och startknappen (I15/odefinierad) råkar aktiveras med motorn igång: O23 aktiveras och startmotorn engageras mot en redan roterande motor. Standardproblem med kuggkransskador.

**Rekommendation:** Lägg till en oljetrycksinterlock: `GF1 AND start_input AND NOT (OilPressure > threshold)`. Hög oljetryck = motorn är igång = startmotor blockeras.

---

### B6 — K2 Laddningslampa + K3 Oljetryck + K28 Kyltemp: beroende av RPi

**Plats:** INST.LAMP.* etiketter utan direkta PDM-outputs

Tre säkerhetskritiska varningslampor (laddning, oljetryck, kyltemp) drivs uteslutande via RPi (CAN/GPIO). Om RPi hänger sig, bootar om eller har mjukvarufel: **inga varningslampor lyser**, oavsett vad som händer i motorrummet.

**Rekommendation:** Minst K3 (oljetryck) bör ha en direktkoppling — om inte via PDM-output, så åtminstone via en inline LED+resistor direkt från F1 till 12V, fristående från RPi.

---

## 📝 MINDRE BRISTER / DOKUMENTATIONSFEL

---

### D1 — PDM.OUT.PARK-L och PDM.OUT.PARK-R delar samma output och pin

**Plats:** Signal- och positionsljus-tabell

Båda raderna anger `O7 / D6`. Det är en enda utgång som delar sig till alla 4 parkljuslampor. Etiketterna `-L` och `-R` antyder två separata kablar från PDM, men det är i praktiken ett gemensamt uttag som sedan splittas.

**Risk:** Felaktig märkning kan leda till förvirring vid felsökning ("var sitter PARK-L-kabeln?"). Etiketten på kabeln från D6 borde vara `PDM.OUT.PARK` (utan L/R), och splitten märks sedan med `-L`/`-R` vid grenuttaget.

---

### D2 — Blåsfläkt (E9) spänningsdelartabell ej dokumenterad

**Plats:** I1 BLOWER — Analog, "E9 fläktvred (4.7k+4.7k)"

PWM-tabellen visar 0% vid 0–5V, 40% vid 6V, 70% vid 10V, 100% vid 12V. Men hur E9:s switch-positioner (OFF/1/2/3) faktiskt skapar dessa spänningar via 4.7kΩ+4.7kΩ-delaren är inte dokumenterat.

**Vad saknas:** En tydlig tabell: switch-position → spänning ut ur delaren → PWM-duty. Utan detta kan man inte verifiera att fläkthastigheterna är korrekta.

---

### D3 — `PDM.ENG.COIL.T1` märkt som gul etikett (PDM.OUT) men är en motorsignalkabel

**Plats:** Direktkablar motorrum, etikett nr 29

`PDM.ENG.COIL.T1` (gn, 1.0mm²) = Tändspole kl.1 → Fördelare. Detta är en **signalkabel** (tändsignal från spole till fördelare), inte en PDM-output. Att märka den med gul tejp (PDM.OUT-kategori) är missvisande — den är varken ansluten till PDM eller en effektutgång.

**Rekommendation:** Grön tejp (INST-kategori) eller en ny kategori för motorsignaler.

---

### D4 — Manualens jordkabelrekommendation verkar vara ett tryckfel

**Plats:** PDM15_25_35_Instruction_Manual.md, Battery Negative

Manualen skriver: *"it is recommended that at least **20 AWG** wire be used"* för groundkabeln.  
20 AWG ≈ 0.5mm² — omöjligt tunt för en PDM med 120A kombinerad output vid load dump.

ELTON-dokumentet använder 10mm² (≈8 AWG) vilket är korrekt och rimligt. Manualtexten borde troligen säga "2 AWG" (som för plus-kabeln). **Inga ändringar krävs i ELTON-dokumentet** — det är manualen som verkar ha ett tryckfel. Notera detta för kontakt med Hardwire Electronics vid behov.

---

### D5 — Helljus-indicator K1 och blinkerindikator K5 — drive-logik saknas

**Plats:** INST.LAMP.HIGHBEAM (K1), INST.LAMP.TURN (K5)

Dessa lampor är listade men hur de drivs är inte dokumenterat. I original-VW var K5 (blinkers grön) driven av blinkerrelä. I PDM-systemet blinkar O5/O6 — men inget output är mappat till K5. Om K5 sitter i serieanslutning med O5/O6-kretsen, blinkar den automatiskt, men det framgår inte av dokumentet.

---

### D6 — .xlsx-konfig ej granskad

**Plats:** ELTON_PDM25V2_CONFIG_v5.6b.xlsx

Det är det faktiska Configurator-konfigurationsfilen (.HWPDM exporterad som xlsx?). Denna fil kan ej läsas av textbaserade verktyg. Alla inställningar i denna rapport baseras uteslutande på markdown-dokumentet. **Verifiera att .xlsx faktiskt matchar markdown-dokumentets konfigurationstabell** — det är lätt att glömma uppdatera en av dem.

---

## ✅ KORREKT OCH VÄLGJORT

- **Pinout-verifiering v5.6** är grundlig: B7/B8/B9/B10/B11/D1/D10 korrigerade mot manualen — detta är viktigt och gjort rätt
- **Blinker via Timer + AND** är exakt rätt metod per manualens exempel (avsnitt "Indicator/Turn Signal Setup")
- **I12 Horn Active Low med 10kΩ pull-up** — korrekt och säkert (kabelbrottsfail-safe)
- **5V budget**: 1kΩ (5mA) + 100Ω (50mA) = 55mA av 100mA max ✓
- **CAN-terminering**: PDM i ena änden med mjukvaruterminering = korrekt topologi
- **I3 HAZARD Latching**: korrekt — en tryckning PÅ, nästa tryckning AV
- **O14/O15 Turn On Delay 3s**: elegant ersättning för J59 X-kontaktrelä
- **O11 Fläkt Stay On 30s**: restvärme-utblåsning — bra tanke
- **Torkarmotor parkkrets** (31b→53 jumper + busbar→53a via E22 AV) är välanalyserad och dokumenterad
- **Global Cut-Off < 10.0V** skyddar batteriet — korrekt
- **Ändringslogg** är välförd och versionshanterad

---

## SAMMANFATTNING PRIORITETSORDNING

| Prioritet | ID | Beskrivning | Status |
|-----------|-----|-------------|--------|
| 🔴 Kritisk | K1 | Definiera "start"-input (I15 föreslaget) för O23 | ✅ **ÅTGÄRDAT v5.7** |
| 🔴 Kritisk | K2 | O23 Stay On 0s (inte 10s) | ✅ **ÅTGÄRDAT v5.7** |
| 🔴 Kritisk | K3 | O7 funktion = I7 Status (inte GF1) — parkljus utan tändning | ✅ **ÅTGÄRDAT v5.7** |
| 🔴 Kritisk | K4 | Dokumentera/skydda tändspole-kretsen (fuse eller PDM-output) | ✅ **ÅTGÄRDAT v5.7** — O3=IGN COIL 5A |
| ~~🟠 Viktig~~ | ~~B1~~ | ~~Överväg 25mm² på M8-stud-kabeln~~ | ✅ **ÅTGÄRDAT** — 32mm² monterad |
| 🟠 Viktig | B2 | Bränslepump-interlock vid motorstall | ✅ **DOKUMENTERAT v5.7** — RPi CAN |
| 🟠 Viktig | B3 | Definiera resetfunktion | ✅ **ÅTGÄRDAT v5.7** — CAN / strömcykel |
| 🟠 Viktig | B4 | Verifiera RPi CAN HAT terminering | ✅ **DOKUMENTERAT v5.7** |
| 🟠 Viktig | B5 | Starterinterlock mot igångvarande motor | ✅ **DOKUMENTERAT v5.7** — RPi CAN |
| 🟡 Bör fixas | D1 | Parkljus-etiketter: PDM-sida vs grenuttag | ✅ **ÅTGÄRDAT v5.7** |
| 🟡 Bör fixas | D2 | Dokumentera E9 switch-position → spänning → PWM-tabell | ✅ **ÅTGÄRDAT v5.7** |
| 🟡 Notera | D3 | COIL.T1 = inte en PDM-output, fel tejpfärg | ✅ **ÅTGÄRDAT v5.7** — grön tejp |
| 🟡 Notera | D6 | Verifiera .xlsx mot markdown-konfig | ⚠️ **KVARSTÅR** — binärt format |

---

*Rapporten baseras på dokumentgranskning. Praktisk verifiering med PDM ansluten rekommenderas alltid.*