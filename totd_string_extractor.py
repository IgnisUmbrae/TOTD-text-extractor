import glob
import os
from itertools import batched
from enum import Enum

class Mode(Enum):
    COLISEUM = 0
    EMPEROR = 1
    GENERAL = 2
    GENRE = 3
    WEIRD = 4
    TOWER = 5

FILENAMES = ["totd-coliseum.txt", "totd-emperor.txt", "totd-general.txt", "totd-genredict.txt", "totd-weird.txt", "totd-tower.txt"]
PATTERNS = ["ZE04*.bin", "ZE06*.bin", "Z000*.bin", "ZE05*.bin", "ZE03*.bin", "ZE01*.bin"]
SUBDIR = "extracted"

if not os.path.exists(SUBDIR) or not os.path.isdir(SUBDIR):
    try:
        os.mkdir(SUBDIR)
    except FileExistsError as e:
        print("WARNING: Failed to create directory; will output to current directory instead")
        SUBDIR = ""

print("Extracting strings…")
for mode in Mode:
    decoded_strings = []
    for file in glob.glob(PATTERNS[mode.value]):
        with open(file, "rb") as f:
            contents = f.read()

        decrypted = bytes(0x41 ^ b for b in contents).split(b"\x00"*8)[1].split(b"\x00")
        decoded = [d.split(b"\xff")[-1].decode("utf-8") for d in decrypted[::2][:-1]]

        if mode in (Mode.TOWER, Mode.GENRE):
            decoded_strings.append(decoded)
        else:
            decoded_strings.extend(decoded)

    match mode:
        case Mode.COLISEUM | Mode.EMPEROR:
            decoded_strings = ["\n".join(t) for t in batched(decoded_strings, 4)]
            joiner = "\n\n"
        case Mode.GENRE:
            decoded_strings = ["\n".join(t) for t in decoded_strings]
            joiner = "\n\n"
        case Mode.TOWER:
            decoded_strings = ["\n".join((
                t[0],
                f"✓ {'\n✓ '.join(t[1:-10])}",
                f"✕ {'\n✕ '.join(t[-10:])}"
                ))
                for t in decoded_strings]
            joiner = "\n\n"
        case Mode.GENERAL | Mode.WEIRD:
            decoded_strings = [t[0] for t in sorted([(s, len(s)) for s in set(decoded_strings)], key=lambda t: (t[1], t[0].lower()))]
            joiner = "\n"

    with open(os.path.join(SUBDIR, FILENAMES[mode.value]), "wb") as f:
        f.write(joiner.join(decoded_strings).encode("utf-8"))
print("Extraction complete!")