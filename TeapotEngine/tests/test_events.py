"""
Tests for Event, Reaction, StackItem, and PendingInput classes
"""

import pytest
from datetime import datetime
from TeapotEngine.core.Events import Event, Reaction, StackItem, PendingInput, EventStatus, StackItemType
from TeapotEngine.ruleset.system_models.SystemEvent import PHASE_STARTED, PHASE_ENDED, ACTION_EXECUTED


class TestEvent:
    """Tests for Event class"""
    
    def test_create_event(self):
        """Test creating a basic event"""
        event = Event(
            type=PHASE_STARTED,
            payload={"phase_id": 1}
        )
        assert event.type == PHASE_STARTED
        assert event.payload == {"phase_id": 1}
        assert event.status == EventStatus.PENDING
        assert event.id == 0
        assert event.order == 0
    
    def test_event_with_id_and_order(self):
        """Test creating event with ID and order"""
        event = Event(
            id=5,
            type=ACTION_EXECUTED,
            payload={"action_id": 1},
            order=10
        )
        assert event.id == 5
        assert event.order == 10
    
    def test_event_to_dict(self):
        """Test event serialization"""
        event = Event(
            id=1,
            type=PHASE_STARTED,
            payload={"phase_id": 2},
            caused_by="player1",
            status=EventStatus.APPLIED,
            order=5
        )
        data = event.to_dict()
        assert data["id"] == 1
        assert data["type"] == PHASE_STARTED
        assert data["payload"] == {"phase_id": 2}
        assert data["caused_by"] == "player1"
        assert data["status"] == "applied"
        assert data["order"] == 5
        assert "timestamp" in data
    
    def test_event_from_dict(self):
        """Test event deserialization"""
        data = {
            "id": 2,
            "type": PHASE_ENDED,
            "payload": {"phase_id": 1},
            "caused_by": "player2",
            "status": "prevented",
            "timestamp": datetime.now().isoformat(),
            "order": 3
        }
        event = Event.from_dict(data)
        assert event.id == 2
        assert event.type == PHASE_ENDED
        assert event.payload == {"phase_id": 1}
        assert event.caused_by == "player2"
        assert event.status == EventStatus.PREVENTED
        assert event.order == 3


class TestReaction:
    """Tests for Reaction class"""
    
    def test_create_reaction(self):
        """Test creating a basic reaction"""
        reaction = Reaction(
            when={"eventType": "PhaseEntered"},
            effects=[1, 2],
            timing="post"
        )
        assert reaction.when == {"eventType": "PhaseEntered"}
        assert reaction.effects == [1, 2]
        assert reaction.timing == "post"
        assert reaction.condition is None
        assert reaction.id > 0  # Auto-generated
    
    def test_reaction_with_caused_by(self):
        """Test reaction with caused_by"""
        reaction = Reaction(
            when={"eventType": "CardMoved"},
            effects=[3],
            caused_by={"object_type": "component", "object_id": "123"}
        )
        assert reaction.caused_by == {"object_type": "component", "object_id": "123"}
    
    def test_reaction_to_dict(self):
        """Test reaction serialization"""
        reaction = Reaction(
            id=10,
            when={"eventType": "ActionExecuted"},
            condition={"op": "check"},
            effects=[1, 2, 3],
            timing="pre",
            caused_by={"object_type": "player", "object_id": "player1"}
        )
        data = reaction.to_dict()
        assert data["id"] == 10
        assert data["when"] == {"eventType": "ActionExecuted"}
        assert data["condition"] == {"op": "check"}
        assert data["effects"] == [1, 2, 3]
        assert data["timing"] == "pre"
        assert data["caused_by"] == {"object_type": "player", "object_id": "player1"}
    
    def test_reaction_from_dict(self):
        """Test reaction deserialization"""
        data = {
            "id": 20,
            "when": {"eventType": "TurnEnded"},
            "condition": None,
            "effects": [5],
            "timing": "post",
            "caused_by": {"object_type": "component", "object_id": "456"}
        }
        reaction = Reaction.from_dict(data)
        assert reaction.id == 20
        assert reaction.when == {"eventType": "TurnEnded"}
        assert reaction.condition is None
        assert reaction.effects == [5]
        assert reaction.timing == "post"
        assert reaction.caused_by == {"object_type": "component", "object_id": "456"}


