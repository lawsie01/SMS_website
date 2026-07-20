# Extracted technical notes from supplied brochures / drawings / certificate

Source documents (in this folder):
- SMS_Maintenance_Shaft_Brochure_Sep2025.pdf — DN375 Maintenance Shaft (AXEDO brand)
- SMS_Maintenance_Chamber_Brochure_Sep2025.pdf — DN600 Maintenance Chamber (AXEDO brand)
- SMS_Maintenance_Hole_Brochure_Sep2025.pdf — DN1000 Maintenance Hole (ROMOLD brand)
- WSAA_PA1317_Issue5_Certificate.pdf — WSAA Product Appraisal certificate
- MS_Engineering_Drawings_Rev3.pdf, MC_Engineering_Drawings_Rev3.pdf, MH_Engineering_Drawings_Rev584.pdf

This file is a working reference for building the site's content data layer. Treat brochures/drawings
as source of truth per the brief; anything flagged "CONFIRM" needs a client answer before publishing as fact.

## Cross-product standards referenced
- WSA 137:2019 — Industry standard for PVC-U/PP/PE maintenance shafts, chambers and holes for sewerage
- EN 13598-2 — Plastics piping systems, manholes/inspection chambers in traffic areas & deep installations
- EN 14396 — Fixed ladders for manholes
- AS/NZS 2566 — Buried flexible pipelines
- AS/NZS 5065 — PE/PP pipes and fittings for drainage and sewerage
- AS 3996 — Access covers and grates (NOTE: brochures render this as "AS3966" in the "Max Traffic Load"
  row of at least one spec table, but correctly as "AS 3996" elsewhere and consistently in the engineering
  drawings — this is a typo in the brochures, confirmed by cross-reference. Use "AS 3996" sitewide.)
- AS 1646 — Elastomeric seals for waterworks purposes
- WSA PS-315 / PS-340 / PS-290 / PS-230 — applicable WSAA product specifications
- WSAA Product Appraisal: brochures (dated Sept 2025) cite "PA 1317 – Issue 4"; the certificate supplied
  is "PA 1317 Issue 5" (newer, issued after the brochures). Site should cite Issue 5 — CONFIRM exact
  issue/expiry date wording from the certificate before publishing on a certification/trust page.

## Manufacture location — NOT uniform across the range
- DN375 Shaft (AXEDO): brochure states designed/engineered/manufactured in **Germany** (Nyloplast).
  The MS engineering drawing title block, however, is branded "SMS/DYKA" — CONFIRM which entity/country
  applies to which component of the Shaft assembly before stating a single country of manufacture.
- DN600 Chamber (AXEDO): brochure states designed/engineered/manufactured in the **Netherlands** (Dyka BV).
- DN1000 Hole (ROMOLD): brochure states designed/engineered/manufactured in **Germany** (Romold GmbH).
- The WSAA certificate lists separate manufacturer tables (Nyloplast Shafts; Dyka Shafts and Chambers),
  consistent with a split Germany/Netherlands supply chain. The brief's line "German/Dutch manufacture"
  is directionally correct but must be attributed per product family, not stated as one blanket claim
  applying identically to all three products on every page.

## "DN600 corrugated" (per brief)
Reading of the Chamber brochure/drawing: the DN600 Chamber's riser is constructed from DN600 SN8
corrugated PP pipe. This appears to be a construction detail of the DN600 Maintenance Chamber, not a
fourth distinct product line — CONFIRM with client before finalising IA (affects whether Products has
3 or 4 family pages).

## Weight / manual-install claim — needs qualification, not a blanket "<25kg"
DN1000 Hole component weights (from MH engineering drawing, Sheet 6):
| Component | Weight (kg) |
|---|---|
| MH Base | 50–65 |
| MH Riser 250mm | 15 |
| MH Riser 500mm | 25 |
| MH Riser 750mm | 35 |
| MH Riser 1000mm | 45 |
| MH Cone | 25 |
| Top Hat Access Cover w/ Vegetation Ring | 100–200 |
| Concrete Cover Plate option | 200 |
| Concrete Load Distribution Ring option | 180 |

