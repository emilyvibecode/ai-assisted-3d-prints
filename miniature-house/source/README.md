# Editable geometry source

`baseline/` is the v05 geometry generator with private reference metadata and image rendering removed. It creates intermediate baseline meshes, including an older wall shell. That older wall shell is an input to the v06 wall modification; it is not the current wall to print.

`walls/` generates the current wall frame and 24 heads from explicit preserved baseline inputs in `reference-inputs/`. Those inputs are geometry-only exports. The generator checks reconstructed pockets, apertures, foundation contact, wall bounds and original head preservation.

## Reproduction

The sanitized source was executed successfully in Python 3.9 using the exact dependency versions in `requirements.txt`. Run in a disposable copy so generated files remain separate from the curated release exports:

```sh
python -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements.txt
mkdir -p baseline/parts walls/parts
python baseline/build.py
python walls/build_wall_candidate.py
```

The environment setup commands describe how to provision the recorded dependencies; this release was verified in an already installed environment, without a new package installation. Both Python generators were actually run on sanitized copies. Their outputs were geometrically compared against the curated current meshes. See `../source-validation.json`.

Baseline output includes reference OBJ inserts and intermediate metadata; these are not clear glazing to print. `walls/parts/miniature-house-v06-wall-frame.stl` and its heads supersede the baseline wall and heads. Consult the curated `../parts-manifest.json` for the final selection and quantities. Generated STL headers can differ from the sanitized release headers; compare geometry, not file bytes.

The sources do not generate the experimental R6 replacement. They do not launch a slicer, contact a printer or establish physical fit. No STEP/native CAD feature tree is available in this release.
