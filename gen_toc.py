#!/usr/bin/env python

# Copyright 2018 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Generate a table of contents .ipynb.

It will also create a brief description based off the header file
from each notebook.

Usage:
    gen_toc $asl-dir-path"""

import os
import re
import sys

import nbformat as nbf

ASL_DIR = sys.argv[1]

def get_lab_dirs():
    """We want all days. Pull out only lab files"""
    def _is_a_lab(dirname):
        return dirname.endswith('_lab') or dirname.endswith('_soln') 
    directories = []
    for d in os.listdir(ASL_DIR):
        full_path = os.path.join(ASL_DIR, d)
        if os.path.isdir(full_path) and _is_a_lab(full_path):
            directories.append(full_path)
    return sorted(directories)

def _is_py_package(dirname, f):
    """We want to list python packages in table of contents."""
    path = os.path.join(dirname, f)
    is_dir = os.path.isdir(path)
    
    if is_dir:
        py_package = 'setup.py' in os.listdir(path)
        if py_package:
            return True
    return False

def get_relevant_files(dirname):
    """Given a directory, pull out Python and Python package name"""
    ipy_notebooks = []
    py_packages = []
    for fpath in os.listdir(dirname):
        ipy_file = fpath.endswith('.ipynb')
        if ipy_file:
            ipy_notebooks.append(fpath)
        elif _is_py_package(dirname, fpath):
            py_packages.append(fpath)
        
    return sorted(ipy_notebooks) + sorted(py_packages)

def _get_notebook_heading(fpath):
    """We want to get a short description for a given notebook in the TOC. 
    Read notebook, assume that the notebook title has html or # for markdown"""
    def striphtml(data):
        """https://stackoverflow.com/questions/3398852/using-python-remove-html-tags-formatting-from-a-string"""
        p = re.compile(r'<.*?>')
        return p.sub('', data)
    
    def stripmarkdown(data):
        return data.split('# ')[-1]
    
    def stripnumbers(data):
        return re.sub("^\d[a-z]?\.", " ", data)

    nb = nbf.read(fpath, nbf.NO_CONVERT)
    first_cell = striphtml(nb['cells'][0]['source'])
    first_line = first_cell.split('\n')[0].strip()
    first_line = stripnumbers(first_line)
    return stripmarkdown(first_line)

def _gen_markdown_bullet(item, url, heading_markdown='', desc=''):
    """Gen markdown for a bullet"""
    return '''{0} [{1}]({2}){3}\n
'''.format(heading_markdown, item, url, desc)

def gen_module_markdown(module, content):

    def _get_basename_and_parent(fpath):
        last2 = os.path.normpath(fpath).split(os.path.sep)[-2:]
        return os.path.join(*last2)

    header = '###' 
    module_name = os.path.basename(module)
    md = _gen_markdown_bullet(module_name, module_name, header)
    bullet = '* '
    for c in content:
        content_path = os.path.join(module, c)
        desc = ''
        if c.endswith('ipynb'):
            desc += ' - ' + _get_notebook_heading(content_path)
        path2 = _get_basename_and_parent(content_path)
        md += bullet + _gen_markdown_bullet(c, path2, desc=desc)
    return md


# create the markdown
all_modules = get_lab_dirs()
labs = [m for m in all_modules if m.endswith('lab')]
solns = [m for m in all_modules if m.endswith('soln') ]
lab_md = ''
for lab in labs:
    contents = get_relevant_files(lab)
    lab_md += gen_module_markdown(lab, contents)
    lab_md += '<br> \n'
print contents

soln_md = ''
for soln in solns:
    contents = get_relevant_files(soln)
    soln_md += '\n' + gen_module_markdown(soln, contents)

# write to .ipynb
nb = nbf.v4.new_notebook()
nb['cells'] = [nbf.v4.new_markdown_cell('## ASL Labs Table of Contents'),
               nbf.v4.new_markdown_cell(lab_md),
               nbf.v4.new_markdown_cell('## Solutions'),
               nbf.v4.new_markdown_cell(soln_md)]
nbf.write(nb, 'Table of Contents.ipynb')
