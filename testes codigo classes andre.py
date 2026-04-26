from datetime import datetime

from classes.magazine import Magazine
from classes.publisher import Publisher
from classes.transaction import Transaction
from classes.warehouse import Warehouse


def test_publisher_from_row_parses_valid_fields() -> None:
    row = {
        "publisher_id": "235",
        "publisher_name": " Hawkins Ltd ",
        "created_date": "2022/01/15",
    }

    model = Publisher.from_row(row)

    assert model.id == "235"
    assert model.publisher_id == 235
    assert model.publisher_name == "Hawkins Ltd"
    assert model.created_date == datetime(2022, 1, 15)

    print(f"  id             = {model.id!r}")
    print(f"  publisher_id   = {model.publisher_id!r}")
    print(f"  publisher_name = {model.publisher_name!r}")
    print(f"  created_date   = {model.created_date!r}")


def test_publisher_from_row_handles_invalid_date() -> None:
    row = {
        "publisher_id": "10",
        "publisher_name": "Sample",
        "created_date": "invalid-date",
    }

    model = Publisher.from_row(row)

    assert model.publisher_id == 10
    assert model.created_date is None

    print(f"  publisher_id = {model.publisher_id!r}")
    print(f"  created_date = {model.created_date!r}  (invalid date → None)")


def test_magazine_from_row_trims_text() -> None:
    row = {
        "magazine_id": "733",
        "magazine_title": " Nexus AI Mensal ",
        "magazine_category": " Tecnologia ",
    }

    model = Magazine.from_row(row)

    assert model.id == "733"
    assert model.magazine_id == 733
    assert model.magazine_title == "Nexus AI Mensal"
    assert model.magazine_category == "Tecnologia"

    print(f"  id               = {model.id!r}")
    print(f"  magazine_id      = {model.magazine_id!r}")
    print(f"  magazine_title   = {model.magazine_title!r}")
    print(f"  magazine_category= {model.magazine_category!r}")


def test_warehouse_from_row_parses_valid_id() -> None:
    row = {
        "warehouses_id": "128",
        "warehouses_info": "Porto Alegre - Setor de Carga, Lote 607A",
    }

    model = Warehouse.from_row(row)

    assert model.id == 128
    assert model.warehouses_id == 128
    assert model.warehouses_info == "Porto Alegre - Setor de Carga, Lote 607A"

    print(f"  id              = {model.id!r}")
    print(f"  warehouses_id   = {model.warehouses_id!r}")
    print(f"  warehouses_info = {model.warehouses_info!r}")


def test_warehouse_from_row_treats_empty_zero_and_invalid_as_none() -> None:
    for value in ("", "0", None, "not-an-int"):
        row = {"warehouses_id": value, "warehouses_info": "No Warehouse"}
        model = Warehouse.from_row(row)
        assert model.warehouses_id is None
        assert model.id is None
        print(f"  warehouses_id={value!r:12} → id={model.id!r}, warehouses_id={model.warehouses_id!r}")


def test_transaction_from_row_parses_valid_values() -> None:
    row = {
        "transaction_date": "2022/05/09",
        "amount": "483",
        "publisher_id": "235",
        "magazine_id": "733",
    }

    model = Transaction.from_row(row)

    assert model.transaction_date == datetime(2022, 5, 9)
    assert model.amount == 483.0
    assert model.publisher_id == 235
    assert model.magazine_id == 733

    print(f"  transaction_date = {model.transaction_date!r}")
    print(f"  amount           = {model.amount!r}")
    print(f"  publisher_id     = {model.publisher_id!r}")
    print(f"  magazine_id      = {model.magazine_id!r}")


def test_transaction_from_row_handles_invalid_date_and_amount() -> None:
    row = {
        "transaction_date": "invalid-date",
        "amount": "invalid-amount",
        "publisher_id": "",
        "magazine_id": "",
    }

    model = Transaction.from_row(row)

    assert model.transaction_date is None
    assert model.amount == 0.0
    assert model.publisher_id is None
    assert model.magazine_id is None

    print(f"  transaction_date = {model.transaction_date!r}  (invalid → None)")
    print(f"  amount           = {model.amount!r}  (invalid → 0.0)")
    print(f"  publisher_id     = {model.publisher_id!r}  (empty string → None)")
    print(f"  magazine_id      = {model.magazine_id!r}  (empty string → None)")


# ── runner ────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    tests = [
        test_publisher_from_row_parses_valid_fields,
        test_publisher_from_row_handles_invalid_date,
        test_magazine_from_row_trims_text,
        test_warehouse_from_row_parses_valid_id,
        test_warehouse_from_row_treats_empty_zero_and_invalid_as_none,
        test_transaction_from_row_parses_valid_values,
        test_transaction_from_row_handles_invalid_date_and_amount,
    ]

    passed = 0
    failed = 0
    for t in tests:
        print(f"\n{'─' * 55}")
        print(f"RUNNING  {t.__name__}")
        try:
            t()
            print(f"PASS ✓")
            passed += 1
        except AssertionError as e:
            print(f"FAIL ✗  {e}")
            failed += 1

    print(f"\n{'═' * 55}")
    print(f"Results: {passed} passed, {failed} failed out of {len(tests)} tests")
