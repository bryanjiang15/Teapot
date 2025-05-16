import json
from abilityData import TriggerType, TargetType, TargetRange, TargetSort, EffectType, RequirementType, RequirementComparator, AbilityAmountType
from typing_extensions import TypedDict
import asyncio
from agents import function_tool


class AmountData(TypedDict):
    """Class to represent the amount for an ability
    Attributes:
        amount_type (AbilityAmountType): What kind of value the amount is
        value (int): The value of the amount. This is the constant integer value.
        target_value_property (RequirementType): The property of the target that the amount is based on if the amount_type is TARGETVALUE.
        multiplier_condition (str): The condition that the amount is multiplied by if the amount_type is TARGETVALUE or FOREACHTARGET.
            If the amount_type is TargetValue, this is a str that describe the amount as: the <property> of <a specific target>.
            If the amount_type is ForEachTarget, this is a str that describe the amount as: the number of <targets>.
            Make sure to be descriptive about what property it is based on and what target the amount is based on. Do not include other information.
    """
    amount_type: AbilityAmountType
    value: int
    target_value_property: RequirementType
    multiplier_condition: str
    # constant_value: int
    # target_property: RequirementType
    # target: "TargetData"
    # def to_dict(self) -> dict:
    #     """Convert the AmountData to a dictionary."""
    #     return {
    #         "amount_type": self.amount_type.value,
    #         "constant_value": self.constant_value,
    #         "target_property": self.target_property.value,
    #         "target": self.target
    #     }

class RequirementData(TypedDict):
    """Class to represent the requirement data for a trigger.
    Attributes:
        requirement_type (str): The type of requirement.
        requirement_comparator (str): The comparator for the requirement.
        requirement_amount (int): The amount to compare to.
    """
    requirement_type: RequirementType
    requirement_comparator: RequirementComparator
    requirement_amount: AmountData

    def to_dict(self) -> dict:
        """Convert the RequirementData to a dictionary."""
        return {
            "requirement_type": self.requirement_type.value,
            "requirement_comparator": self.requirement_comparator.value,
            "requirement_amount": self.requirement_amount
        }

class TargetData(TypedDict):
    """Class to represent the target data for a trigger.
    Attributes:
        target_type (TargetType): The type of target that can trigger the ability.
        target_range (TargetRange): The range of the target.
        target_sort (str): The sorting criteria for the target.
        target_requirements (str): The requirements for the target, None if there is no requirement.
    """

    target_type: TargetType
    target_range: TargetRange
    target_sort: TargetSort
    target_requirements: RequirementData

    def to_dict(self) -> dict:
        """Convert the TargetData to a dictionary."""
        return {
            "target_type": self.target_type.value,
            "target_range": self.target_range.value,
            "target_sort": self.target_sort.value,
            "target_requirements": self.target_requirements
        }

class AbilityTrigger(TypedDict):
    """Class to represent the trigger data for an ability.
    Attributes:
        trigger_type (str): The type of trigger.
        trigger_targets (TargetData): Data specifying what target can cause the trigger to activate.
    """
    trigger_type: TriggerType
    trigger_target_data: TargetData

    def to_dict(self) -> dict:
        """Convert the AbilityTrigger to a dictionary."""
        return {
            "trigger_type": self.trigger_type.value,
            "trigger_targets": self.trigger_target_data
        }

class AbilityEffect(TypedDict):
    """Class to represent the effect data for an ability.
    Attributes:
        effect_type (str): The type of effect.
        amount (AmountData): The amount of the effect.
    """
    effect_type: EffectType
    amount: AmountData

    def to_dict(self) -> dict:
        """Convert the AbilityEffect to a dictionary."""
        return {
            "effect_type": self.effect_type.value,
            "amount": self.amount
        }

class AbilityRequirement(TypedDict):
    """Class to represent the requirement data for an ability.
    Attributes:
        requirement (RequirementData): The requirement data for the ability.
        target (TargetData): The target data for the ability.
    """
    requirement: RequirementData
    target: TargetData

    def to_dict(self) -> dict:
        """Convert the AbilityRequirement to a dictionary."""
        return {
            "requirement": self.requirement.to_dict(),
            "target": self.target.to_dict()
        }

