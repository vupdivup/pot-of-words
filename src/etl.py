import requests
import re
import pandas as pd
from pathlib import Path
from sqlalchemy import create_engine, insert
from sqlalchemy.schema import CreateTable
from sqlalchemy.orm import Session
from model import Entry, Definition

# ==============================================================================
# 1. EXTRACT
# ==============================================================================

url = "https://www.gutenberg.org/ebooks/29765.txt.utf-8"
r = requests.get(url, stream=True)

r.raise_for_status()

# regex patterns for strings that signal the start of a section
patterns = {
    "content_marker": r"\*{3}.*\*{3}",
    "key": r"^[A-Z][^a-z]*$",
    "def": r"^(Defn: |\d*\. | *\([a-z]\) )",
    "note": r"^Note: ",
    "synonyms": r"^Syn\. ",
    "extra": r"^ --"
}

patterns = {k: re.compile(v) for k, v in patterns.items()}

content_flag = False
ignore_flag = False

# list for unprocessed entries
raw = []

for l in r.iter_lines():
    # decode line binary
    l = l.decode("utf-8")

    # signal content area if cursor is between the two marker lines
    if patterns["content_marker"].match(l):
        content_flag = not content_flag
        continue

    # ignore meta content
    if not content_flag:
        continue

    # ignore empty lines
    if l == "":
        continue

    if patterns["key"].match(l):
        ignore_flag = False

        current_entry = {"key": l, "info": "", "defs": []}
        current_def_idx = -1
        
        raw.append(current_entry)
        
        current_section = "key"

        continue

    if patterns["def"].match(l):
        ignore_flag = False

        current_entry["defs"].append(l)
        current_def_idx += 1

        current_section = "defs"

        continue

    # ignore synonyms, notes and additional def sections
    if (
        patterns["note"].match(l) or
        patterns["synonyms"].match(l) or
        patterns["extra"].match(l)
    ):
        ignore_flag = True

    # NOTE: checks that reset the ignore flag must come before this
    if ignore_flag:
        continue
    
    # if previous line was a key, next will always be info
    # NOTE: there are a few multiline keys, they will be parsed incorrectly
    if current_section == "key":
        current_section = "info"
    
    # append line to current section's parsed text
    if current_section == "info":
        current_entry["info"] += f" {l}"
    elif current_section == "defs":
        current_entry["defs"][current_def_idx] += f" {l}"

# ==============================================================================
# 2. TRANSFORM
# ==============================================================================

df = pd.DataFrame(raw)

# drop rows with empty info
df = df[df["info"] != ""]

# drop rows with 0 definitions
df["def_count"] = df.defs.apply(lambda x: len(x))
df = df[df.def_count > 0]

# reset index for continuous IDs
df = df.reset_index()

# ------------------------------------------------------------------------------
# 2.1 ENTRY TABLE
# ------------------------------------------------------------------------------

entries = df.loc[:, ["key", "info"]]

# make keys lowercase
entries.key = entries.key.str.lower()

# remove leading space from info line
entries["info"] = entries["info"].str.strip()

# take first word of info line as stress pattern
entries["pattern"] = entries["info"].str.split(" ", expand=True).iloc[:, 0]

# remove trailing comma after stress pattern split
entries.pattern = entries.pattern.str.removesuffix(",")

# class abbreviations found within entry info
classes = [
    # NOTE: v. must come after v. t. and v. i.
    # NOTE: this list is not complete, but reasonable
    "n.", "v. t.", "v. i.", "v.", "a.", "adv.", "prep.", "p. p.", "interj.",
    "conj.", "imp."
    ]

def determine_class(info):
    for c in classes:
        # the leading space is to ensure that class is a separate word
        if f" {c}" in info:
            return c

# set class of key to first class abbreviation that's found in info
entries["class"] = entries["info"].apply(determine_class)

# parse etimology
entries["etimology"] = entries["info"].str.split(
    " Etym: ", expand=True
).iloc[:, 1]

# remove brackets from etimology col
entries.etimology = entries.etimology.str.replace(r"[\[\]]{1}", "", regex=True)

# drop info column
entries = entries.drop(columns="info")

# ------------------------------------------------------------------------------
# 2.2 DEFINITION TABLE
# ------------------------------------------------------------------------------

# separate definition table
defs = df.loc[:, "defs"].explode()

defs = defs.str.replace("Defn: ", "")

# remove numbered defs with their own etimology
defs = defs[~defs.str.contains(r"^\d+\. Etym:")]

# remove single field labels, both with and without index
defs = defs[~defs.str.contains(r"^(?:\d+\. )*\(.*\)$")]

# remove definition indices
defs = defs.str.replace(r"^\d+\. ", "", regex=True)

defs = defs.reset_index()
defs.columns = ["entry_id", "definition"]

# ==============================================================================
# 3. LOAD TO SQLITE
# ==============================================================================

# create db folder if it does not exist
p = Path("db")
p.mkdir(exist_ok=True, parents=True)

# sql setup
engine = create_engine("sqlite:///db/dictionary.db")

# insert rows
with Session(engine) as s:
    s.execute(CreateTable(Entry.__table__, if_not_exists=True))
    s.execute(CreateTable(Definition.__table__, if_not_exists=True))

    # rename is needed to match the ORM map's inner property
    entries = entries.rename(columns={"class": "class_"})

    # bulk insert
    s.execute(insert(Entry), entries.to_dict(orient="records"))
    s.execute(insert(Definition), defs.to_dict(orient="records"))

    s.commit()