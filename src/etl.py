import requests
import re
import pandas as pd
import pathlib
import sqlalchemy

url = "http://localhost:8080/temp/pg29765.txt"
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
entries = []

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
        
        entries.append(current_entry)
        
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