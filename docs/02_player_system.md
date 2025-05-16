# Player System Documentation

## Overview
The Player System manages the game state for each player, handling card management, turn structure, and player actions.

## Player Class Structure

### Core Components
```cpp
class Player {
    Card* leader;                    // Player's hero card
    std::vector<Card*> field;        // Battlefield
    std::vector<Card*> hand;         // Cards in hand
    std::vector<Card*> deck;         // Cards in deck
    std::queue<DeferredEvent*>& event_queue;  // Event processing queue
    Player* opponent;                // Reference to opponent
    // ... other members
};
```

### Player States
```cpp
// Game State
bool is_lost;           // Player has lost
bool is_turn_active;    // Player's turn is active
int turn_num;          // Current turn number
int max_mp;            // Maximum mana points
int mp_loss;           // Mana points lost
int fatigue;           // Fatigue damage counter

// Size Tracking
int field_size_adjust;  // Field size discrepancy
int hand_size_adjust;   // Hand size discrepancy
int deck_size_adjust;   // Deck size discrepancy
```

## Game Constants

### Size Limits
```cpp
#define INIT_HAND_SIZE 3
#define MAX_FIELD_SIZE 7
#define MAX_MP 10
#define MAX_HAND_SIZE 10
#define MAX_NUM_TURNS 30
```

## Player Actions

### Card Management
1. Drawing Cards
```cpp
void DrawCard(bool start_of_batch);
void InitialCardDraw(bool is_second_player);
```

2. Playing Cards
```cpp
bool CheckPlayValid(int x, int y, int& z) const;
void Play(int x, int y, int z);
```

3. Attacking
```cpp
bool CheckAttackValid(int x, int z) const;
void Attack(int x, int z);
```

### Mana Management
```cpp
bool CheckMP(int cost) const;
void UseMP(int cost);
void ModifyMp(int amount);
void ModifyMaxMp(int amount);
```

### Turn Structure
```cpp
void StartTurn();
void EndTurn();
void RecoverAttackTimes();
```

## Event System

### Deferred Events
The game uses a deferred event system to handle complex interactions:

1. Event Types
- Card destruction
- Spell casting
- Field discards
- Hand discards
- Deck discards
- Field summons
- Card transformations
- State resets

2. Event Processing
```cpp
bool ProcessDeferredEvents();
bool CleanUp();
void ClearCorpse();
```

## AI Integration

### AI Levels
```cpp
int ai_level;  // 0: Random AI, 1-9: Search-based AI
```

### AI Actions
```cpp
void TakeSearchAIInputs();
void TakeSearchAIInput();
void TakeRandomAIInputs();
void TakeRandomAIInput();
```

### AI Evaluation
```cpp
double GetHeuristicEval() const;
double ForwardToNextTurnAndEval();
double GetHeuristicAdjustment(int turn_num_adjust) const;
```

## Player Information

### Display Functions
```cpp
void DisplayHelp() const;
void Query(int x) const;
std::string BriefInfo() const;
std::string DetailInfo() const;
void PrintBoard() const;
```

### Size Queries
```cpp
int GetActualFieldSize() const;
int GetActualHandSize() const;
int GetActualDeckSize() const;
```

## Target System

### Target Validation
```cpp
bool IsValidTarget(int z) const;
bool IsValidCharTarget(int z) const;
bool IsValidMinionTarget(int z) const;
bool IsValidCardTarget(int z) const;
bool IsTargetAlly(int z) const;
bool IsTargetOpponent(int z) const;
```

### Target Management
```cpp
Card* GetTargetCard(int z) const;
Card* ExtractTargetCard(int z);
```

## Card Movement

### Field Management
```cpp
void SummonToField(Card* card);
void FlagFieldSummon(Card* card, bool start_of_batch);
```

### Hand Management
```cpp
void PutToHand(Card* card);
void FlagHandPut(Card* card, bool start_of_batch);
```

### Deck Management
```cpp
void ShuffleToDeck(Card* card);
void FlagDeckShuffle(Card* card, bool start_of_batch);
```

## Development Notes

### Best Practices
1. State Management
   - Keep track of all card positions
   - Maintain proper event ordering
   - Handle edge cases in card movement

2. AI Implementation
   - Balance between performance and intelligence
   - Consider multiple strategies
   - Implement proper evaluation functions

### Common Issues
1. Event Processing
   - Order of operations
   - State consistency
   - Edge case handling

2. Resource Management
   - Memory allocation
   - Card ownership
   - Event cleanup

### Performance Considerations
1. Card Search
   - Efficient target validation
   - Quick card lookup
   - Optimized state tracking

2. AI Performance
   - Search depth control
   - Evaluation function efficiency
   - Memory usage optimization 