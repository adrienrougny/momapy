# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = "MomaPy"
copyright = "2024, Adrien Rougny"
author = "Adrien Rougny"
release = "0.1"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "autoapi.extension",
]

autodoc_typehints = "description"

autoapi_dirs = ["../src/momapy"]
autoapi_type = "python"
autoapi_options = [
    "undoc-members",
    "members",
    "show-inheritance",
    "show-module-summary",
    "imported-members",
    "inherited-members",
]
autoclass_content = "both"

templates_path = ["_templates"]
exclude_patterns = []


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "furo"
html_static_path = ["_static"]