The Base (50–65kg) and larger risers (750/1000mm = 35/45kg) exceed the brief's "<25kg, manual install,
no crane" claim. That claim holds for the smaller elements (250mm riser, cone) and is likely accurate
for the DN375 Shaft / DN600 Chamber's smaller components, but for the DN1000 Hole it should be phrased
as "most elements handled by 1–2 people without a crane" rather than a blanket "<25kg" figure, or scoped
per component in the spec table rather than as a single homepage-wide stat.

## DN1000 Maintenance Hole (ROMOLD) — key data for spec tables
- Clear opening access cover: 600mm
- Base part-code pattern: `MHB1000<inlet-DN><angle-code>` — e.g. MHB1000150090 = DN150 inlet, RRJ 90°
  - Angle codes: 090, 120, 150, 180S (straight), 210, 240, 270, 4WC (cross/4-way)
  - Inlet/outlet sizes offered: DN150, DN225, DN300, DN375 (32 base part codes total: 4 sizes × 8 angles)
- Riser part codes: MH10000250 / MH10000500 / MH10000750 / MH10001000 (250/500/750/1000mm heights)
- Cone: MHRC600
- Element seals: MHG0625 (600 cone/access cover), MHG1000 (1000 base/riser/cone)
- Access cover options: Standard Top Hat (ACCMHTHCSDMH, optional vegetation ring MCCVR), Option 1
  Concrete Cover Plate incorporating access cover, Option 2 Concrete Load Distribution Ring with access
  cover — all rated Class D
- Lateral drop-in connections (on-site, optional): DN100/DN150/DN200, via hole saw + rubber collar kit
  - Part numbers: LC5-LAT100MH / LC6-LAT150MH / LC7-LAT200MH (connectors), LCS100MH / LCS150MH / LCS200MH
    (hole saws)
- Installation depth: standard max 6m; max 5m in high water table/groundwater conditions
- Base socket tolerance: ±3.75° horizontal angle and gradient (simultaneously reduces max value)
- Height adjustment: cone neck can be trimmed up to 250mm max (cut between ribs, 10mm apart)
- Bedding: min 100mm below base, non-cohesive granular material (≤32mm rounded / ≤16mm broken gravel),
  compaction ≥97% DPr
- Backfill width: min 400mm standard, min 500mm in high water table/groundwater conditions
- Detailed depth-to-bill-of-materials tables exist (Table 1 for Top Hat access cover, Table 2 for Option
  1/2 access covers) mapping installation depth in ~250mm increments (1420mm–6170/6000mm range) to exact
  qty of each riser height + cone + base required — good source content for an "installation depth"
  calculator/table on the product page.

## DN375 Maintenance Shaft (AXEDO)
- Config/part codes referenced: MS8, MS9, MS14 (base configurations)
- Same standards family as above; WSA 137, EN 13598-2, AS 3996 Class D, AS 1646, WSAA PA 1317
- 100-year service life, pH 1–13 resistance, H2S/H2SO4 resistant
- Manual install, elements lightweight (see weight caveat above — confirm exact per-component weights
  for DN375 specifically before stating "<25kg" as a DN375-wide claim)

## DN600 Maintenance Chamber (AXEDO)
- Riser: DN600 SN8 corrugated PP pipe
- Same access cover options pattern as the DN1000 Hole (Top Hat / Concrete Cover Plate / Concrete Load
  Distribution Ring), Class D
- Same standards family as above

## Open items to confirm with client (see also questions asked in chat)
1. AS 3996 vs "AS3966" typo — confirm OK to standardise on AS 3996 across the new site.
2. WSAA PA 1317 Issue 5 exact issue/expiry date wording for the trust/approvals page.
3. Per-product country of manufacture — confirm Shaft is solely Nyloplast/Germany or split with Dyka.
4. Whether "DN600 corrugated" is the Chamber's riser construction (assumed) or a separate line item.
5. Exact per-component weights for DN375 Shaft and DN600 Chamber (only fully captured for DN1000 Hole
   from the supplied drawings) — confirm before publishing "at a glance" stat blocks for those two pages.