@function_tool
async def create_random_card_effect_schema(number_of_cards: int, card_generation_condition: RequirementData) -> AmountData:
    """Create the amountData schema for a random card generation effect.
    Args:
        number_of_cards (int): The number of cards to generate.
        card_generation_condition (RequirementData): The condition that the cards must meet to be a valid choice.
    
    Returns:
        AmountData: The effect schema for the random card generation.
    """
    return AmountData(
        amount_type=AbilityAmountType.RANDOM_CARD,
        value=number_of_cards,
        target_value_property=RequirementType.NONE,
        multiplier_condition=str(card_generation_condition),
    )
@function_tool
async def get_valid_trigger_target_types(trigger_type: TriggerType) -> list[TargetType]:
    """Get the valid target types for a given trigger type.

    Args:
        trigger_type (TriggerType): The type of trigger to check valid targets for.
    
    Returns:
        list[TargetType]: List of valid target types for the given trigger type.
    """
    # Define valid target types for each trigger type
    # Onreveal, ongoing, game start, end turn, end game, have no target
    trigger_target_mapping = {
        TriggerType.ON_REVEAL: [
            TargetType.SELF
        ],
        TriggerType.ONGOING: [
            TargetType.SELF
        ],
        TriggerType.GAME_START: [
            TargetType.SELF
        ],
        TriggerType.END_TURN: [
            TargetType.SELF,
        ],
        TriggerType.END_GAME: [
            TargetType.SELF,
        ],
        TriggerType.IN_HAND: [
            TargetType.SELF,
            TargetType.HAND
        ],
        TriggerType.IN_DECK: [
            TargetType.SELF,
            TargetType.DECK
        ],
        TriggerType.DESTROYED: [
            TargetType.SELF,
            TargetType.PLAYER_DIRECT_LOCATION_CARDS,
            TargetType.ENEMY_DIRECT_LOCATION_CARDS,
            TargetType.ALL_DIRECT_LOCATION_CARDS,
            TargetType.ALL_PLAYER_CARDS,
            TargetType.ALL_ENEMY_CARDS,
            TargetType.ALL_BOARD_CARDS,
        ],
        TriggerType.DISCARDED: [
            TargetType.SELF,
            TargetType.HAND,
            TargetType.DECK,
            TargetType.ENEMY_DECK,
            TargetType.ENEMY_HAND
        ],
        TriggerType.MOVED: [
            TargetType.SELF,
        ],
        TriggerType.BANISHED: [
            TargetType.SELF,
            TargetType.HAND,
            TargetType.DECK,
            TargetType.ENEMY_DECK,
            TargetType.ENEMY_HAND,
            TargetType.PLAYER_DIRECT_LOCATION_CARDS,
            TargetType.ENEMY_DIRECT_LOCATION_CARDS,
            TargetType.ALL_DIRECT_LOCATION_CARDS,
            TargetType.ALL_PLAYER_CARDS,
            TargetType.ALL_ENEMY_CARDS,
            TargetType.ALL_BOARD_CARDS,
        ],
        TriggerType.START_TURN: [
            TargetType.SELF,
        ],
        TriggerType.ACTIVATE: [
            TargetType.SELF,
            TargetType.PLAYER_DIRECT_LOCATION_CARDS,
            TargetType.ENEMY_DIRECT_LOCATION_CARDS,
            TargetType.ALL_DIRECT_LOCATION_CARDS,
            TargetType.ALL_PLAYER_CARDS,
            TargetType.ALL_ENEMY_CARDS,
            TargetType.ALL_BOARD_CARDS,
        ],
        TriggerType.BEFORE_CARD_PLAYED: [
            TargetType.PLAYER_DIRECT_LOCATION_CARDS,
            TargetType.ENEMY_DIRECT_LOCATION_CARDS,
            TargetType.ALL_DIRECT_LOCATION_CARDS,
            TargetType.ALL_PLAYER_CARDS,
            TargetType.ALL_ENEMY_CARDS,
            TargetType.ALL_BOARD_CARDS,
        ],
        TriggerType.AFTER_CARD_PLAYED: [
            TargetType.PLAYER_DIRECT_LOCATION_CARDS,
            TargetType.ENEMY_DIRECT_LOCATION_CARDS,
            TargetType.ALL_DIRECT_LOCATION_CARDS,
            TargetType.ALL_PLAYER_CARDS,
            TargetType.ALL_ENEMY_CARDS,
            TargetType.ALL_BOARD_CARDS,
        ],
        TriggerType.AFTER_ABILITY_TRIGGERED: [
            TargetType.SELF
        ],
        TriggerType.ON_CREATED: [
            TargetType.PLAYER_DIRECT_LOCATION_CARDS,
            TargetType.ENEMY_DIRECT_LOCATION_CARDS,
            TargetType.ALL_DIRECT_LOCATION_CARDS,
            TargetType.ALL_PLAYER_CARDS,
            TargetType.ALL_ENEMY_CARDS,
            TargetType.ALL_BOARD_CARDS,
            TargetType.HAND,
            TargetType.DECK,
            TargetType.ENEMY_DECK,
            TargetType.ENEMY_HAND
        ],
        TriggerType.NONE: [
            TargetType.SELF
        ]
    }
    
    return trigger_target_mapping.get(trigger_type, [TargetType.SELF])

