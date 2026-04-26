from conftest import EXPECTED_COLUMNS


def test_csv_has_expected_columns(csv_df) -> None:
    assert list(csv_df.columns) == EXPECTED_COLUMNS


def test_database_contains_expected_tables(db_connection) -> None:
    rows = db_connection.execute(
        "SELECT name FROM sqlite_master WHERE type='table'"
    ).fetchall()
    tables = {name for (name,) in rows}

    assert {"publishers", "magazines", "warehouses", "transactions"}.issubset(tables)


def test_transactions_count_matches_csv_rows(db_connection, csv_df) -> None:
    db_count = db_connection.execute("SELECT COUNT(*) FROM transactions").fetchone()[0]
    assert db_count == len(csv_df)


def test_publishers_count_matches_csv_unique_values(db_connection, csv_df) -> None:
    expected = (
        csv_df[["publisher_id", "publisher_name", "created_date"]]
        .drop_duplicates()
        .shape[0]
    )
    db_count = db_connection.execute("SELECT COUNT(*) FROM publishers").fetchone()[0]
    assert db_count == expected


def test_magazines_count_matches_csv_unique_values(db_connection, csv_df) -> None:
    expected = (
        csv_df[["magazine_id", "magazine_title", "magazine_category"]]
        .drop_duplicates()
        .shape[0]
    )
    db_count = db_connection.execute("SELECT COUNT(*) FROM magazines").fetchone()[0]
    assert db_count == expected


def test_warehouses_count_matches_non_empty_csv_values(db_connection, csv_df) -> None:
    non_empty = csv_df[csv_df["warehouses_id"].str.strip() != ""]
    expected = non_empty[["warehouses_id", "warehouses_info"]].drop_duplicates().shape[0]

    db_count = db_connection.execute("SELECT COUNT(*) FROM warehouses").fetchone()[0]
    assert db_count == expected


def test_transactions_amount_is_always_not_null(db_connection) -> None:
    null_count = db_connection.execute(
        "SELECT COUNT(*) FROM transactions WHERE amount IS NULL"
    ).fetchone()[0]
    assert null_count == 0
