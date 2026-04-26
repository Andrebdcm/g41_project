from classes.gclass import Gclass


def test_to_dict_returns_expected_mapping() -> None:
    model = Gclass(id=42)
    assert model.to_dict() == {"id": 42}
