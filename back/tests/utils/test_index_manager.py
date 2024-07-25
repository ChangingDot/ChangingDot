from utils.index_manager import IndexManager


def test_basic_index_manager() -> None:
    index_manager = IndexManager()
    assert index_manager.get_updated_index(5) == 5


def test_add_index_manager() -> None:
    index_manager = IndexManager()
    index_manager.add_from_index(3)
    assert index_manager.get_updated_index(2) == 2
    assert index_manager.get_updated_index(3) == 4
    assert index_manager.get_updated_index(10) == 11


def test_remove_index_manager() -> None:
    index_manager = IndexManager()
    index_manager.remove_from_index(3)
    assert index_manager.get_updated_index(2) == 2
    # decided to return -1 rather than raise exception
    assert index_manager.get_updated_index(3) == -1
    assert index_manager.get_updated_index(10) == 9

    # with pytest.raises(IndexWasRemovedError):
    #     assert index_manager.get_updated_index(3)
