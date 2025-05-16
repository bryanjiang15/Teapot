# ChaosCards Documentation

## Overview
ChaosCards is a card game engine that implements a collectible card game system with features for card generation, deck building, AI opponents, and game simulation. The project is written in C++ and provides a framework for creating and testing card game mechanics.

## Core Components

### 1. Card System
The card system is the fundamental building block of the game, implemented through several key structures:

#### NodeRep
- Represents the basic structure of a card
- Contains:
  - `choice`: An unsigned integer representing card type/attributes
  - `term_info`: A vector of doubles containing card parameters
- Used for card generation and comparison

#### Card Types
- Leader Cards (Heroes)
- Minion Cards
- Spell Cards

#### Card Properties
- Cost
- Attack
- Health
- Attack Times
- Minion Types (Beast, Dragon, Demon)
- Abilities (Charge, Taunt, Stealth, Untargetable, Shielded, Poisonous, Lifesteal)

### 2. Player System
The `Player` class manages the game state for each player:

#### Key Components
- Leader card
- Field (battlefield)
- Hand
- Deck
- Mana system
- Event queue

#### Player States
- Health Points (HP)
- Mana Points (MP)
- Maximum Mana
- Turn number
- Fatigue counter

#### Player Actions
- Card drawing
- Card playing
- Attacking
- Mana management
- Event processing

### 3. Game Mechanics

#### Card Positions
```cpp
#define CARD_POS_AT_LEADER 1
#define CARD_POS_AT_FIELD 2
#define CARD_POS_AT_HAND 3
#define CARD_POS_AT_DECK 4
#define CARD_POS_UNKNOWN 5
```

#### Game Constants
```cpp
#define INIT_HAND_SIZE 3
#define MAX_FIELD_SIZE 7
#define MAX_MP 10
#define MAX_HAND_SIZE 10
#define MAX_NUM_TURNS 30
```

#### Target System
The game implements a sophisticated targeting system using bit flags for:
- Card positions
- Card types
- Allegiance (Ally/Opponent)
- Minion types
- Abilities
- Special conditions

### 4. AI System
The game includes multiple AI levels:
- Random AI (level 0)
- Search-based AI (levels 1-9)
- Heuristic evaluation system
- Action simulation and testing

### 5. Tournament System
The `TournamentState` class manages tournament simulations:

#### Features
- Card pool management
- Deck building
- Match simulation
- Statistics tracking
- Balance metrics

#### Balance Metrics
- Symmetry score
- Strength score
- Coverage score
- Diversity score
- Interaction score

### 6. Card Generation
The system includes multiple methods for card generation:
- Random generation
- Cost-based generation
- Named card generation
- Card set generation
- Demo card sets

## Main Workflow

### 1. Game Initialization
1. Load or generate card pool
2. Initialize players
3. Set up decks
4. Determine play order

### 2. Game Loop
1. Start turn
2. Process events
3. Player actions
4. End turn
5. Check game end conditions

### 3. Tournament Mode
1. Initialize tournament state
2. Generate/load card pool
3. Run matches
4. Collect statistics
5. Update balance metrics

## File Structure

### Core Files
- `main.cpp`: Main game logic and tournament system
- `Player.h/cpp`: Player class implementation
- `DataUtil.h/cpp`: Utility functions and data structures
- `card.generated.h`: Generated card definitions
- `card.xc`: Card generation rules

### Demo Files
- Various demo card set files
- Tournament data files
- HTML output files

## Usage

### Building Decks
1. Select cards from the card pool
2. Ensure deck size requirements are met
3. Validate deck composition

### Running Matches
1. Initialize players with decks
2. Set AI levels if using AI
3. Run match simulation
4. Process results

### Tournament Mode
1. Set up tournament parameters
2. Initialize card pool
3. Run tournament simulation
4. Analyze results and balance metrics

## Development Notes

### Card Generation
The system uses a sophisticated card generation system that can:
- Generate random cards
- Create cards with specific costs
- Generate named cards
- Create balanced card sets

### Balance System
The balance system evaluates cards and decks based on:
- Win rates
- Card usage
- Deck diversity
- Player symmetry
- Card interactions

### AI Implementation
The AI system uses:
- Heuristic evaluation
- Action simulation
- Tree search algorithms
- Multiple difficulty levels

## Future Improvements
1. Enhanced card generation algorithms
2. More sophisticated AI strategies
3. Additional card types and mechanics
4. Improved balance metrics
5. Extended tournament features 