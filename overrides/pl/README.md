# Instructions for generating Polish overrides

This folder will contain the generated overrides for Polish (overrides/pl/overrides.json).

Workflow (recommended):

1. Ensure you have the original repository data available; the script by default fetches the Dutch overrides from the original project as a starting point.
2. Configure translation method (see scripts/translate_to_pl.py) — options: local HF model (if you have transformers installed), external command (TRANSLATE_CMD) or noop (copy source).
3. Run the translator script to produce overrides/pl/overrides.json.
4. Run `python build_translation.py` to build the mod. Provide ROMs locally as required.

Preservation rules:
- Attack names and item names are left in English. If you have a list of terms to preserve, create a file `overrides/pl/preserve_terms.txt` (one term per line).
- All output will be ASCII-folded (no polish diacritics) to match your preference.
