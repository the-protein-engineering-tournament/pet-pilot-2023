from pathlib import Path

import pandas as pd

files = ("test.csv", "test (with values).csv")

for data_dir in (Path("in_silico_supervised") / "input").glob("*"):
    expected_columns = set(pd.read_csv(data_dir / "train.csv").columns)
    for f in files:
        df = pd.read_csv(data_dir / f)
        assert set(df.columns) == expected_columns, Path(d) / data_dir / f
