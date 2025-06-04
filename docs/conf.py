import sys
from pathlib import Path

# -- Project information -----------------------------------------------------
project = "python-rabbitx"
copyright = "2025, RabbitX"
author = "RabbitX Team"
version = release = "1.0.0"

# -- General configuration ---------------------------------------------------
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    # 'sphinx.ext.autosummary',
    # 'sphinx.ext.intersphinx',
    "sphinx.ext.viewcode",
    "sphinx.ext.extlinks",
    # 'sphinx_autodoc_typehints',
    "sphinx_copybutton",
]

autodoc_typehints = "description"
add_module_names = True
autosummary_generate = True
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]
language = "en"
master_doc = "index"
pygments_style = "sphinx"
source_suffix = ".rst"
templates_path = ["_templates"]

# -- Options for HTML output -------------------------------------------------
html_theme = "sphinx_rtd_theme"
html_static_path = ["_static"]

# -- Intersphinx mapping -----------------------------------------------------
intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
}

# -- Path setup --------------------------------------------------------------
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

extlinks = {
    "ghfile": ("https://github.com/timsolov/python-rabbitx/blob/main/%s", "%s"),
}
