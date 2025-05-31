import json
from abilityData import TriggerType, TargetType, TargetRange, TargetSort, EffectType, RequirementType, RequirementComparator, AbilityAmountType
from typing_extensions import TypedDict
from pydantic import BaseModel
from agents import function_tool


class AmountData(TypedDict):
    """Class to represent the amount for an ability
    Attributes:
        amountType (AbilityAmountType): What kind of value the amount is
        value (int): The value of the amount. This is the constant integer value.
        targetValueProperty (RequirementType): The property of the target that the amount is based on if the amount_type is TARGETVALUE.
        multiplierCondition (str): The condition that the amount is multiplied by if the amount_type is TARGETVALUE or FOREACHTARGET.
            If the amountType is TargetValue, this is a str that describe the amount as: the <property> of <a specific target>.
            If the amountType is ForEachTarget, this is a str that describe the amount as: the number of <targets>.
            Make sure to be descriptive about what property it is based on and what target the amount is based on. Do not include other information.
    """
    amountType: AbilityAmountType
    value: int
    targetValueProperty: RequirementType
    multiplierCondition: str

class RequirementData(TypedDict):
    """Class to represent the requirement data for a trigger.
    Attributes:
        requirementType (str): The type of requirement.
        requirementComparator (str): The comparator for the requirement.
        requirementAmount (int): The amount to compare to.
    """
    requirementType: RequirementType
    requirementComparator: RequirementComparator
    requirementAmount: AmountData

    def to_dict(self) -> dict:
        """Convert the RequirementData to a dictionary."""
        return {
            "requirementType": self.requirementType.value,
            "requirementComparator": self.requirementComparator.value,
            "requirementAmount": self.requirementAmount
        }

class TargetData(TypedDict):
    """Class to represent the target data for a trigger.
    Attributes:
        targetType (TargetType): The type of target that can trigger the ability.
        targetRange (TargetRange): The range of the target.
        targetSort (str): The sorting criteria for the target.
        targetRequirements (str): The requirements for the target, None if there is no requirement.
    """

    targetType: TargetType
    targetRange: TargetRange
    targetSort: TargetSort
    targetRequirements: RequirementData

    def to_dict(self) -> dict:
        """Convert the TargetData to a dictionary."""
        return {
            "targetType": self.targetType.value,
            "targetRange": self.targetRange.value,
            "targetSort": self.targetSort.value,
            "targetRequirements": self.targetRequirements
        }

class AbilityTrigger(TypedDict):
    """Class to represent the trigger data for an ability.
    Attributes:
        triggerType (TriggerType): The type of trigger.
        triggerSource (TargetData): Data specifying what target can cause the trigger to activate.
    """
    triggerType: TriggerType
    triggerSource: list[TargetData]

    def to_dict(self) -> dict:
        """Convert the AbilityTrigger to a dictionary."""
        return {
            "triggerType": self.triggerType.value,
            "triggerSource": self.triggerSource
        }

class AbilityEffect(TypedDict):
    """Class to represent the effect data for an ability.
    Attributes:
        effectType (str): The type of effect.
        amount (AmountData): The amount of the effect.
    """
    effectType: EffectType
    amount: AmountData

    def to_dict(self) -> dict:
        """Convert the AbilityEffect to a dictionary."""
        return {
            "effectType": self.effectType.value,
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
async def create_random_card_effect_schema(numberOfCards: int, cardGenerationCondition: RequirementData) -> AmountData:
    """Create the amountData schema for a random card generation effect.
    Args:
        numberOfCards (int): The number of cards to generate.
        cardGenerationCondition (RequirementData): The condition that the cards must meet to be a valid choice.
    
    Returns:
        AmountData: The effect schema for the random card generation.
    """
    return AmountData(
        amount_type=AbilityAmountType.RANDOM_CARD,
        value=numberOfCards,
        target_value_property=RequirementType.NONE,
        multiplier_condition=str(cardGenerationCondition),
    )

@function_tool
async def get_valid_trigger_target_types(triggerType: TriggerType) -> list[TargetType]:
    """Get the valid target types for a given trigger type.

    Args:
        triggerType (TriggerType): The type of trigger to check valid targets for.
    
    Returns:
        list[TargetType]: List of valid target types for the given trigger type.
    """
    # Define valid target types for each trigger type
    # Onreveal, ongoing, game start, end turn, end game, have no target
    triggerTargetMapping = {
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
    
    return triggerTargetMapping.get(triggerType, [TargetType.SELF])

@function_tool
async def get_valid_effect_target_types(effectType: EffectType) -> list[TargetType]:
    """Get the valid target types for a given effect type.

    Args:
        effectType (EffectType): The type of effect to check valid targets for.
    
    Returns:
        list[TargetType]: List of valid target types for the given effect type.
    """
    # Define valid target types for each effect type
    effectTargetMapping = {
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
    
    return effectTargetMapping.get(effectType, [TargetType.SELF])
    

@function_tool
async def get_card_id(cardName: str) -> int:
    """Get the card id for a given card name.

    Args:
        cardName (str): The name of the card to check.
    
    Returns:
        int: The card id for the given card name. -1 if the card does not exist.
    """
    return 2

class AbilityRequest(BaseModel):
    description: str

class AbilityResponse(BaseModel):
    triggerDefinition: AbilityTrigger
    effect: EffectType
    amount: AmountData
    targetDefinition: list[TargetData]