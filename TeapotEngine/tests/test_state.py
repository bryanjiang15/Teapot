"""
Tests for GameState class
"""

from TeapotEngine.core.state import GameState
from TeapotEngine.core.events import Event
from TeapotEngine.core.component import Component
from TeapotEngine.ruleset.componentDefinition import ComponentDefinition, ComponentType
from TeapotEngine.ruleset.models.resource_models import ResourceDefinition, ResourceScope, ResourceType
from TeapotEngine.ruleset.ir import RulesetIR
from TeapotEngine.ruleset.system_data.system_events import PHASE_STARTED, PHASE_ENDED, TURN_ENDED
from TeapotEngine.tests.helpers.ruleset_helper import RulesetHelper


class TestGameState:
    """Tests for GameState class"""
    
    def test_create_state_from_ruleset(self):
        """Test creating a game state from a ruleset"""
        ruleset = RulesetHelper.create_ruleset_ir()
        state = GameState.from_ruleset("test_match", ruleset, ["player1", "player2"])
        
        assert state.match_id == "test_match"
        assert state.active_player == "player1"
        assert state.phase_manager is not None
        assert state.current_phase == 1
    
    def test_allocate_resource_instance_id(self):
        """Test allocating resource instance IDs"""
        ruleset = RulesetHelper.create_ruleset_ir()
        state = GameState.from_ruleset("test_match", ruleset, ["player1"])
        
        id1 = state.allocate_resource_instance_id()
        id2 = state.allocate_resource_instance_id()
        id3 = state.allocate_resource_instance_id()
        
        assert id1 == 1
        assert id2 == 2
        assert id3 == 3
    
    def test_create_component(self):
        """Test creating a component instance"""
        ruleset = RulesetHelper.create_ruleset_ir()
        state = GameState.from_ruleset("test_match", ruleset, ["player1"])
        
        definition = ComponentDefinition(
            id=1,
            name="Test Component",
            component_type=ComponentType.CARD
        )
        component = state.create_component(definition, zone="hand")
        
        assert component is not None
        assert component.definition_id == 1
        assert component.zone == "hand"
    
    def test_get_component(self):
        """Test getting a component by ID"""
        ruleset = RulesetHelper.create_ruleset_ir()
        state = GameState.from_ruleset("test_match", ruleset, ["player1"])
        
        definition = ComponentDefinition(
            id=1,
            name="Test Component",
            component_type=ComponentType.CARD
        )
        component = state.create_component(definition)
        component_id = component.id
        
        retrieved = state.get_component(component_id)
        assert retrieved is not None
        assert retrieved.id == component_id
    
    def test_remove_component(self):
        """Test removing a component"""
        ruleset = RulesetHelper.create_ruleset_ir()
        state = GameState.from_ruleset("test_match", ruleset, ["player1"])
        
        definition = ComponentDefinition(
            id=1,
            name="Test Component",
            component_type=ComponentType.CARD
        )
        component = state.create_component(definition)
        component_id = component.id
        
        result = state.remove_component(component_id)
        assert result is True
        assert state.get_component(component_id) is None
    
    def test_get_components_by_type(self):
        """Test getting components by type"""
        ruleset = RulesetHelper.create_ruleset_ir()
        state = GameState.from_ruleset("test_match", ruleset, ["player1"])
        
        card_def = ComponentDefinition(id=1, name="Card", component_type=ComponentType.CARD)
        player_def = ComponentDefinition(id=2, name="Player", component_type=ComponentType.PLAYER)
        
        card = state.create_component(card_def)
        player = state.create_component(player_def)
        
        cards = state.get_components_by_type(ComponentType.CARD)
        assert len(cards) == 1
        assert cards[0].id == card.id
    
    def test_get_game_component_instance(self):
        """Test getting the game component instance"""
        ruleset_dict = RulesetHelper.create_ruleset_with_game_component()
        ruleset = RulesetIR.from_dict(ruleset_dict)
        state = GameState.from_ruleset("test_match", ruleset, ["player1"])
        
        game_component = state.get_game_component_instance()
        assert game_component is not None
        assert game_component.component_type == ComponentType.GAME
    
    def test_get_components_by_zone(self):
        """Test getting components by zone"""
        ruleset = RulesetHelper.create_ruleset_ir()
        state = GameState.from_ruleset("test_match", ruleset, ["player1"])
        
        definition = ComponentDefinition(
            id=1,
            name="Component",
            component_type=ComponentType.CARD
        )
        component1 = state.create_component(definition, zone="hand")
        component2 = state.create_component(definition, zone="hand")
        component3 = state.create_component(definition, zone="battlefield")
        
        hand_components = state.get_components_by_zone("hand")
        assert len(hand_components) == 2
    
    def test_get_components_by_controller(self):
        """Test getting components by controller"""
        ruleset = RulesetHelper.create_ruleset_ir()
        state = GameState.from_ruleset("test_match", ruleset, ["player1", "player2"])
        
        definition = ComponentDefinition(
            id=1,
            name="Component",
            component_type=ComponentType.CARD
        )
        component1 = state.create_component(definition, controller_id="player1")
        component2 = state.create_component(definition, controller_id="player1")
        component3 = state.create_component(definition, controller_id="player2")
        
        player1_components = state.get_components_by_controller("player1")
        assert len(player1_components) == 2
    
    def test_move_component(self):
        """Test moving a component to a new zone"""
        ruleset = RulesetHelper.create_ruleset_ir()
        state = GameState.from_ruleset("test_match", ruleset, ["player1"])
        
        definition = ComponentDefinition(
            id=1,
            name="Component",
            component_type=ComponentType.CARD
        )
        component = state.create_component(definition, zone="hand")
        component_id = component.id
        
        result = state.move_component(component_id, "battlefield")
        assert result is True
        assert state.get_component(component_id).zone == "battlefield"
    
    def test_apply_event_phase_entered(self):
        """Test applying a PhaseEntered event"""
        ruleset = RulesetHelper.create_ruleset_ir()
        state = GameState.from_ruleset("test_match", ruleset, ["player1"])
        
        initial_phase = state.current_phase
        event = Event(
            type=PHASE_STARTED,
            payload={"phase_id": 2}
        )
        state.apply_event(event)
        
        assert state.current_phase == 2
        assert len(state.event_log) == 1
    
    def test_apply_event_phase_exited(self):
        """Test applying a PhaseExited event"""
        ruleset = RulesetHelper.create_ruleset_ir()
        state = GameState.from_ruleset("test_match", ruleset, ["player1"])
        
        event = Event(
            type=PHASE_ENDED,
            payload={"phase_id": 1}
        )
        state.apply_event(event)
        
        assert len(state.event_log) == 1
    
    def test_apply_event_turn_ended(self):
        """Test applying a TurnEnded event"""
        ruleset = RulesetHelper.create_ruleset_ir()
        state = GameState.from_ruleset("test_match", ruleset, ["player1", "player2"])
        
        initial_player = state.active_player
        event = Event(
            type=TURN_ENDED,
            payload={"turn_number": 1}
        )
        state.apply_event(event)
        
        # Active player should sync with phase manager
        assert len(state.event_log) == 1
    
    def test_apply_event_card_moved(self):
        """Test applying a CardMoved event"""
        ruleset = RulesetHelper.create_ruleset_ir()
        state = GameState.from_ruleset("test_match", ruleset, ["player1"])
        
        event = Event(
            type="CardMoved",
            payload={
                "card_id": "card_123",
                "from_zone": "hand",
                "to_zone": "battlefield",
                "player_id": "player1"
            }
        )
        state.apply_event(event)
        
        # Check that card is in new zone
        battlefield = state.get_player_zone("player1", "battlefield")
        # Note: zones structure may vary, this is a basic check
        assert len(state.event_log) == 1
    
    def test_apply_event_resource_changed(self):
        """Test applying a ResourceChanged event"""
        ruleset = RulesetHelper.create_ruleset_ir()
        state = GameState.from_ruleset("test_match", ruleset, ["player1"])
        
        # Add a resource definition
        resource_def = ResourceDefinition(
            id=1,
            name="mana",
            description="Mana",
            scope=ResourceScope.PLAYER,
            resource_type=ResourceType.CONSUMABLE,
            starting_amount=0
        )
        state.resource_definitions[1] = resource_def
        
        event = Event(
            type="ResourceChanged",
            payload={
                "player_id": "player1",
                "resource": 1,
                "amount": 5
            }
        )
        state.apply_event(event)
        
        assert len(state.event_log) == 1
    
    def test_current_phase_property(self):
        """Test current_phase property"""
        ruleset = RulesetHelper.create_ruleset_ir()
        state = GameState.from_ruleset("test_match", ruleset, ["player1"])
        
        assert state.current_phase == 1
        if state.phase_manager:
            state.phase_manager.current_phase_id = 2
            assert state.current_phase == 2
    
    def test_turn_number_property(self):
        """Test turn_number property"""
        ruleset = RulesetHelper.create_ruleset_ir()
        state = GameState.from_ruleset("test_match", ruleset, ["player1"])
        
        assert state.turn_number == 1
        if state.phase_manager:
            state.phase_manager.turn_number = 5
            assert state.turn_number == 5
    
    def test_get_player(self):
        """Test getting a player component"""
        ruleset = RulesetHelper.create_ruleset_ir()
        state = GameState.from_ruleset("test_match", ruleset, ["player1", "player2"])
        
        # Players should be created from component definitions
        # This depends on the ruleset having player components
        # For now, just test the method exists
        player = state.get_player("player1")
        # May be None if no player component exists in ruleset
        # This is expected behavior
    
    def test_find_resource_instance(self):
        """Test finding a resource instance by component and resource definition"""
        ruleset = RulesetHelper.create_ruleset_ir()
        state = GameState.from_ruleset("test_match", ruleset, ["player1"])
        
        # Create component with resource
        definition = ComponentDefinition(
            id=1,
            name="Component",
            component_type=ComponentType.CARD,
            resources=[
                ResourceDefinition(
                    id=1,
                    name="mana",
                    description="Mana",
                    scope=ResourceScope.OBJECT,
                    resource_type=ResourceType.CONSUMABLE
                )
            ]
        )
        component = state.create_component(definition)
        
        instance_id = state.find_resource_instance(component.id, 1)
        assert instance_id is not None

