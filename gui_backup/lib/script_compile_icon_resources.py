# -*- coding: utf-8 -*-
"""
@author: Raymond F. Pauszek III, Ph.D. (2020)
helper script: auto-generate icons .qrc in parent directory
               adds all png files in ./icons
to compile in shell, from ./smtirf/gui/ run command
    pyrcc5 resources.qrc -o ../resources.py
"""
from pathlib import Path
import subprocess

iconsDir = Path(r'./icons').absolute()
qrcFile = Path("./resources.qrc").absolute()
pyResourceFile = qrcFile.parent.parent / "resources.py"

# write .qrc file
with open(qrcFile, 'w') as F:
    F.write('<!DOCTYPE RCC><RCC version="1.0">\n<qresource>\n')
    for icon in iconsDir.glob("*.png"):
        F.write(f'\t<file>icons/{icon.stem}.png</file>\n')
    F.write("</qresource>\n</RCC>")

# TODO ==> compile .qrc -> .py resources, subprocess.run()?
