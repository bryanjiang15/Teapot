from enum import Enum

class TriggerType(Enum):
    ON_REVEAL = "OnReveal"  # When card is revealed - from any place (hand, deck, created, played) to location
    ONGOING = "Ongoing"
    GAME_START = "GameStart"
    END_TURN = "EndTurn"
    END_GAME = "EndGame"
    IN_HAND = "InHand"
    IN_DECK = "InDeck"
    DESTROYED = "Destroyed"
    DISCARDED = "Discarded"
    MOVED = "Moved"
    BANISHED = "Banished"
    START_TURN = "StartTurn"
    ACTIVATE = "Activate"
    BEFORE_CARD_PLAYED = "BeforeCardPlayed"  # Triggered before OnRevealGA is performed
    AFTER_CARD_PLAYED = "AfterCardPlayed"  # Triggered after OnRevealGA is performed
    AFTER_ABILITY_TRIGGERED = "AfterAbilityTriggered"
    ON_CREATED = "OnCreated"  # Triggered when the card is created
    NONE = "None"

class EffectType(Enum):
    GAIN_POWER = "GainPower"
    LOSE_POWER = "LosePower"  # Self loses power
    STEAL_POWER = "StealPower"
    AFFLICT = "Afflict"  # Decrease power of target
    DRAW = "Draw"
    DISCARD = "Discard"
    DESTROY = "Destroy"
    MOVE = "Move"
    GAIN_ENERGY = "GainEnergy"
    GAIN_MAX_ENERGY = "GainMaxEnergy"
    LOSE_ENERGY = "LoseEnergy"
    ADD_POWER_TO_LOCATION = "AddPowerToLocation"
    CREATE_CARD_IN_HAND = "CreateCardInHand"
    CREATE_CARD_IN_DECK = "CreateCardInDeck"
    CREATE_CARD_IN_LOCATION = "CreateCardInLocation"
    REMOVE_ABILITY = "RemoveAbility"
    REDUCE_COST = "ReduceCost"
    INCREASE_COST = "IncreaseCost"
    MERGE = "Merge"
    RETURN = "Return"
    ADD_CARD_TO_LOCATION = "AddCardToLocation"
    ADD_CARD_TO_HAND = "AddCardToHand"
    SET_POWER = "SetPower"
    SET_COST = "SetCost"
    COPY_AND_ACTIVATE = "CopyAndActivate"
    ADD_KEYWORD = "AddKeyword"
    ADD_TEMPORARY_ABILITY = "AddTemporaryAbility"
    
class TargetType(Enum):
    DECK = "Deck"
    HAND = "Hand"
    SELF = "Self"
    PLAYER_DIRECT_LOCATION_CARDS = "PlayerDirectLocationCards"
    ENEMY_DIRECT_LOCATION_CARDS = "EnemyDirectLocationCards"
    ALL_DIRECT_LOCATION_CARDS = "AllDirectLocationCards"
    ALL_PLAYER_CARDS = "AllPlayerCards"
    ALL_ENEMY_CARDS = "AllEnemyCards"
    ALL_BOARD_CARDS = "AllBoardCards"
    PLAYER_DIRECT_LOCATION = "PlayerDirectLocation"
    ALL_PLAYER_LOCATION = "AllPlayerLocation"
    ENEMY_DIRECT_LOCATION = "EnemyDirectLocation"
    ALL_ENEMY_LOCATION = "AllEnemyLocation"
    DIRECT_LOCATION = "DirectLocation"
    ALL_LOCATION = "AllLocation"
    ENEMY_DECK = "EnemyDeck"
    ENEMY_HAND = "EnemyHand"
    NEXT_PLAYED_CARD = "NextPlayedCard"
    TRIGGERED_ACTION_TARGETS = "TriggeredActionTargets"  # Targets that the action that triggered this ability affected
    TRIGGERED_ACTION_SOURCE = "TriggeredActionSource"  # The source card of the action that triggered this ability
    CREATED_CARD = "CreatedCard"  # Only activated when trigger is AfterAbilityTriggered and is a create card ability

class TargetRange(Enum):
    NONE = "None"
    FIRST = "First"
    LAST = "Last"
    ALL = "All"
    RANDOM = "Random"
    ALL_REQUIREMENTS_MET = "AllRequirementsMet"
    RANDOM_REQUIREMENTS_MET = "RandomRequirementsMet"

class TargetSort(Enum):
    NONE = "None"
    POWER = "Power"
    BASE_COST = "BaseCost"
    CURRENT_COST = "CurrentCost"
    PLAYED_ORDER = "PlayedOrder"
    LOCATION_ORDER = "LocationOrder"

class RequirementType(Enum):
    NONE = "None"
    POWER = "Power"
    COST = "Cost"
    NUMBER_OF_CARDS = "NumberOfCards"
    CURRENT_TURN = "CurrentTurn"
    CURRENT_MAX_ENERGY = "CurrentMaxEnergy"
    LOCATION_POWER_DIFFERENCE = "LocationPowerDifference"
    HAS_KEYWORD = "HasKeyword"
    IS_CREATED = "IsCreated"
    CARD_NAME = "CardName"  # Check for specific card names
    BUFF_PRESENT = "BuffPresent"  # Check if a specific buff is present
    LOCATION_FULL = "LocationFull"  # Check if a location is occupied

class RequirementComparator(Enum):
    NONE = "None"
    EQUAL = "Equal"
    GREATER = "Greater"
    LESS = "Less"
    GEQ = "GEQ"  # Greater than or equal to
    LEQ = "LEQ"  # Less than or equal to
    IS_HIGHEST_IN_LOCATION = "IsHighestInLocation"
    IS_MIN_IN_GROUP = "IsMinInGroup"
    NOT_EQUAL = "NotEqual"  # Check for inequality
    CONTAINS = "Contains"  # Check if a collection contains a value
    DOES_NOT_CONTAIN = "DoesNotContain"  # Check if a collection does not contain a value

class AbilityAmountType(Enum):
    NONE = "None"
    CONSTANT = "Constant"
    FOR_EACH_TARGET = "ForEachTarget"
    CARD_ID = "CardId"
    JSON = "Json"
    TARGET_VALUE = "TargetValue"
    BOOLEAN = "Boolean"
    RANDOM_CARD = "RandomCard"