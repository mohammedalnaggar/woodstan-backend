"""Tests for the assign_unit_id function and part ID format."""

import pytest

from engine.models.room import RoomContext
from engine.generators.base import assign_unit_id


class TestAssignUnitId:
    def test_empty_room_returns_cab_001(self):
        room = RoomContext()
        assert assign_unit_id(room) == "CAB-001"

    def test_sequential_after_existing(self):
        room = RoomContext(existing_unit_ids=("CAB-001", "CAB-002"))
        assert assign_unit_id(room) == "CAB-003"

    def test_gaps_in_sequence_uses_max(self):
        """Non-contiguous IDs: next is max+1, not first gap."""
        room = RoomContext(existing_unit_ids=("CAB-001", "CAB-005"))
        assert assign_unit_id(room) == "CAB-006"

    def test_non_cab_ids_are_ignored(self):
        """Unknown ID formats do not count toward the sequence."""
        room = RoomContext(existing_unit_ids=("UNIT-001", "CAB-003"))
        assert assign_unit_id(room) == "CAB-004"

    def test_zero_padded_to_three_digits(self):
        room = RoomContext(existing_unit_ids=tuple(f"CAB-{i:03d}" for i in range(1, 10)))
        result = assign_unit_id(room)
        assert result == "CAB-010"

    def test_id_format_prefix(self):
        room = RoomContext()
        result = assign_unit_id(room)
        assert result.startswith("CAB-")

    def test_large_sequence_number(self):
        room = RoomContext(existing_unit_ids=(f"CAB-{999:03d}",))
        assert assign_unit_id(room) == "CAB-1000"
