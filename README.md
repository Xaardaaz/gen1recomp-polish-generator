# Gen1Recomp Polish generator

Polish translation mod generator for Gen1Recomp — fork of BartInTheField/gen1recomp-dutch-generator.

This repository contains the pipeline and configuration to build a Polish translation mod. It follows the original project's structure and tooling.

Important notes (projekt):
- Attack names and item names will remain in English.
- Final translation will NOT use polish diacritics (ASCII-folding will be applied).

Rebuild (short):

Requirements: Python 3.11+, Git, LuaJIT, Pillow, and your own US Red/Blue ROMs placed where the pipeline expects them (see config/rom_paths.example.toml).

1) Generate Polish overrides (see scripts/translate_to_pl.py)

2) Build translation:

```sh
python build_translation.py
```

If you want to reproduce corpus generation (optional):

```sh
python scripts/generate_nl_corpus.py
python scripts/postprocess_nl_corpus.py
python build_translation.py
```

Note: You must provide ROM files locally; the build will not include ROMs.
