from classes.gclass import Gclass


def test_to_dict_returns_expected_mapping() -> None:
    """`to_dict` should return the dataclass fields as a dictionary."""
    model = Gclass(id=42)
    assert model.to_dict() == {"id": 42}
