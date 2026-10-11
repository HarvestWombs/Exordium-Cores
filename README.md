# Exordium Cores

The game cores Exordium installs: one folder per Diablo II patch (`1.00` … `1.13d`), each holding that
patch's DLLs, `Game.exe`, `Patch_D2.mpq` and an `exordium.mod.json` that names the core and its art.

## Changing a core

Edit the folder and push to `main`. The **Release cores** workflow zips every core (`build.py`), writes
`cores.json` and `SHA256SUMS.txt`, and publishes them as a new release. Exordium reads
`releases/latest/download/cores.json` and checks every download against its SHA-256.

To build locally: `python build.py` writes the same files to `dist/` (without download links).

1.14 and later are not here: Exordium uses the player's own install for those.
