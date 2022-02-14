"""
Compresses all frames with loseless compression to free up disk space.
https://stackoverflow.com/questions/54570614/how-can-i-reduce-the-file-size-of-a-png-image-without-changing-its-dimensions
https://stackoverflow.com/questions/35176639/compare-images-python-pil
https://stackoverflow.com/questions/19587118/iterating-through-directories-with-python
https://stackoverflow.com/questions/273192/how-can-i-safely-create-a-nested-directory
"""

import os
from PIL import Image
from pathlib import Path

total_uncompressed = 0
total_compressed = 0


# Compress PNG file named "filename" using Pillow's image compression
def compress_png(file1, file2):
    size1 = os.path.getsize(file1)
    img = Image.open(file1)
    img.save(file2, optimize=True)
    size2 = os.path.getsize(file2)
    return size1, size2


# Directory containing screenshots to compress
# rootdir = "../../../screenshots"
rootdir = "FAKE DIRECTORY"
for subdir, dirs, files in os.walk(rootdir):
    for file in files:
        file1 = os.path.join(subdir, file)
        new_subdir = subdir.replace("screenshots", "new_screenshots")
        Path(new_subdir).mkdir(parents=True, exist_ok=True)
        file2 = os.path.join(subdir, file).replace("screenshots", "new_screenshots")
        size1, size2 = compress_png(file1, file2)
        total_uncompressed += size1
        total_compressed += size2
        print(f"[{size2 / size1 * 100:.2f}%] {file1} -> {file2}")

print(f"Total compression ratio: {total_compressed / total_uncompressed * 100:.2f}%")

'''
# Check if the images are still the same
image_one = Image.open(file1)
image_two = Image.open(file2)

diff = ImageChops.difference(image_one, image_two)

if diff.getbbox():
    print("Images are different")
else:
    print("Images are the same")
'''