class TestStackItem:
    """Tests for StackItem class"""
    
    def test_create_stack_item_event(self):
        """Test creating a stack item for an event"""
        item = StackItem(
            kind=StackItemType.EVENT,
            ref_id=1,
            created_at_order=5
        )
        assert item.kind == StackItemType.EVENT
        assert item.ref_id == 1
        assert item.created_at_order == 5
        assert item.flags == {}
    
    def test_create_stack_item_reaction(self):
        """Test creating a stack item for a reaction"""
        item = StackItem(
            kind=StackItemType.REACTION,
            ref_id=2,
            created_at_order=10,
            flags={"priority": 1}
        )
        assert item.kind == StackItemType.REACTION
        assert item.ref_id == 2
        assert item.created_at_order == 10
        assert item.flags == {"priority": 1}
    
    def test_stack_item_to_dict(self):
        """Test stack item serialization"""
        item = StackItem(
            kind=StackItemType.EVENT,
            ref_id=3,
            created_at_order=15,
            flags={"test": True}
        )
        data = item.to_dict()
        assert data["kind"] == "event"
        assert data["ref_id"] == 3
        assert data["created_at_order"] == 15
        assert data["flags"] == {"test": True}
    
    def test_stack_item_from_dict(self):
        """Test stack item deserialization"""
        data = {
            "kind": "reaction",
            "ref_id": 4,
            "created_at_order": 20,
            "flags": {"priority": 2}
        }
        item = StackItem.from_dict(data)
        assert item.kind == StackItemType.REACTION
        assert item.ref_id == 4
        assert item.created_at_order == 20
        assert item.flags == {"priority": 2}


class TestPendingInput:
    """Tests for PendingInput class"""
    
    def test_create_pending_input(self):
        """Test creating a basic pending input"""
        input_obj = PendingInput(
            for_player_ids=["player1"],
            kind="target_select",
            constraints={"max_targets": 1}
        )
        assert input_obj.for_player_ids == ["player1"]
        assert input_obj.kind == "target_select"
        assert input_obj.constraints == {"max_targets": 1}
        assert input_obj.input_id is not None
        assert input_obj.expires_at is None
    
    def test_pending_input_with_expiry(self):
        """Test pending input with expiration"""
        expiry = datetime.now()
        input_obj = PendingInput(
            for_player_ids=["player1", "player2"],
            kind="confirm",
            constraints={},
            expires_at=expiry
        )
        assert input_obj.expires_at == expiry
        assert len(input_obj.for_player_ids) == 2
    
    def test_pending_input_to_dict(self):
        """Test pending input serialization"""
        expiry = datetime.now()
        input_obj = PendingInput(
            input_id="test-input-123",
            for_player_ids=["player1"],
            kind="mode_pick",
            constraints={"options": ["option1", "option2"]},
            expires_at=expiry
        )
        data = input_obj.to_dict()
        assert data["input_id"] == "test-input-123"
        assert data["for_player_ids"] == ["player1"]
        assert data["kind"] == "mode_pick"
        assert data["constraints"] == {"options": ["option1", "option2"]}
        assert data["expires_at"] == expiry.isoformat()
    
    def test_pending_input_from_dict(self):
        """Test pending input deserialization"""
        expiry = datetime.now()
        data = {
            "input_id": "test-input-456",
            "for_player_ids": ["player2"],
            "kind": "pay_cost",
            "constraints": {"cost": 5},
            "expires_at": expiry.isoformat()
        }
        input_obj = PendingInput.from_dict(data)
        assert input_obj.input_id == "test-input-456"
        assert input_obj.for_player_ids == ["player2"]
        assert input_obj.kind == "pay_cost"
        assert input_obj.constraints == {"cost": 5}
        assert input_obj.expires_at is not None

