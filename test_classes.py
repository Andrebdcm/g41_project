"""Simple tests for the data classes.

This script demonstrates instantiation of the domain classes using the
first row of the CSV. It is a lightweight smoke-test; use `pytest` or
more elaborate assertions for production tests.
"""

import pandas as pd
import sys
from pathlib import Path

# Resolve paths relative to this file so the script works from any CWD.
PROJECT_ROOT = Path(__file__).resolve().parent
CSV_PATH = PROJECT_ROOT.parent / 'g41_Publishers_Magazines_v2.csv'

# Ensure project classes are importable when running from any location.
sys.path.insert(0, str(PROJECT_ROOT))

from classes.publisher import Publisher
from classes.magazine import Magazine
from classes.warehouse import Warehouse
from classes.transaction import Transaction


def main():
    # Use latin-1 encoding because the CSV contains accented characters.
    df = pd.read_csv(CSV_PATH, sep=';', dtype=str, encoding='latin-1').fillna('')
    # Pick the first row and build entities.
    row = df.iloc[0].to_dict()
    pub = Publisher.from_row(row)
    mag = Magazine.from_row(row)
    wh = Warehouse.from_row(row)
    tx = Transaction.from_row(row)

    print('Publisher:', pub)
    print('Magazine:', mag)
    print('Warehouse:', wh)
    print('Transaction:', tx)


if __name__ == '__main__':
    main()
