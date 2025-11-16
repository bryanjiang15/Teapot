"""
Tests for Component and ComponentManager classes
"""

import pytest
from TeapotEngine.core.component import Component, ComponentManager, ComponentStatus
from TeapotEngine.ruleset.componentDefinition import ComponentDefinition, ComponentType
from TeapotEngine.ruleset.ruleDefinitions.rule_definitions import TriggerDefinition
from TeapotEngine.ruleset.models.resource_models import ResourceDefinition, ResourceScope, ResourceType


class TestComponent:
    """Tests for Component class"""
    
    def test_create_component(self):
        """Test creating a basic component"""
        component = Component(
            id=1,
            definition_id=10,
            name="Test Component",
            component_type=ComponentType.CARD
        )
        assert component.id == 1
        assert component.definition_id == 10
        assert component.name == "Test Component"
        assert component.component_type == ComponentType.CARD
        assert component.status == ComponentStatus.ACTIVE
        assert component.properties == {}
        assert component.triggers == []
    
    def test_component_with_properties(self):
        """Test component with custom properties"""
        component = Component(
            id=2,
            definition_id=11,
            name="Component with Props",
            component_type=ComponentType.CARD,
            properties={"cost": 3, "power": 2}
        )
        assert component.properties == {"cost": 3, "power": 2}
    
    def test_component_with_zone_and_controller(self):
        """Test component with zone and controller"""
        component = Component(
            id=3,
            definition_id=12,
            name="Zoned Component",
            component_type=ComponentType.CARD,
            zone="hand",
            controller_id="player1"
        )
        assert component.zone == "hand"
        assert component.controller_id == "player1"
    
    def test_add_trigger(self):
        """Test adding a trigger to a component"""
        component = Component(
            id=4,
            definition_id=13,
            name="Component with Trigger",
            component_type=ComponentType.CARD
        )
        trigger = TriggerDefinition(
            id=1,
            when={"eventType": "PhaseEntered"},
            execute_rules=[1]
        )
        component.add_trigger(trigger)
        assert len(component.triggers) == 1
        assert component.triggers[0].id == 1
    
    def test_is_active(self):
        """Test checking if component is active"""
        component = Component(
            id=9,
            definition_id=18,
            name="Active Component",
            component_type=ComponentType.CARD
        )
        assert component.is_active() is True
        
        component.status = ComponentStatus.INACTIVE
        assert component.is_active() is False
        
        component.status = ComponentStatus.DESTROYED
        assert component.is_active() is False
    
    def test_set_zone(self):
        """Test setting component zone"""
        component = Component(
            id=10,
            definition_id=19,
            name="Component",
            component_type=ComponentType.CARD
        )
        component.set_zone("battlefield")
        assert component.zone == "battlefield"
    
    def test_set_controller(self):
        """Test setting component controller"""
        component = Component(
            id=11,
            definition_id=20,
            name="Component",
            component_type=ComponentType.CARD
        )
        component.set_controller("player2")
        assert component.controller_id == "player2"
    
    def test_update_metadata(self):
        """Test updating component metadata"""
        component = Component(
            id=12,
            definition_id=21,
            name="Component",
            component_type=ComponentType.CARD
        )
        component.update_metadata("key1", "value1")
        assert component.get_metadata("key1") == "value1"
    
    def test_get_metadata(self):
        """Test getting component metadata"""
        component = Component(
            id=13,
            definition_id=22,
            name="Component",
            component_type=ComponentType.CARD
        )
        component.update_metadata("test", 42)
        assert component.get_metadata("test") == 42
        assert component.get_metadata("nonexistent") is None
        assert component.get_metadata("nonexistent", "default") == "default"
    
    def test_add_resource_instance(self):
        """Test adding a resource instance to a component"""
        component = Component(
            id=14,
            definition_id=23,
            name="Component",
            component_type=ComponentType.CARD
        )
        resource_def = ResourceDefinition(
            id=1,
            name="mana",
            description="Mana resource",
            scope=ResourceScope.PLAYER,
            resource_type=ResourceType.CONSUMABLE,
            starting_amount=5
        )
        instance_id = component.add_resource_instance(100, resource_def)
        assert instance_id == 100
        assert 100 in component.resources_by_instance_id
        assert len(component.get_resource_instances(1)) == 1
    
    def test_get_resource_instances(self):
        """Test getting resource instances by definition ID"""
        component = Component(
            id=15,
            definition_id=24,
            name="Component",
            component_type=ComponentType.CARD
        )
        resource_def = ResourceDefinition(
            id=2,
            name="energy",
            description="Energy resource",
            scope=ResourceScope.OBJECT,
            resource_type=ResourceType.CONSUMABLE
        )
        component.add_resource_instance(200, resource_def)
        component.add_resource_instance(201, resource_def)
        
        instances = component.get_resource_instances(2)
        assert len(instances) == 2
        assert 200 in instances
        assert 201 in instances
    
    def test_get_resource_by_instance(self):
        """Test getting a resource by instance ID"""
        component = Component(
            id=16,
            definition_id=25,
            name="Component",
            component_type=ComponentType.CARD
        )
        resource_def = ResourceDefinition(
            id=3,
            name="life",
            description="Life resource",
            scope=ResourceScope.PLAYER,
            resource_type=ResourceType.TRACKED,
            starting_amount=20
        )
        instance_id = component.add_resource_instance(300, resource_def)
        resource = component.get_resource_by_instance(instance_id)
        assert resource is not None
        assert resource.resource_id == 3
        assert resource.current_amount == 20


