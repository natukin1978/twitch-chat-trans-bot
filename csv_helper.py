import csv
import os
from typing import Any, List

import global_value as g


def read_csv_to_list(name: str) -> List[List[Any]]:
    if not os.path.isabs(name):
        name = os.path.join(g.base_dir, name)
    if not os.path.isfile(name):
        return {}
    with open(name, encoding="utf-8") as f:
        reader = csv.reader(f)
        return [row for row in reader]
