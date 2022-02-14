"""
Deletes a bunch of frames to free up disk space.
https://stackoverflow.com/questions/1548704/delete-multiple-files-matching-a-pattern
"""

import os
import re

# root_dir = "../../screenshots/ingame"
root_dir = "FAKE DIRECTORY"
for f in os.listdir(root_dir):
    pattern = "frame_(.*).png"
    a = int(re.search(pattern, f).group(1))
    if a % 4 != 1:
        os.remove(os.path.join(root_dir, f))
    print(a)