class TestComponentManager:
    """Tests for ComponentManager class"""
    
    def test_create_manager(self):
        """Test creating a component manager"""
        manager = ComponentManager()
        assert manager.get_component_count() == 0
    
    def test_create_component(self):
        """Test creating a component instance"""
        manager = ComponentManager()
        definition = ComponentDefinition(
            id=1,
            name="Test Component",
            component_type=ComponentType.CARD
        )
        component = manager.create_component(definition)
        assert component is not None
        assert component.definition_id == 1
        assert component.name == "Test Component"
        assert manager.get_component_count() == 1
    
    def test_create_component_with_zone_and_controller(self):
        """Test creating component with zone and controller"""
        manager = ComponentManager()
        definition = ComponentDefinition(
            id=2,
            name="Component",
            component_type=ComponentType.CARD
        )
        component = manager.create_component(
            definition,
            zone="hand",
            controller_id="player1"
        )
        assert component.zone == "hand"
        assert component.controller_id == "player1"
    
    def test_get_component(self):
        """Test getting a component by ID"""
        manager = ComponentManager()
        definition = ComponentDefinition(
            id=3,
            name="Component",
            component_type=ComponentType.CARD
        )
        component = manager.create_component(definition)
        component_id = component.id
        
        retrieved = manager.get_component(component_id)
        assert retrieved is not None
        assert retrieved.id == component_id
    
    def test_get_nonexistent_component(self):
        """Test getting a nonexistent component"""
        manager = ComponentManager()
        retrieved = manager.get_component(999)
        assert retrieved is None
    
    def test_remove_component(self):
        """Test removing a component"""
        manager = ComponentManager()
        definition = ComponentDefinition(
            id=4,
            name="Component",
            component_type=ComponentType.CARD
        )
        component = manager.create_component(definition)
        component_id = component.id
        
        result = manager.remove_component(component_id)
        assert result is True
        assert manager.get_component(component_id) is None
        assert manager.get_component_count() == 0
    
    def test_remove_nonexistent_component(self):
        """Test removing a nonexistent component"""
        manager = ComponentManager()
        result = manager.remove_component(999)
        assert result is False
    
    def test_get_components_by_type(self):
        """Test getting components by type"""
        manager = ComponentManager()
        card_def = ComponentDefinition(id=5, name="Card", component_type=ComponentType.CARD)
        player_def = ComponentDefinition(id=6, name="Player", component_type=ComponentType.PLAYER)
        
        card = manager.create_component(card_def)
        player = manager.create_component(player_def)
        
        cards = manager.get_components_by_type(ComponentType.CARD)
        assert len(cards) == 1
        assert cards[0].id == card.id
        
        players = manager.get_components_by_type(ComponentType.PLAYER)
        assert len(players) == 1
        assert players[0].id == player.id
    
    def test_get_component_by_type_and_id(self):
        """Test getting component by type and ID"""
        manager = ComponentManager()
        definition = ComponentDefinition(
            id=7,
            name="Component",
            component_type=ComponentType.CARD
        )
        component = manager.create_component(definition)
        
        retrieved = manager.get_component_by_type_and_id(ComponentType.CARD, component.id)
        assert retrieved is not None
        assert retrieved.id == component.id
    
    def test_get_components_by_zone(self):
        """Test getting components by zone"""
        manager = ComponentManager()
        definition = ComponentDefinition(
            id=8,
            name="Component",
            component_type=ComponentType.CARD
        )
        component1 = manager.create_component(definition, zone="hand")
        component2 = manager.create_component(definition, zone="hand")
        component3 = manager.create_component(definition, zone="battlefield")
        
        hand_components = manager.get_components_by_zone("hand")
        assert len(hand_components) == 2
        
        battlefield_components = manager.get_components_by_zone("battlefield")
        assert len(battlefield_components) == 1
    
    def test_get_components_by_controller(self):
        """Test getting components by controller"""
        manager = ComponentManager()
        definition = ComponentDefinition(
            id=9,
            name="Component",
            component_type=ComponentType.CARD
        )
        component1 = manager.create_component(definition, controller_id="player1")
        component2 = manager.create_component(definition, controller_id="player1")
        component3 = manager.create_component(definition, controller_id="player2")
        
        player1_components = manager.get_components_by_controller("player1")
        assert len(player1_components) == 2
        
        player2_components = manager.get_components_by_controller("player2")
        assert len(player2_components) == 1
    
    def test_move_component(self):
        """Test moving a component to a new zone"""
        manager = ComponentManager()
        definition = ComponentDefinition(
            id=10,
            name="Component",
            component_type=ComponentType.CARD
        )
        component = manager.create_component(definition, zone="hand")
        component_id = component.id
        
        result = manager.move_component(component_id, "battlefield")
        assert result is True
        assert manager.get_component(component_id).zone == "battlefield"
        
        # Check zone indexing
        hand_components = manager.get_components_by_zone("hand")
        assert component_id not in [c.id for c in hand_components]
        
        battlefield_components = manager.get_components_by_zone("battlefield")
        assert component_id in [c.id for c in battlefield_components]
    
    def test_move_component_with_controller(self):
        """Test moving component with new controller"""
        manager = ComponentManager()
        definition = ComponentDefinition(
            id=11,
            name="Component",
            component_type=ComponentType.CARD
        )
        component = manager.create_component(definition, zone="hand", controller_id="player1")
        component_id = component.id
        
        manager.move_component(component_id, "battlefield", "player2")
        moved = manager.get_component(component_id)
        assert moved.zone == "battlefield"
        assert moved.controller_id == "player2"
    
    def test_move_nonexistent_component(self):
        """Test moving a nonexistent component"""
        manager = ComponentManager()
        result = manager.move_component(999, "battlefield")
        assert result is False
    
    def test_get_all_components(self):
        """Test getting all components"""
        manager = ComponentManager()
        definition = ComponentDefinition(
            id=12,
            name="Component",
            component_type=ComponentType.CARD
        )
        component1 = manager.create_component(definition)
        component2 = manager.create_component(definition)
        component3 = manager.create_component(definition)
        
        all_components = manager.get_all_components()
        assert len(all_components) == 3
        assert all(c.id in [component1.id, component2.id, component3.id] for c in all_components)
    
    def test_component_id_auto_increment(self):
        """Test that component IDs auto-increment"""
        manager = ComponentManager()
        definition = ComponentDefinition(
            id=13,
            name="Component",
            component_type=ComponentType.CARD
        )
        component1 = manager.create_component(definition)
        component2 = manager.create_component(definition)
        component3 = manager.create_component(definition)
        
        assert component1.id == 1
        assert component2.id == 2
        assert component3.id == 3

