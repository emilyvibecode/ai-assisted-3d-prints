# Mac mini enclosure + phone stand

A blueberry-and-leaf enclosure, also called Bluey / Grokbot in the project notes. The phone sits above the computer so the wide front port opening remains accessible; the back remains open.

**Documentation only in this release.** Original Python geometry, STL/3MF exports and the fit-test model were not found in the searched local project folders, downloads, desktop, connected Drive or Library. The interactive visualization is schematic and is not a printable substitute. No printable enclosure assets are included.

## Intended parts

| Group | Description | Expected material/color from notes |
| --- | --- | --- |
| Base | Open-backed enclosure with wide front opening | Blue PLA |
| Lid and stand | Integrated phone rest, disc backrest and rear brace | Blue PLA |
| Bush skirt | Separate leafy lower surround | Green PLA |
| Top leaves | Two small inserts | Green PLA |
| Fit-test section | Short base section and spacers | PLA; printed twice according to notes |

Units, final dimensions, exact Mac model, phone/case model and MagSafe puck dimensions remain unverified. The intended scale is full-size around the devices, not an architectural miniature scale.

## Documented process and equipment

The process notes describe Claude Desktop / Claude Code generating Python geometry with trimesh, manifold3d and shapely, followed by Bambu Studio preparation, a small fit test and separate-color prints. The reported printer is a Bambu Lab H2S with AMS 2 Pro, using blue and green PLA. Only one blue spool was available, motivating separate blue and green parts.

The original 3MF exports were geometry-only, without a complete printer-settings bundle. Final nozzle, layer height, wall count, infill, support settings, print times and filament totals are not recorded reliably enough to publish as tested settings. No reproducible build command is available without the original source.

## Intended assembly sequence

1. Slide the skirt over the base.
2. Align and secure the lid; alignment pins alone do not establish retention when removing the phone.
3. Add the two small leaves.
4. Fit the MagSafe puck and route its cable.
5. Slide the Mac in from the rear, checking ports, power-button access and airflow.

This sequence comes from the design notes. The final adhesive/tape, fit adjustments and assembly retention method remain undocumented. Physical strength, phone retention and thermal performance have not been documented as tested.

## Needed for a fabrication release

Recover the approved source and final base, lid/stand, skirt, leaves and fit-test exports. Verify device/accessory dimensions, model units and bounds, exact final slicer settings, fit-test result, actual assembly method and real-world retention/thermal checks. Preserve any original rights notices when the original files are recovered.
