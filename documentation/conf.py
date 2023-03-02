# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'How to build and public a Sphinx documentation on GitHub Pages using Drone CI'
copyright = '2023, BibLibre'
author = 'BibLibre'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = []

templates_path = ['_templates']
exclude_patterns = ['_build', '.venv']

language = 'en'

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'sphinx_book_theme'
html_theme_options = {
    "path_to_docs": "documentation",
    "repository_url": "https://github.com/biblibre/sphinx-to-github-pages-with-drone",
    "repository_branch": "master",
    "use_issues_button": False,
    "use_download_button": False,
    "use_source_button": True,
    "use_repository_button": True,
    "use_edit_page_button": True,
}
html_title = "Publish Sphinx documentation to GitHub Pages with Drone"
html_static_path = ['_static']
