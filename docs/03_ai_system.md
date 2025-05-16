# AI System Documentation

## Overview
The AI System in ChaosCards implements both random and search-based AI opponents with varying levels of intelligence and strategic depth.

## AI Levels

### Level Structure
```cpp
int ai_level;  // 0: Random AI, 1-9: Search-based AI
```

### Level Characteristics
1. Level 0 (Random AI)
   - Makes completely random moves
   - No strategic planning
   - Used for testing and baseline performance

2. Levels 1-9 (Search-based AI)
   - Increasing search depth
   - More sophisticated evaluation
   - Better strategic planning
   - Higher levels = more computational resources

## AI Components

### Action Generation
```cpp
std::vector<ActionSetEntity*> GetOptionSet() const;
std::vector<ActionEntity*> GetActionList() const;
```

### Action Types
1. Card Play Actions
   - Playing cards from hand
   - Targeting decisions
   - Position selection

2. Attack Actions
   - Attacker selection
   - Target selection
   - Attack order optimization

3. Special Actions
   - Hero power usage
   - Special ability activation
   - End turn decision

## Search Algorithm

### Tree Search
1. State Representation
   - Current game state
   - Available actions
   - Opponent's possible responses

2. Search Parameters
   - Search depth
   - Branching factor
   - Time constraints

### Evaluation Function
```cpp
double GetHeuristicEval() const;
double ForwardToNextTurnAndEval();
double GetHeuristicAdjustment(int turn_num_adjust) const;
```

#### Evaluation Factors
1. Board State
   - Card advantage
   - Health totals
   - Mana efficiency

2. Strategic Position
   - Card quality
   - Hand size
   - Deck remaining

3. Win Conditions
   - Lethal detection
   - Survival probability
   - Resource management

## AI Decision Making

### Action Selection
```cpp
void TakeSearchAIInputs();
void TakeSearchAIInput();
void TakeRandomAIInputs();
void TakeRandomAIInput();
```

### Decision Process
1. State Analysis
   - Evaluate current position
   - Identify key threats
   - Plan future turns

2. Action Planning
   - Generate possible moves
   - Evaluate outcomes
   - Select optimal action

3. Execution
   - Perform selected action
   - Update game state
   - Prepare for next decision

## Performance Optimization

### Search Optimization
1. Alpha-Beta Pruning
   - Reduce search space
   - Maintain optimal play
   - Improve performance

2. Move Ordering
   - Prioritize promising moves
   - Reduce branching factor
   - Speed up search

3. Transposition Tables
   - Cache evaluated positions
   - Avoid redundant calculations
   - Improve efficiency

### Memory Management
1. State Representation
   - Efficient data structures
   - Minimal memory usage
   - Quick state copying

2. Search Space
   - Depth control
   - Branch limiting
   - Memory constraints

## AI Testing

### Performance Metrics
1. Win Rate
   - Against different AI levels
   - Against human players
   - In tournament settings

2. Decision Quality
   - Move optimality
   - Strategic planning
   - Resource management

3. Computational Efficiency
   - Time per decision
   - Memory usage
   - Search depth achieved

### Testing Methods
1. Self-Play
   - AI vs AI matches
   - Performance comparison
   - Strategy evolution

2. Human Testing
   - Player feedback
   - Strategy validation
   - Balance assessment

## Development Notes

### Best Practices
1. AI Design
   - Balance intelligence and performance
   - Consider multiple strategies
   - Implement proper evaluation

2. Code Organization
   - Modular design
   - Clear interfaces
   - Efficient algorithms

### Common Issues
1. Performance
   - Search space explosion
   - Memory constraints
   - Time limitations

2. Strategy
   - Local optima
   - Predictable patterns
   - Resource management

### Future Improvements
1. Algorithm Enhancements
   - Machine learning integration
   - Advanced search techniques
   - Better evaluation functions

2. Performance Optimization
   - Parallel processing
   - Better state representation
   - Improved pruning

3. Strategy Development
   - More sophisticated planning
   - Better resource management
   - Advanced threat assessment 