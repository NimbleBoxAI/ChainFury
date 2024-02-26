# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import os
import sys

sys.path.insert(0, os.path.abspath(".."))

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = "ChainFury"
copyright = "2023, NimbleBox Engineering"
author = "NimbleBox Engineering"
release = "1.7.0a0"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
]

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

autodoc_default_options = {
    "special-members": "__call__",
}


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "sphinx_rtd_theme"
# html_theme_options = {
#     "rightsidebar": False,
#     "stickysidebar": False,
#     "collapsiblesidebar": False,
#     "externalrefs": False,
#     # "footerbgcolor": "#e6e6e6",
#     # "footertextcolor": "#333333",
#     # "sidebarbgcolor": "#ffffff",
#     # "sidebarbtncolor": "#333333",
#     # # "sidebartextercolor": "#333333",
#     # "sidebarlinkcolor": "#007aff",
#     # "relbarbgcolor": "#e6e6e6",
#     # # "relbartextercolor": "#333333",
#     # "relbarlinkcolor": "#007aff",
#     # "bgcolor": "#ffffff",
#     # # "textercolor": "#333333",
#     # "linkcolor": "#007aff",
#     # "visitedlinkcolor": "#cccccc",
#     # "headbgcolor": "#e6e6e6",
#     # # "headtextercolor": "#333333",
#     # "headlinkcolor": "#007aff",
#     # "codebgcolor": "#fafafa",
#     # # "codetextercolor": "#212121",
#     # "bodyfont": "Arial, sans-serif",
#     # "headfont": "Georgia, serif",
# }
html_static_path = ["_static"]
