__version__ = "0.1.0"
import pathlib

ROOT_DIR = pathlib.Path(__file__).parent.parent.parent.absolute()
DATA_DIR = ROOT_DIR / "data"
OUTPUT_DIR = ROOT_DIR / "output"
