#!/usr/bin/env python3
"""
Simple helper to generate Polish overrides from a source JSON by applying MT (configurable) and ASCII-folding.

Usage:
  python scripts/translate_to_pl.py --source <path_or_url> --out overrides/pl/overrides.json

Translation strategy (in order):
- If TRANSLATION_MODE=hf and transformers is installed, try to use Helsinki/opus-mt-en-pl or similar model.
- If env var TRANSLATE_CMD is set, call that command with the text on stdin and read stdout as translation.
- Otherwise, fallback to noop (copy source strings unchanged).

The script performs a recursive walk of the JSON structure and translates string values.
It will skip terms listed in overrides/pl/preserve_terms.txt if present.
After translation the text is ASCII-folded (diacritics removed) to meet the no-diacritics requirement.

Note: This script is a helper. You should run tests and validate outputs using the repository's validate/build pipeline.
"""

import argparse
import json
import os
import re
import subprocess
import sys
import unicodedata
from typing import Any, Dict, List


def ascii_fold(s: str) -> str:
    return unicodedata.normalize('NFKD', s).encode('ascii', 'ignore').decode('ascii')


def load_preserve_terms(path: str) -> List[str]:
    if not os.path.exists(path):
        return []
    with open(path, 'r', encoding='utf-8') as f:
        return [line.strip() for line in f if line.strip()]


def should_preserve(s: str, preserve_terms: List[str]) -> bool:
    if not preserve_terms:
        return False
    for t in preserve_terms:
        # simple containment check, case-insensitive
        if t.lower() in s.lower():
            return True
    return False


def translate_text_hf(texts: List[str]) -> List[str]:
    # optional path: use transformers if available
    try:
        from transformers import MarianMTModel, MarianTokenizer
    except Exception:
        raise RuntimeError('transformers not available')
    model_name = os.environ.get('HF_MODEL', 'Helsinki-NLP/opus-mt-en-pl')
    tokenizer = MarianTokenizer.from_pretrained(model_name)
    model = MarianMTModel.from_pretrained(model_name)
    translated = []
    batch = tokenizer(texts, return_tensors='pt', padding=True)
    gen = model.generate(**batch)
    outs = tokenizer.batch_decode(gen, skip_special_tokens=True)
    return outs


def translate_text_cmd(text: str, cmd: str) -> str:
    # call external command, send text to stdin, read stdout
    p = subprocess.Popen(cmd, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    out, err = p.communicate(text)
    if p.returncode != 0:
        raise RuntimeError(f"Translation command failed: {err}")
    return out.strip()


def translate_value(val: str, mode: str, preserve_terms: List[str], cmd: str) -> str:
    if should_preserve(val, preserve_terms):
        return ascii_fold(val)
    if mode == 'hf':
        try:
            out = translate_text_hf([val])[0]
            return ascii_fold(out)
        except Exception as e:
            print(f"HF translation failed: {e}", file=sys.stderr)
            # fallback to cmd
            if cmd:
                out = translate_text_cmd(val, cmd)
                return ascii_fold(out)
            return ascii_fold(val)
    elif mode == 'cmd' and cmd:
        out = translate_text_cmd(val, cmd)
        return ascii_fold(out)
    else:
        # noop
        return ascii_fold(val)


def walk_and_translate(obj: Any, mode: str, preserve_terms: List[str], cmd: str) -> Any:
    if isinstance(obj, dict):
        return {k: walk_and_translate(v, mode, preserve_terms, cmd) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [walk_and_translate(v, mode, preserve_terms, cmd) for v in obj]
    elif isinstance(obj, str):
        return translate_value(obj, mode, preserve_terms, cmd)
    else:
        return obj


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--source', help='Path or URL to source JSON', default='https://raw.githubusercontent.com/BartInTheField/gen1recomp-dutch-generator/main/overrides/nl/overrides.json')
    parser.add_argument('--out', help='Output path', default='overrides/pl/overrides.json')
    parser.add_argument('--mode', help='Translation mode: hf, cmd, noop', default=os.environ.get('TRANSLATION_MODE', 'cmd'))
    parser.add_argument('--cmd', help='External translation command (if using cmd mode)', default=os.environ.get('TRANSLATE_CMD', ''))
    args = parser.parse_args()

    preserve_terms = load_preserve_terms('overrides/pl/preserve_terms.txt')

    # load source
    data = None
    if args.source.startswith('http'):
        import urllib.request
        with urllib.request.urlopen(args.source) as resp:
            data = json.load(resp)
    else:
        with open(args.source, 'r', encoding='utf-8') as f:
            data = json.load(f)

    out = walk_and_translate(data, args.mode, preserve_terms, args.cmd)

    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    with open(args.out, 'w', encoding='utf-8') as f:
        json.dump(out, f, ensure_ascii=False, indent=2)

    print(f'Written {args.out}')


if __name__ == '__main__':
    main()
