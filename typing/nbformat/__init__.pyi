from pathlib import Path
from nbformat.notebooknode import NotebookNode as NotebookNode

# Upstream notebook read/write APIs have no annotations. These declarations
# describe the actual public APIs used by this module's notebook runner.
def read(fp: Path, as_version: int) -> NotebookNode: ...
def write(nb: NotebookNode, fp: Path) -> None: ...
