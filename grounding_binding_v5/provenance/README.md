# Protocol verification

`protocol_original.zip` preserves the protocol bytes corresponding to `PROTOCOL.md` in `FROZEN_SHA256SUMS`. The readable `PROTOCOL.md` is the edited documentation copy. `verify_archive.py` checks the archived original against the frozen hash; `SHA256SUMS` checks the current documentation and archive files.
