import os
import subprocess
import tempfile
from collections import defaultdict

from astropy.utils.console import color_print

REPOSITORY = 'git://github.com/astropy/astropy.git'
NAME = os.path.basename(REPOSITORY).replace('.git', '')

TMPDIR = tempfile.mkdtemp()
STARTDIR = os.path.abspath('.')

# The branches we are interested in
BRANCHES = ['v0.1.x', 'v0.2.x', 'v0.3.x', 'v0.4.x', 'v1.0.x', 'v1.1.x', 'v1.2.x']

# Read in a list of all the PRs
import json
with open('merged_pull_requests.json') as merged:
    merged_prs = json.load(merged)

# Set up a dictionary where each key will be a PR and each value will be a list
# of branches in which the PR is present
pr_branches = defaultdict(list)

try:

    # Set up repository
    color_print('Cloning {0}'.format(REPOSITORY), 'green')
    os.chdir(TMPDIR)
    subprocess.call('git clone {0}'.format(REPOSITORY), shell=True)
    os.chdir(NAME)

    # Loop over branches and find all PRs in the branch
    for branch in BRANCHES:

        # Change branch
        color_print('Switching to branch {0}'.format(branch), 'green')
        subprocess.call('git reset --hard', shell=True)
        subprocess.call('git clean -fxd', shell=True)
        subprocess.call('git checkout {0}'.format(branch), shell=True)

        # Extract entire log
        log = subprocess.check_output('git log --first-parent', shell=True).decode('utf-8')

        # Check for the presence of the PR in the log
        for pr in merged_prs:
            count = log.count("Merge pull request #{0} ".format(pr))
            if count == 0:
                pass  # not in branch
            else:
                pr_branches[pr].append(branch)
                if count > 1:
                    color_print("Pull request {0} appears {1} times in branch {2}".format(pr, count, branch), 'red')

finally:
    os.chdir(STARTDIR)

with open('pull_requests_branches.json', 'w') as f:
    json.dump(pr_branches, f, sort_keys=True, indent=2)
