# Card System Documentation

## Overview
The Card System is the fundamental building block of ChaosCards, handling all aspects of card representation, types, properties, and interactions.

## Card Structure

### NodeRep
The `NodeRep` structure is the core representation of a card in the system:

```cpp
struct NodeRep {
    unsigned choice;           // Card type and attributes
    std::vector<double> term_info;  // Card parameters
};
```

#### Usage
- Used for card generation and comparison
- Stores card attributes in a compact format
- Enables efficient card state tracking

## Card Types

### 1. Leader Cards (Heroes)
- Represent the player's avatar
- Have higher health points
- Can attack and be targeted
- Special abilities and effects

### 2. Minion Cards
- Played to the battlefield
- Can attack and be attacked
- Various minion types:
  - Beast
  - Dragon
  - Demon
- Can have multiple abilities

### 3. Spell Cards
- One-time effects
- Various targeting options
- Different effect types:
  - Damage
  - Healing
  - Buff/Debuff
  - Special effects

## Card Properties

### Basic Properties
- Cost: Mana cost to play
- Attack: Damage dealt
- Health: Damage capacity
- Attack Times: Number of attacks per turn

### Minion Types
```cpp
#define NONE_MINION 0
#define BEAST_MINION 1
#define DRAGON_MINION 2
#define DEMON_MINION 3
```

### Abilities
```cpp
// Ability Flags
#define TARGET_IS_CHARGE 0x800u
#define TARGET_IS_TAUNT 0x1000u
#define TARGET_IS_STEALTH 0x2000u
#define TARGET_IS_UNTARGETABLE 0x4000u
#define TARGET_IS_SHIELDED 0x8000u
#define TARGET_IS_POISONOUS 0x10000u
#define TARGET_IS_LIFESTEAL 0x20000u
```

#### Ability Descriptions
1. Charge: Can attack immediately when played
2. Taunt: Must be attacked before other targets
3. Stealth: Cannot be targeted until it attacks
4. Untargetable: Cannot be targeted by spells or abilities
5. Shielded: Immune to one instance of damage
6. Poisonous: Destroys any target it damages
7. Lifesteal: Heals the player for damage dealt

## Card Generation

### Methods
1. Random Generation
   - Uses seed-based generation
   - Ensures balanced card distribution
   - Considers cost curves

2. Cost-Based Generation
   - Generates cards with specific mana costs
   - Maintains balance within cost brackets
   - Adjusts power level based on cost

3. Named Card Generation
   - Creates cards with specific names
   - Allows for custom card creation
   - Useful for testing and development

### Card Set Generation
```cpp
std::vector<Card*> GenerateCardSet(int n, int seed);
std::vector<Card*> GenerateInitCardSet(int n, int seed);
```

## Card Interactions

### Targeting System
The game uses a sophisticated bit-flag system for targeting:
```cpp
#define TARGET_TYPE_NOTHING 0u
#define TARGET_TYPE_ANY 0xFFFFFFFFu
#define TARGET_POS_FIELD 0x1u
#define TARGET_POS_HAND 0x2u
#define TARGET_POS_DECK 0x4u
```

### Effect System
1. Battlecry Effects
   - Trigger when card is played
   - Can target specific entities
   - One-time effects

2. Deathrattle Effects
   - Trigger when card is destroyed
   - Can have lasting impact
   - Often used for card generation

3. Turn Effects
   - Trigger at start/end of turn
   - Can be persistent
   - Often used for buffs/debuffs

## Card State Management

### Position Tracking
```cpp
#define CARD_POS_AT_LEADER 1
#define CARD_POS_AT_FIELD 2
#define CARD_POS_AT_HAND 3
#define CARD_POS_AT_DECK 4
#define CARD_POS_UNKNOWN 5
```

### State Changes
1. Card Movement
   - Hand to Field
   - Deck to Hand
   - Field to Graveyard
   - Deck to Deck (shuffling)

2. Stat Modifications
   - Attack changes
   - Health changes
   - Ability additions/removals
   - Cost modifications

## Card Comparison and Analysis

### Card Representation
```cpp
double DiffCardRep(CardRep& rep_a, CardRep& rep_b);
```

### Balance Metrics
1. Power Level
   - Cost efficiency
   - Stat distribution
   - Ability impact

2. Synergy Potential
   - Card combinations
   - Deck building potential
   - Strategy formation

## Development Notes

### Best Practices
1. Card Design
   - Balance cost and effects
   - Consider interaction potential
   - Maintain game balance

2. Implementation
   - Use efficient data structures
   - Implement proper state tracking
   - Handle edge cases

### Common Issues
1. State Management
   - Tracking card positions
   - Handling effects
   - Managing interactions

2. Balance Considerations
   - Power level assessment
   - Synergy evaluation
   - Meta impact analysis 