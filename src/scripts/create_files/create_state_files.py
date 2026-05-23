
from pathlib import Path

import json
import pandas as pd

from src.scripts.import_files import import_location_data

FILE_PATH: str = "data/raw/microdados_saeb_2023/DADOS/TS_ESCOLA.csv"
INPUT_FILE_PATH: str = "data/process/location.json"
OUTPUT_FILE_PATH: str = "data/process/states"

