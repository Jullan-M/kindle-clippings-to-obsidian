#!/usr/bin/env python3

"""
A Python-script that extracts and organises highlights/notes from the "My Clippings.txt" file on a Kindle e-reader. Formats for Obsidian.

Usage: ./extract-kindle-clippings.py <My Clippings.txt file> -o [<optional: output directory>]

Github repository: https://github.com/dannberg/kindle-clippings-to-obsidian

    Copyright 2025, Dann Berg (dannb.org)

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

import argparse
import getpass
import hashlib
import os
import re
import sys
from datetime import datetime, timedelta, timezone

from dateutil.parser import parse

from utilities import getvalidfilename, longest_common_substring_len


def parse_args():
    parser = argparse.ArgumentParser(
        description='Extract and organize highlights and notes from Kindle "My Clippings.txt" file'
    )
    parser.add_argument(
        "input_file",
        nargs="?",
        default="My Clippings.txt",
        help="Path to My Clippings.txt file (default: My Clippings.txt)",
    )
    parser.add_argument(
        "-o",
        "--output",
        default="./clippings",
        help="Output directory (default: ./clippings)",
    )
    return parser.parse_args()


def get_user_book_selection(titles):
    # Create a sorted list of unique titles
    unique_titles = sorted(list(set(titles.values())))

    print("\nSelect a book (or books) to output:")
    print("[0]: All books")
    for i, title in enumerate(unique_titles, 1):
        print(f"[{i}]: {title}")

    while True:
        try:
            selection = input(
                "\nInput one or more numbers, separated by a space: "
            ).strip()
            numbers = [int(num) for num in selection.split()]

            # Validate input
            if not numbers:
                print("Please enter at least one number")
                continue

            # Check if 0 is selected
            if 0 in numbers:
                return unique_titles

            # Validate range of numbers
            if any(num < 0 or num > len(unique_titles) for num in numbers):
                print(f"Please enter numbers between 0 and {len(unique_titles)}")
                continue

            # Return selected titles
            return [unique_titles[num - 1] for num in numbers]

        except ValueError:
            print("Please enter valid numbers separated by spaces")
            continue


args = parse_args()
infile = args.input_file
outpath = args.output

# Check if input file exists
if not os.path.isfile(infile):
    username = getpass.getuser()
    infile = os.path.join("/media", username, "Kindle", "documents/My Clippings.txt")
    if not os.path.isfile(infile):
        print(
            'Could not find "My Clippings.txt", please provide the file location as an argument'
        )
        sys.exit(1)

# Create output directory if it doesn't exist
if not os.path.isdir(outpath):
    os.makedirs(outpath, exist_ok=True)

note_sep = "=========="

commentstr = ".. "  # RST (reStructuredText) comment

regex_title = re.compile(r"^(.*)\((.*)\)$")
regex_info = re.compile(r"^- Your (\S+) (.*)[\s|]+Added on\s+(.+)$")
regex_loc = re.compile(r"location ([\d\-]+)")
regex_page = re.compile(r"page ([\d\-]+)")
regex_date = re.compile(r"Added on\s+(.+)$")
regex_num = re.compile(r"(\d+)")
regex_numrange = re.compile(r"(\d+)\-(\d+)")

regex_hashline = re.compile(r"^\.\.\s*([a-fA-F0-9]+)" + "\s*")

pub_title = {}
pub_author = {}
pub_notes = {}
pub_hashes = {}

notes = {}
locations = {}
types = {}
dates = {}

existing_hashes = {}

print("Scanning output dir", outpath)
for directory, subdirlist, filelist in os.walk(outpath):
    for fname in filelist:
        _, ext = os.path.splitext(fname)
        if ext.lower() == ".md":
            print("Found Markdown file", fname, "in directory", directory)
            # open file, find comment lines, store hashes
            md = open(directory + "/" + fname, "r", encoding="utf8")
            line = md.readline()
            lines = 0
            hashes = 0
            while line:
                lines += 1
                findhash_result = regex_hashline.findall(line)
                if len(findhash_result):
                    foundhash = findhash_result[0]
                    existing_hashes[foundhash] = fname
                    hashes += 1
                line = md.readline()
            md.close()
            print(hashes, "hashes found in", lines, "scanned lines")
        else:
            print("File", fname, "does not seem to be Markdown, skipping", ext)

print("Found", len(existing_hashes), "existing note hashes")
print("Processing clippings file", infile)

mc = open(infile, "r", encoding="utf8")

mc.read(1)  # Skip first character

line = mc.readline().strip().replace("﻿", "")

while line:

    key = line.strip()
    result_title = regex_title.findall(key)  # Extract title and author
    line = mc.readline().strip()  # Read information line
    print(line)
    note_type, location, date = regex_info.findall(line)[
        0
    ]  # Extract note type, location and date
    result_loc = regex_loc.findall(location)
    result_page = regex_page.findall(location)
    if len(result_title):
        title, author = result_title[0]
    else:
        title = key
        author = "Unknown"

    if len(result_loc):
        note_loc = result_loc[0]
    else:
        note_loc = ""

    if len(result_page):
        note_page = result_page[0]
    else:
        note_page = ""

    note_text = ""
    line = mc.readline()  # Skip empty line
    line = mc.readline().strip()

    while line != note_sep:
        note_text += line + "\n"
        line = mc.readline().strip()

    # Note / highlight text post-processing
    note_text = note_text.strip().replace("  ", " ")

    note_hash = hashlib.sha256(note_text.encode("utf8")).hexdigest()[:8]

    if key not in pub_notes:
        pub_notes[key] = []
        pub_hashes[key] = []

    pub_title[key] = title.strip()
    pub_author[key] = author.strip()
    pub_notes[key].append(note_text)
    pub_hashes[key].append(note_hash)

    locstr = ""
    if note_loc:
        locstr = "loc. " + note_loc
    if note_page:
        if note_loc:
            locstr += ", "
        locstr += "p." + note_page

    try:
        datestr = str(parse(date))
    except:
        datestr = date

    notes[note_hash] = note_text
    locations[note_hash] = locstr
    types[note_hash] = note_type
    dates[note_hash] = datestr

    line = mc.readline().strip()

# Sort highlights according to how when they chronologically appear in the book, not when they were highlighted.
for k in pub_hashes.keys():
    print(k)
    if "loc. " in locations[pub_hashes[k][0]]:
        pub_hashes[k] = [
            v
            for v in sorted(
                pub_hashes[k],
                key=lambda item: (
                    int(regex_numrange.search(locations[item])[1])
                    if regex_numrange.search(locations[item])
                    else -1
                ),
            )
        ]

        for i in range(len(pub_hashes[k]) - 1):
            hash1, hash2 = pub_hashes[k][i], pub_hashes[k][i + 1]
            str1, str2 = notes[hash1], notes[hash2]
            if (
                types[hash1] == "Bookmark"
                or types[hash2] == "Bookmark"
                or max(len(str1), len(str2)) < 52
            ):
                continue
            try:
                s1 = regex_numrange.search(locations[hash1])
                s2 = regex_numrange.search(locations[hash2])
                range1 = [int(s1.group(1)), int(s1.group(2))]
                range2 = [int(s2.group(1)), int(s2.group(2))]
            except (TypeError, AttributeError) as err:
                continue

            if (range1[0] in range2) or (range1[1] in range2):
                len_lcs = longest_common_substring_len(str1, str2)
                if len_lcs > 0.4 * max(len(str1), len(str2)):
                    print(
                        "Overlapping strings detected at loc.",
                        locations[hash1],
                        "/",
                        locations[hash2],
                    )
                    print(str1)
                    print()

    elif "p." in locations[pub_hashes[k][0]]:
        pub_hashes[k] = [
            v
            for v in sorted(
                pub_hashes[k],
                key=lambda item: (
                    int(regex_num.search(locations[item])[1])
                    if regex_num.search(locations[item])
                    else -1
                ),
            )
        ]

mc.close()

# Get user selection
selected_titles = get_user_book_selection(pub_title)

# Modify the main processing loop to only process selected books
for key in pub_title.keys():
    # Skip if this book wasn't selected
    if pub_title[key] not in selected_titles:
        continue

    nr_notes = len(pub_notes[key])
    author = pub_author[key]
    title = pub_title[key]
    short_title = title.split("|")[0]
    short_title = short_title.split(" - ")[0]
    short_title = short_title.split(". ")[0]
    if len(short_title) > 128:
        short_title = short_title[:127]
    if nr_notes > 2:
        fname = author + " - " + short_title.strip() + ".md"
        short = False
    else:
        fname = "short_notes.md"
        short = True

    new_hashes = 0
    for note_hash in pub_hashes[key]:
        if note_hash not in existing_hashes:
            new_hashes += 1

    if new_hashes > 0:
        print(new_hashes, "new notes found for", title)
    else:
        continue  # Skip to next title if there are no new hashes

    outfile = os.path.join(outpath, getvalidfilename(fname))

    newfile = os.path.isfile(outfile)

    out = open(outfile, "a", encoding="utf8")

    if short:
        # Short note, output a small header and append to short note file
        if author != "Unknown":
            titlestr = author + " - " + title
        else:
            titlestr = title
        out.write(titlestr + "\n")
        out.write(("-" * len(titlestr)) + "\n\n")
    elif not newfile:
        # Many notes, output with header and metadata in a separate file
        # Write metadata
        out.write("---" + "\n")
        out.write("created_date: " + datetime.now().strftime("%Y-%m-%d") + "\n")
        out.write("title: " + title + "\n")
        if author != "Unknown":
            out.write("authors: [" + author + "]" + "\n")
        out.write("tags:\n  - books" + "\n")
        out.write("---" + "\n")

        out.write("## Summary" + "\n")
        out.write("\n")
        out.write("## Highlights" + "\n")

    last_date = datetime.now()

    for note_hash in pub_hashes[key]:
        note = notes[note_hash]
        note_type = types[note_hash]
        note_date = dates[note_hash]
        note_loc = locations[note_hash]
        if note_hash in existing_hashes:
            print("Note", note_hash, "is already in", existing_hashes[note_hash])
        elif not note:
            print("Note", note_hash, f"is empty. Probably because it's a {note_type}.")
        else:
            print(
                "Adding new note to",
                outfile + ":",
                note_hash,
                note_type,
                note_loc,
                note_date,
            )

            comment = str(
                # commentstr
                # + note_hash
                # + " ; "
                # + note_type
                # +" ; " +
                note_loc
                + " ; "
                + note_date
            )

            if short:
                comment += " ; " + author + " ; " + title

            # this adds metadata before each note.
            out.write(comment + "\n")
            out.write(">" + note + "\n---\n\n")
        try:
            last_date = parse(note_date)
        except:
            pass

    out.close()

    # Update file modification time to time of last note

    if last_date.tzinfo is None or last_date.tzinfo.utcoffset(last_date) is None:
        epoch = datetime(1970, 1, 1)
    else:
        epoch = datetime(1970, 1, 1, tzinfo=timezone.utc)
    note_timestamp = (last_date - epoch) / timedelta(seconds=1)
    os.utime(outfile, (note_timestamp, note_timestamp))
