import re
import os
import json
import zipfile
import tempfile
import subprocess

import requests

CHANGELOG = 'https://raw.githubusercontent.com/astropy/astropy/master/CHANGES.rst'
TMPDIR = tempfile.mkdtemp()

BLOCK_PATTERN = re.compile('\[#.+\]', flags=re.DOTALL)
ISSUE_PATTERN = re.compile('#[0-9]+')


def find_prs_in_changelog(content):
    issue_numbers = []
    for block in BLOCK_PATTERN.finditer(content):
        block_start, block_end = block.start(), block.end()
        block = content[block_start:block_end]
        for m in ISSUE_PATTERN.finditer(block):
            start, end = m.start(), m.end()
            issue_numbers.append(block[start:end][1:])
    return issue_numbers

# Get all the PR numbers from the changelog

changelog_prs = {}
version = None
content = ''
previous = None

for line in requests.get(CHANGELOG).text.splitlines():
    if '-------' in line:
        if version is not None:
            for pr in find_prs_in_changelog(content):
                changelog_prs[pr] = version
        version = previous.strip().split('(')[0].strip()
        if not 'v' in version:
            version = 'v' + version
        content = ''
    elif version is not None:
        content += line
    previous = line

with open('pull_requests_changelog_sections.json', 'w') as f:
    json.dump(changelog_prs, f, sort_keys=True, indent=2)