@function_tool
async def get_valid_effect_target_types(effect_type: EffectType) -> list[TargetType]:
    """Get the valid target types for a given effect type.

    Args:
        effect_type (EffectType): The type of effect to check valid targets for.
    
    Returns:
        list[TargetType]: List of valid target types for the given effect type.
    """
    # Define valid target types for each effect type
    effect_target_mapping = {
        EffectType.GAIN_POWER: [
            TargetType.SELF,
            TargetType.PLAYER_DIRECT_LOCATION_CARDS,
            TargetType.ENEMY_DIRECT_LOCATION_CARDS,
            TargetType.ALL_DIRECT_LOCATION_CARDS,
            TargetType.ALL_PLAYER_CARDS,
            TargetType.ALL_ENEMY_CARDS,
            TargetType.ALL_BOARD_CARDS,
            TargetType.HAND,
            TargetType.DECK,
            TargetType.ENEMY_DECK,
            TargetType.ENEMY_HAND,
            TargetType.NEXT_PLAYED_CARD,
            TargetType.TRIGGERED_ACTION_TARGETS,
            TargetType.TRIGGERED_ACTION_SOURCE,
            TargetType.CREATED_CARD
        ],
        EffectType.LOSE_POWER: [
            TargetType.SELF,
            TargetType.PLAYER_DIRECT_LOCATION_CARDS,
            TargetType.ENEMY_DIRECT_LOCATION_CARDS,
            TargetType.ALL_DIRECT_LOCATION_CARDS,
            TargetType.ALL_PLAYER_CARDS,
            TargetType.ALL_ENEMY_CARDS,
            TargetType.ALL_BOARD_CARDS,
            TargetType.HAND,
            TargetType.DECK,
            TargetType.ENEMY_DECK,
            TargetType.ENEMY_HAND,
            TargetType.NEXT_PLAYED_CARD,
            TargetType.TRIGGERED_ACTION_TARGETS,
            TargetType.TRIGGERED_ACTION_SOURCE,
            TargetType.CREATED_CARD
        ],
        EffectType.STEAL_POWER: [
            TargetType.PLAYER_DIRECT_LOCATION_CARDS,
            TargetType.ENEMY_DIRECT_LOCATION_CARDS,
            TargetType.ALL_DIRECT_LOCATION_CARDS,
            TargetType.ALL_PLAYER_CARDS,
            TargetType.ALL_ENEMY_CARDS,
            TargetType.ALL_BOARD_CARDS,
            TargetType.HAND,
            TargetType.DECK,
            TargetType.ENEMY_DECK,
            TargetType.ENEMY_HAND,
            TargetType.NEXT_PLAYED_CARD,
            TargetType.TRIGGERED_ACTION_TARGETS,
            TargetType.TRIGGERED_ACTION_SOURCE,
            TargetType.CREATED_CARD
        ],
        EffectType.AFFLICT: [
            TargetType.SELF,
            TargetType.PLAYER_DIRECT_LOCATION_CARDS,
            TargetType.ENEMY_DIRECT_LOCATION_CARDS,
            TargetType.ALL_DIRECT_LOCATION_CARDS,
            TargetType.ALL_PLAYER_CARDS,
            TargetType.ALL_ENEMY_CARDS,
            TargetType.ALL_BOARD_CARDS,
            TargetType.HAND,
            TargetType.DECK,
            TargetType.ENEMY_DECK,
            TargetType.ENEMY_HAND,
            TargetType.NEXT_PLAYED_CARD,
            TargetType.TRIGGERED_ACTION_TARGETS,
            TargetType.TRIGGERED_ACTION_SOURCE,
            TargetType.CREATED_CARD
        ],
        EffectType.DRAW: [
            TargetType.DECK,
            TargetType.ENEMY_DECK
        ],
        EffectType.DISCARD: [
            TargetType.SELF,
            TargetType.HAND,
            TargetType.ENEMY_HAND
        ],
        EffectType.DESTROY: [
            TargetType.SELF,
            TargetType.PLAYER_DIRECT_LOCATION_CARDS,
            TargetType.ENEMY_DIRECT_LOCATION_CARDS,
            TargetType.ALL_DIRECT_LOCATION_CARDS,
            TargetType.ALL_PLAYER_CARDS,
            TargetType.ALL_ENEMY_CARDS,
            TargetType.ALL_BOARD_CARDS,
            TargetType.NEXT_PLAYED_CARD,
            TargetType.TRIGGERED_ACTION_TARGETS,
            TargetType.TRIGGERED_ACTION_SOURCE,
            TargetType.CREATED_CARD
        ],
        EffectType.MOVE: [
            TargetType.SELF,
            TargetType.PLAYER_DIRECT_LOCATION_CARDS,
            TargetType.ENEMY_DIRECT_LOCATION_CARDS,
            TargetType.ALL_DIRECT_LOCATION_CARDS,
            TargetType.ALL_PLAYER_CARDS,
            TargetType.ALL_ENEMY_CARDS,
            TargetType.ALL_BOARD_CARDS,
            TargetType.NEXT_PLAYED_CARD,
            TargetType.TRIGGERED_ACTION_TARGETS,
            TargetType.TRIGGERED_ACTION_SOURCE,
            TargetType.CREATED_CARD
        ],
        EffectType.GAIN_ENERGY: [
            TargetType.SELF
        ],
        EffectType.GAIN_MAX_ENERGY: [
            TargetType.SELF
        ],
        EffectType.LOSE_ENERGY: [
            TargetType.SELF
        ],
        EffectType.ADD_POWER_TO_LOCATION: [
            TargetType.PLAYER_DIRECT_LOCATION,
            TargetType.ENEMY_DIRECT_LOCATION,
            TargetType.DIRECT_LOCATION,
            TargetType.ALL_PLAYER_LOCATION,
            TargetType.ALL_ENEMY_LOCATION,
            TargetType.ALL_LOCATION
        ],
        EffectType.CREATE_CARD_IN_HAND: [
            TargetType.HAND,
            TargetType.ENEMY_HAND
        ],
        EffectType.CREATE_CARD_IN_DECK: [
            TargetType.DECK,
            TargetType.ENEMY_DECK
        ],
        EffectType.CREATE_CARD_IN_LOCATION: [
            TargetType.PLAYER_DIRECT_LOCATION,
            TargetType.ENEMY_DIRECT_LOCATION,
            TargetType.DIRECT_LOCATION,
            TargetType.ALL_PLAYER_LOCATION,
            TargetType.ALL_ENEMY_LOCATION,
            TargetType.ALL_LOCATION
        ],
        EffectType.REMOVE_ABILITY: [
            TargetType.SELF,
            TargetType.PLAYER_DIRECT_LOCATION_CARDS,
            TargetType.ENEMY_DIRECT_LOCATION_CARDS,
            TargetType.ALL_DIRECT_LOCATION_CARDS,
            TargetType.ALL_PLAYER_CARDS,
            TargetType.ALL_ENEMY_CARDS,
            TargetType.ALL_BOARD_CARDS,
            TargetType.NEXT_PLAYED_CARD,
            TargetType.TRIGGERED_ACTION_TARGETS,
            TargetType.TRIGGERED_ACTION_SOURCE,
            TargetType.CREATED_CARD,
            TargetType.HAND,
            TargetType.DECK,
            TargetType.ENEMY_DECK,
            TargetType.ENEMY_HAND
        ],
        EffectType.REDUCE_COST: [
            TargetType.SELF,
            TargetType.HAND,
            TargetType.DECK
        ],
        EffectType.INCREASE_COST: [
            TargetType.SELF,
            TargetType.HAND,
            TargetType.DECK,
            TargetType.ENEMY_DECK,
            TargetType.ENEMY_HAND
        ],
        EffectType.MERGE: [
            TargetType.PLAYER_DIRECT_LOCATION_CARDS,
            TargetType.ENEMY_DIRECT_LOCATION_CARDS,
            TargetType.ALL_DIRECT_LOCATION_CARDS,
            TargetType.ALL_PLAYER_CARDS,
            TargetType.ALL_ENEMY_CARDS,
            TargetType.ALL_BOARD_CARDS,
            TargetType.NEXT_PLAYED_CARD,
            TargetType.TRIGGERED_ACTION_TARGETS,
            TargetType.TRIGGERED_ACTION_SOURCE,
        ],
        EffectType.RETURN: [
            TargetType.SELF,
            TargetType.PLAYER_DIRECT_LOCATION_CARDS,
            TargetType.ENEMY_DIRECT_LOCATION_CARDS,
            TargetType.ALL_DIRECT_LOCATION_CARDS,
            TargetType.ALL_PLAYER_CARDS,
            TargetType.ALL_ENEMY_CARDS,
            TargetType.ALL_BOARD_CARDS,
            TargetType.TRIGGERED_ACTION_TARGETS,
            TargetType.TRIGGERED_ACTION_SOURCE,
        ],
        EffectType.ADD_CARD_TO_LOCATION: [
            TargetType.PLAYER_DIRECT_LOCATION,
            TargetType.ENEMY_DIRECT_LOCATION,
            TargetType.DIRECT_LOCATION,
            TargetType.ALL_PLAYER_LOCATION,
            TargetType.ALL_ENEMY_LOCATION,
            TargetType.ALL_LOCATION
        ],
        EffectType.ADD_CARD_TO_HAND: [
            TargetType.HAND,
            TargetType.ENEMY_HAND
        ],
        EffectType.SET_POWER: [
            TargetType.SELF,
            TargetType.HAND,
            TargetType.DECK,
            TargetType.ENEMY_DECK,
            TargetType.ENEMY_HAND,
            TargetType.PLAYER_DIRECT_LOCATION_CARDS,
            TargetType.ENEMY_DIRECT_LOCATION_CARDS,
            TargetType.ALL_DIRECT_LOCATION_CARDS,
            TargetType.ALL_PLAYER_CARDS,
            TargetType.ALL_ENEMY_CARDS,
            TargetType.ALL_BOARD_CARDS,
            TargetType.NEXT_PLAYED_CARD,
            TargetType.TRIGGERED_ACTION_TARGETS,
            TargetType.TRIGGERED_ACTION_SOURCE,
            TargetType.CREATED_CARD
        ],
        EffectType.SET_COST: [
            TargetType.SELF,
            TargetType.HAND,
            TargetType.DECK,
            TargetType.ENEMY_DECK,
            TargetType.ENEMY_HAND
        ],
        EffectType.COPY_AND_ACTIVATE: [
            TargetType.PLAYER_DIRECT_LOCATION_CARDS,
            TargetType.ENEMY_DIRECT_LOCATION_CARDS,
            TargetType.ALL_DIRECT_LOCATION_CARDS,
            TargetType.ALL_PLAYER_CARDS,
            TargetType.ALL_ENEMY_CARDS,
            TargetType.ALL_BOARD_CARDS,
            TargetType.NEXT_PLAYED_CARD,
            TargetType.TRIGGERED_ACTION_TARGETS,
            TargetType.TRIGGERED_ACTION_SOURCE,
        ],
        EffectType.ADD_KEYWORD: [
            TargetType.SELF,
            TargetType.HAND,
            TargetType.DECK,
            TargetType.ENEMY_DECK,
            TargetType.ENEMY_HAND,
            TargetType.PLAYER_DIRECT_LOCATION_CARDS,
            TargetType.ENEMY_DIRECT_LOCATION_CARDS,
            TargetType.ALL_DIRECT_LOCATION_CARDS,
            TargetType.ALL_PLAYER_CARDS,
            TargetType.ALL_ENEMY_CARDS,
            TargetType.ALL_BOARD_CARDS,
            TargetType.NEXT_PLAYED_CARD,
            TargetType.TRIGGERED_ACTION_TARGETS,
            TargetType.TRIGGERED_ACTION_SOURCE,
            TargetType.CREATED_CARD
        ],
        EffectType.ADD_TEMPORARY_ABILITY: [
            TargetType.SELF,
            TargetType.PLAYER_DIRECT_LOCATION_CARDS,
            TargetType.ENEMY_DIRECT_LOCATION_CARDS,
            TargetType.ALL_DIRECT_LOCATION_CARDS,
            TargetType.ALL_PLAYER_CARDS,
            TargetType.ALL_ENEMY_CARDS,
            TargetType.ALL_BOARD_CARDS
        ]
    }
    
    return effect_target_mapping.get(effect_type, [TargetType.SELF])
    

@function_tool
async def get_card_id(card_name: str) -> int:
    """Get the card id for a given card name.

    Args:
        card_name (str): The name of the card to check.
    
    Returns:
        int: The card id for the given card name. -1 if the card does not exist.
    """
    return 2