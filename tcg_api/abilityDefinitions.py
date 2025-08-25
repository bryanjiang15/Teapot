from dataclasses import dataclass
from abilityData import TriggerType, TargetType, TargetRange, TargetSort, EffectType, RequirementType, RequirementComparator, AbilityAmountType
from agents import function_tool

@dataclass
class AmountData:
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

    def __str__(self) -> str:
        if self.amountType == AbilityAmountType.CONSTANT:
            return f"{self.value}"
        elif self.amountType == AbilityAmountType.TARGET_VALUE:
            return f"the {self.targetValueProperty.value} of {self.multiplierCondition}"
        elif self.amountType == AbilityAmountType.FOR_EACH_TARGET:
            return f"the number of {self.multiplierCondition}"
        elif self.amountType == AbilityAmountType.RANDOM_CARD:
            return f"{self.value} random cards ({self.multiplierCondition})"
        else:
            return f"{self.amountType.value}: {self.value}"

    def __repr__(self) -> str:
        return f"AmountData({self.amountType.value}, {self.value}, {self.targetValueProperty.value}, '{self.multiplierCondition}')"

    def get_processable_queries(self) -> list[str]:
        """return processable amount data multiplier condition."""
        if self.amountType in [AbilityAmountType.TARGET_VALUE, AbilityAmountType.FOR_EACH_TARGET]:
            return [self.multiplierCondition]
        return []
    
    def update_data(self, processed_results: dict[str, dict]) -> None:
        """Update the amount data with the given processed results."""
        if self.amountType in [AbilityAmountType.TARGET_VALUE, AbilityAmountType.FOR_EACH_TARGET]:
            if self.multiplierCondition in processed_results:
                self.value = processed_results[self.multiplierCondition]

@dataclass
class RequirementData:
    """Class to represent the requirement data for a trigger.
    Attributes:
        requirementType (str): The type of requirement.
        requirementComparator (str): The comparator for the requirement.
        requirementAmount (int): The amount to compare to.
    """
    requirementType: RequirementType
    requirementComparator: RequirementComparator
    requirementAmount: AmountData

    def __str__(self) -> str:
        return f"{self.requirementType.value} {self.requirementComparator.value} {self.requirementAmount}"

    def __repr__(self) -> str:
        return f"RequirementData({self.requirementType.value}, {self.requirementComparator.value}, {repr(self.requirementAmount)})"

    def to_dict(self) -> dict:
        """Convert the RequirementData to a dictionary."""
        return {
            "requirementType": self.requirementType.value,
            "requirementComparator": self.requirementComparator.value,
            "requirementAmount": self.requirementAmount
        }
    
    def get_processable_queries(self) -> list[str]:
        """return processable amount data multiplier condition."""
        return self.requirementAmount.get_processable_queries()
    
    def update_data(self, processed_results: dict[str, dict]) -> None:
        """Update the requirement data with the given processed results."""
        self.requirementAmount.update_data(processed_results)

@dataclass
class TargetData:
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
    targetRequirements: list[RequirementData]
    excludeSelf: bool

    def __str__(self) -> str:
        target_str = self.targetType.value
        if self.excludeSelf:
            target_str += " (exclude self)"
        if self.targetRequirements:
            req_str = ", ".join(str(req) for req in self.targetRequirements)
            target_str += f" where {req_str}"
        return target_str

    def __repr__(self) -> str:
        return f"TargetData({self.targetType.value}, {self.targetRange.value}, {self.targetSort.value}, {len(self.targetRequirements)} requirements, excludeSelf={self.excludeSelf})"

    def to_dict(self) -> dict:
        """Convert the TargetData to a dictionary."""
        return {
            "targetType": self.targetType.value,
            "targetRange": self.targetRange.value,
            "targetSort": self.targetSort.value,
            "targetRequirements": [requirement.to_dict() for requirement in self.targetRequirements],
            "excludeSelf": self.excludeSelf
        }
    
    def get_processable_queries(self) -> list[str]:
        """Validate the data and return processable amount data descriptions."""
        processable_queries = []
        for requirement in self.targetRequirements:
            processable_queries.extend(requirement.get_processable_queries())
        return processable_queries
    
    def update_data(self, processed_results: dict[str, dict]) -> None:
        """Update the target data with the given processed results."""
        for requirement in self.targetRequirements:
            requirement.update_data(processed_results)

@dataclass
class AbilityTrigger:
    """Class to represent the trigger data for an ability.
    Attributes:
        triggerType (TriggerType): The type of trigger.
        triggerSource (TargetData): Data specifying what target can cause the trigger to activate.
    """
    triggerType: TriggerType
    triggerSource: list[TargetData]

    def __str__(self) -> str:
        if not self.triggerSource:
            return f"Trigger: {self.triggerType.value}"
        sources_str = ", ".join(str(source) for source in self.triggerSource)
        return f"Trigger: {self.triggerType.value} from {sources_str}"

    def __repr__(self) -> str:
        return f"AbilityTrigger({self.triggerType.value}, {len(self.triggerSource)} sources)"

    def to_dict(self) -> dict:
        """Convert the AbilityTrigger to a dictionary."""
        return {
            "triggerType": self.triggerType.value,
            "triggerSource": [target.to_dict() for target in self.triggerSource]
        }
    
    def get_processable_queries(self) -> list[str]:
        """Validate the data and return processable amount data descriptions."""
        processable_queries = []
        for target in self.triggerSource:
            processable_queries.extend(target.get_processable_queries())
        return processable_queries
    
    def update_data(self, processed_results: dict[str, dict]) -> None:
        """Update the trigger data with the given processed results."""
        for target in self.triggerSource:
            target.update_data(processed_results)

@dataclass
class AbilityEffect:
    """Class to represent the effect data for an ability.
    Attributes:
        effectType (str): The type of effect.
        amount (AmountData): The amount of the effect.
    """
    effectType: EffectType
    amount: AmountData

    def __str__(self) -> str:
        return f"Effect: {self.effectType.value} {self.amount}"

    def __repr__(self) -> str:
        return f"AbilityEffect({self.effectType.value}, {repr(self.amount)})"

    def to_dict(self) -> dict:
        """Convert the AbilityEffect to a dictionary."""
        return {
            "effectType": self.effectType.value,
            "amount": self.amount
        }

    def get_processable_queries(self) -> list[str]:
        """Validate the data and return processable amount data descriptions."""
        return self.amount.get_processable_queries()
    
    def update_data(self, processed_results: dict[str, dict]) -> None:
        """Update the effect data with the given processed results."""
        self.amount.update_data(processed_results)

@dataclass
class AbilityRequirement:
    """Class to represent the requirement data for an ability.
    Attributes:
        requirement (RequirementData): The requirement data for the ability.
        target (TargetData): The target data for the ability.
    """
    requirement: RequirementData
    target: TargetData

    def __str__(self) -> str:
        return f"Requirement: {self.requirement} on {self.target}"

    def __repr__(self) -> str:
        return f"AbilityRequirement({repr(self.requirement)}, {repr(self.target)})"

    def to_dict(self) -> dict:
        """Convert the AbilityRequirement to a dictionary."""
        return {
            "requirement": self.requirement.to_dict(),
            "target": self.target.to_dict()
        }
    
    def get_processable_queries(self) -> list[str]:
        """Validate the data and return processable amount data descriptions."""
        return self.requirement.get_processable_queries() + self.target.get_processable_queries()
    
    def update_data(self, processed_results: dict[str, dict]) -> None:
        """Update the requirement data with the given processed results."""
        self.requirement.update_data(processed_results)
        self.target.update_data(processed_results)

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
    