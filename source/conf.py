import os
import sys
from sphinx.ext import autodoc, napoleon

sys.path.insert(0, os.path.abspath('..'))

project = 'PURPLE Documentation'
html_title = "Purple"
copyright = '2024, Francesco Santarelli'
author = 'Francesco Santarelli'
release = '1'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = ['sphinx.ext.autodoc', 'sphinx.ext.napoleon', 'sphinx_autodoc_typehints']

templates_path = ['_templates']
exclude_patterns = []

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'sphinx_material'
html_static_path = ['_static']

html_theme_options = {
    'nav_title': 'PURPLE Docs',
    'color_primary': 'purple',
    'color_accent': 'deep-purple',
    'repo_url': 'https://github.com/Sokoodo/PurpleBackEnd',
    'repo_name': 'GitHub',
}
