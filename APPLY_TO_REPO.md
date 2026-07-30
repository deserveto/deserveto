# Apply to `deserveto/deserveto`

Copy every file and folder from this package into the root of a local clone of `deserveto/deserveto`, allowing replacements. The original MP4 is deliberately not included.

Then run:

```bash
python -m pytest tests -q
python scripts/verify_profile.py
git add README.md .gitignore bad_apple.lua assets/bad-apple-lua.gif scripts tests docs
git commit -m "feat: replace profile with Lua-style Bad Apple animation"
git push origin main
```

The profile README will render `assets/bad-apple-lua.gif` at full width and loop it continuously without audio.
