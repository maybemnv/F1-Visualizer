"""Tests for lap data loading."""

import pandas as pd

from f1_visualization import data_loader
from f1_visualization.data_loader import LapDataStore


class TestLapDataStore:
    """Tests for lazy lap data store behavior."""

    def test_data_load_is_deferred_until_first_access(self, monkeypatch):
        """Lap CSVs should not be loaded when the store is constructed."""
        calls = 0

        def fake_load_laps() -> dict[int, dict[str, pd.DataFrame]]:
            nonlocal calls
            calls += 1
            return {2024: {"R": pd.DataFrame({"Driver": ["VER"]})}}

        monkeypatch.setattr(data_loader, "load_laps", fake_load_laps)

        store = LapDataStore()

        assert calls == 0
        assert store[2024]["R"]["Driver"].iloc[0] == "VER"
        assert calls == 1
        assert list(store.keys()) == [2024]
        assert calls == 1

    def test_reload_clears_cached_data(self, monkeypatch):
        """Reload should force data to be loaded again on the next access."""
        calls = 0

        def fake_load_laps() -> dict[int, dict[str, pd.DataFrame]]:
            nonlocal calls
            calls += 1
            return {2024: {"R": pd.DataFrame({"Load": [calls]})}}

        monkeypatch.setattr(data_loader, "load_laps", fake_load_laps)

        store = LapDataStore()

        assert store[2024]["R"]["Load"].iloc[0] == 1
        store.reload()
        assert store[2024]["R"]["Load"].iloc[0] == 2


def test_load_laps_returns_empty_mapping_when_no_csvs(monkeypatch, tmp_path):
    """Missing transformed CSVs should produce an empty mapping instead of crashing."""
    monkeypatch.setattr(data_loader, "DATA_PATH", tmp_path)

    assert data_loader.load_laps() == {}
