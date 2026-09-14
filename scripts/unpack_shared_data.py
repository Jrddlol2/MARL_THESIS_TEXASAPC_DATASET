"""
=============================================================================
 UNPACK THE SHARED CLEANED DATA  (for a fresh clone, no 3.7 GB download)
=============================================================================

WHAT IT DOES
    Copies the cleaned files committed in data/shared/ to the places the
    scripts read them from, and checks each one against its SHA-256.

      data/shared/route_801_direction_6_clean.zip
          -> data/raw/capmetro/route_801_direction_6_clean.csv   (the study set)
      data/shared/route_801_clean_both_directions.zip
          -> data/raw/capmetro/route_801_clean_both_directions.csv
      data/shared/weather_*.csv
          -> data/processed/texas_capmetro/weather_*.csv

    A file that is already there with the right checksum is left alone.

RUN      python scripts/unpack_shared_data.py        (from the repo root, ~5 s)
         Then everything under starter/ can run. Only the data pipeline
         (scripts/pipeline/) still needs the full raw snapshot.
=============================================================================
"""

import hashlib
import os
import shutil
import sys
import zipfile

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
SHARED = os.path.join(ROOT, "data", "shared")

# (file in data/shared, file inside the zip or None, destination, sha256 of the destination file)
FILES = [
    ("route_801_direction_6_clean.zip", "route_801_direction_6_clean.csv",
     "data/raw/capmetro/route_801_direction_6_clean.csv",
     "8368412e47df32ff8a3c2837048797664315c0e7ae51c44676766b5af7f23e21"),
    ("route_801_clean_both_directions.zip", "route_801_clean_both_directions.csv",
     "data/raw/capmetro/route_801_clean_both_directions.csv",
     "24bf354b4f249a62fd264bafdbb09b61e0ac32f419adca2f8b4a95436d4d32fc"),
    ("weather_camp_mabry_2021_jul_dec.csv", None,
     "data/processed/texas_capmetro/weather_camp_mabry_2021_jul_dec.csv",
     "1d6e9ba87121888f8e23db1954d6f2dde4a8551ee4e207d7f01fa0db9429eb8c"),
    ("weather_bergstrom_2021_jul_dec.csv", None,
     "data/processed/texas_capmetro/weather_bergstrom_2021_jul_dec.csv",
     "4129e60c580acb1d3a2b50b6c80019b13c6cabcd44cd306f62d2f6e292b551ff"),
]


def sha256_of(path):
    digest = hashlib.sha256()
    with open(path, "rb") as file:
        for block in iter(lambda: file.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


problems = 0
for source_name, inner_name, destination, expected in FILES:
    source = os.path.join(SHARED, source_name)
    target = os.path.join(ROOT, destination)

    if os.path.exists(target) and sha256_of(target) == expected:
        print(f"already there   {destination}")
        continue

    os.makedirs(os.path.dirname(target), exist_ok=True)
    if inner_name is None:
        shutil.copyfile(source, target)
    else:
        with zipfile.ZipFile(source) as archive, archive.open(inner_name) as inside, open(target, "wb") as out:
            shutil.copyfileobj(inside, out)

    if sha256_of(target) == expected:
        print(f"unpacked, OK    {destination}")
    else:
        print(f"CHECKSUM WRONG  {destination}  -- do not use it")
        problems += 1

sys.exit(1 if problems else 0)
