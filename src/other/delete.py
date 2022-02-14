"""
Deletes a bunch of frames to free up disk space.
https://stackoverflow.com/questions/1548704/delete-multiple-files-matching-a-pattern
"""

import os, re

dir = "../../screenshots/ingame"
dir = "FAKE DIRECTORY"
for f in os.listdir(dir):
    pattern = "frame_(.*).png"
    a = int(re.search(pattern, f).group(1))
    if a % 4 != 1:
        os.remove(os.path.join(dir, f))
    print(a)
