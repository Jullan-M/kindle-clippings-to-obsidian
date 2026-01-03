# Kindle Clippings to Obsidian

![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg) ![Python 3.6+](https://img.shields.io/badge/python-3.6+-blue.svg) ![Obsidian](https://img.shields.io/badge/Obsidian-Compatible-purple.svg)

A Python script that extracts Kindle highlights and notes, formatting them beautifully for [Obsidian](https://obsidian.md/).

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Requirements](#requirements)
- [Installation](#installation)
- [Usage](#usage)
  - [Step-by-Step Guide](#step-by-step-guide)
  - [Example Output](#example-output)
- [Customizing the Output](#customizing-the-output)
- [How It Works](#how-it-works)
- [FAQ](#faq)
- [Related Obsidian Systems](#related-obsidian-systems)
- [Star History](#star-history)
- [License](#license)

## Overview

This script processes your Kindle’s My Clippings.txt file by:

- Extracting highlights (and any accompanying notes)
- Organizing them into separate text files—one per publication
- Formatting the output using Markdown, which makes it easy to copy/paste into Obsidian

## Features

- Creates separate Markdown files for each book
- Formats highlights with proper Obsidian syntax
- Preserves metadata (book title, author)
- Intelligently handles new highlights when run multiple times
- Allows selective processing of specific books
- Customizable output format

## Requirements

- **Python 3**
- **Unix-based terminal** (Linux, macOS, BSD, etc.)
- A Kindle with highlights saved in `My Clippings.txt`

## Installation

1. Clone this repository or download the script:

```bash
git clone https://github.com/dannberg/kindle-clippings-to-obsidian.git
```

2. Install Dependency:

```bash
pip install -r requirements.txt
```

3. Make the script executable:

```bash
chmod +x extract-kindle-clippings.py
```

## Usage

### Step-by-Step Guide

1. **Create highlights on your Kindle** as you read.

2. **Connect your Kindle to your computer** and locate the `My Clippings.txt` file in the `documents` folder.

3. **Run the script** with the following command:

```bash
./extract-kindle-clippings.py [<path to My Clippings.txt>] -o [<output directory>]
```

Example:

```bash
./extract-kindle-clippings.py /Users/USERNAME/Desktop/Temp/My\ Clippings.txt -o /Users/USERNAME/Desktop/Temp/clippings/
```

**Default values:**
- If no input file is specified, the script looks for `./My Clippings.txt` or `/media/$USER/Kindle/documents/My Clippings.txt`
- If no output directory is specified, files are created in a `clippings/` folder in the current directory

4. **Select which books to process** from the interactive menu:
   - Enter `0` to process all books
   - Enter a single number to process one specific book
   - Enter multiple numbers separated by spaces to process several books

5. **Import into Obsidian** by copying the content from the generated Markdown files.

## Customizing the Output

You can easily customize how your highlights appear in Obsidian by modifying the output format in the script:

1. Open `extract-kindle-clippings.py` in any text editor
2. Locate the section around lines 226-231 where the output formatting is defined
3. Edit the strings to match your preferred format
   - Use `\n` to create line breaks
   - Modify the metadata fields to match your Obsidian workflow

For example, you might want to add additional YAML frontmatter or change the heading structure.

## How It Works

The script works by:

1. **Reading** your Kindle's `My Clippings.txt` file
2. **Parsing** each highlight's metadata (book title, author, location, date)
3. **Generating** a unique hash for each highlight to avoid duplicates
4. **Checking** existing output files to see which highlights are new
5. **Creating** formatted Markdown files for each book with 3+ highlights
6. **Appending** highlights from books with fewer notes to a `short_notes.md` file

The script is smart enough to only add new highlights when run multiple times, so you can safely run it whenever you add new highlights to your Kindle.

## FAQ

**Q: What about Kindle Notes (not just highlights)?**  
A: The script captures both highlights and notes. Notes may require some additional manual formatting to make them look perfect in Obsidian. Feel free to open a PR if you get Notes working in a way you like!

**Q: Can I edit the output files?**  
A: Yes! You can rename, move, split, combine, and edit the output files. The script uses hash values to track which highlights have been processed.

**Q: Does this work with all Kindle models?**  
A: The script has been tested with first-generation Kindle Oasis, but should work with most Kindle models that generate a `My Clippings.txt` file.

**Q: Will this work on Windows?**  
A: This script was designed for Linux/Mac/BSD and may have issues on Windows.

## License

```
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
```
