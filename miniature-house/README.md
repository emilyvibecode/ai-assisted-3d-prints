# Miniature house

A mixed-material architectural miniature at **working scale 1:120**, with printed structural parts, separate window/door heads, roofs, site details and candidate clear-sheet glazing. All exported coordinates and sizes are in **millimeters**.

The user reports that all project pieces have been printed. This is a project-level report; exact spool/settings and print provenance for each staged export are not independently verified. Final assembly is not verified. The current set combines v05 roofs/site components with the v06 wall frame and 24 separate heads. Earlier wall/window alternatives are omitted.

## Files and part list

- `models/structure/`: current wall frame and 24 named window/door heads. Use `head-assembly-map.csv` to match H01–H24 to openings.
- `models/roofs/`: nine existing roof sections. R6 corresponds to `roof-garage.stl` and has a known front-coverage issue.
- `models/site-and-details/`: foundation, base sections, doors, stonework, patio, pool and optional furniture/pergola pieces.
- `models/test-coupons/`: clearance, surface-detail and interface coupons plus a positioning jig; these are test aids, not all permanent assembly parts.
- `parts-manifest.json`: exact file inventory, nominal quantities, sizes and assembly translations. Quantities can exceed file counts; some files contain multiple disconnected intended pieces.
- `source/`: geometry generation code and explicit baseline mesh inputs. See its README before running it.
- `experimental/r6-garage-roof/`: one unprinted replacement candidate, excluded from the current model set.

STL meshes are normalized near their local origin. `assembly_translation_mm` places each mesh in the common assembly scene; these values are local model coordinates. Wall head `print_rotation_xyz_deg` gives the source's flat-print orientation. It is not a full slicer project or bed arrangement. Some existing multi-piece exports need splitting/arranging in the slicer.

Nominal wall envelope: **162.56 × 203.20 × 25.40 mm**. Nominal full scenic base: **223.20 × 403.54 mm**, split into sections. Overall site proportions, roof heights/topology and window sizes include estimates; this is not a measured architectural survey.

## Recorded slicing setup

The preserved wall preparation record reports Bambu H2S, original 0.4 mm nozzle, textured PEI, Bambu PLA Basic white/Jade White, 0.16 mm layers, 0.20 mm first layer and a 3 mm outside brim. Automatic normal supports were enabled, but the inspected wall slice emitted no support paths. Its Bambu Studio 02.08.02.61 offline estimate was 1 h 07 min / 28.16 g for the wall and 24 heads. These are recorded digital preparation settings and estimates, not independently confirmed settings/results of the user's completed prints.

No slicer profiles, G-code or 3MF settings archives are included. Re-slice for the actual printer, material and orientation, then inspect the layer preview. This release has not been newly slice-tested. Existing source checks do not establish adhesion, warping, strength or physical fit.

## Suggested assembly order

1. Identify the base sections and dry-fit the foundation and locators; establish a flat supported working surface.
2. Dry-fit the current wall frame on the foundation, then fit the named H01–H24 heads into their corresponding open top slots. Keep small similar heads labeled.
3. Dry-fit the nine roof sections before finishing. Check R6 over both garage openings and its rear join; do not glue it to conceal a gap.
4. Test paint, sheet material and adhesive on coupons/offcuts. Keep mating surfaces accessible. Finish printed parts separately where practical.
5. Fit doors, stone details and interior backing; install glazing while the roof remains removable. `side-glazing-candidates.csv` lists candidate insert sizes, not verified cutting dimensions. Nominal 0.25 mm sheet and about 0.55 mm pocket clearance require physical checks after paint.
6. Recheck roof alignment and access before any permanent attachment. Add hardscape, pergola, furniture and landscaping last.

Assembly guidance is proposed; no adhesive product or completed assembly is certified here. Never force tight heads against thin wall webs or peel a brim against an unsupported wall.

## Known issues and validation limits

R6's existing front plane may leave a gap over the double garage opening. The separate experimental candidate advances only the front edge by 6.35 mm, retaining the ridge, side bounds, underside and rear join. It remains mesh-checked only. Window stations, glazing fits, paint clearance and finish compatibility need physical checks. Thin webs and multi-component detail exports warrant careful slicing and handling.

`mesh-validation.json` records checks on the exact staged STL files. Watertightness, consistent winding and positive volume describe digital geometry; they do not certify manufacturability, structural performance or architectural accuracy.
