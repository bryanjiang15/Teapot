# Tournament System Documentation

## Overview
The Tournament System manages competitive play between decks, handling match simulations, statistics tracking, and balance metrics calculation.

## Tournament State

### Core Structure
```cpp
struct TournamentState {
    vector<Card*> card_list;
    vector<CardRep> card_reps;
    vector<BalanceStat> card_stats;
    vector<vector<int>> all_decks;
    vector<vector<int>> active_decks;
    vector<BalanceStat> all_deck_stats;
    vector<BalanceStat> active_deck_stats;
    vector<vector<BalanceStat>> card_stats_in_all_decks;
    vector<vector<BalanceStat>> card_stats_in_active_decks;
    BalanceStat snd_player_stat;
    vector<MatchRec> rec_list;
    double** card_pair_diffs;
    vector<double> neibor_dists;
    double ave_neibor_dist;
    int match_pair_count;
    int turn_count;
};
```

## Balance Statistics

### BalanceStat Structure
```cpp
struct BalanceStat {
    int num_wins;
    int num_losses;
    int total_num;
    double effective_win_contribution;
    double draw_contribution;
    double snd_player_eff_win_contrib;
    double total_participation;
    double eval;
    int card_cost;
    double sum_weighted_num_turns;
    double cost_constrained_participation;
    double adjusted_participation;
};
```

### Stat Management
```cpp
void UpdateStatEvals(vector<BalanceStat>& stats);
void AppendBalanceStats(vector<BalanceStat>& stats, const vector<BalanceStat>& new_stats);
void SortStatInIndices(const vector<BalanceStat>& stats, vector<int>& indices);
```

## Match Records

### MatchRec Structure
```cpp
struct MatchRec {
    vector<int> deck_a_indices;
    vector<int> deck_b_indices;
    double weight;
    double win_weight;
    double win_rate;
    vector<double> sum_win_contrib_a;
    vector<double> ave_win_contrib_a;
    vector<double> sum_total_partic_a;
    vector<double> ave_total_partic_a;
    vector<double> sum_win_contrib_b;
    vector<double> ave_win_contrib_b;
    vector<double> sum_total_partic_b;
    vector<double> ave_total_partic_b;
};
```

## Tournament Operations

### Deck Management
1. Deck Creation
   - Random deck generation
   - Cost-based deck building
   - Strategy-based deck construction

2. Deck Evolution
   - Crossover operations
   - Mutation operations
   - Selection pressure

### Match Simulation
```cpp
int SimulateSingleMatchBetweenDecks(int ai_level, vector<Card*>& card_list,
    const vector<int>& deck_a_orig_indices, const vector<int>& deck_b_orig_indices,
    vector<BalanceStat>& card_stats, BalanceStat& deck_a_stat, BalanceStat& deck_b_stat,
    vector<BalanceStat>& card_stats_in_deck_a, vector<BalanceStat>& card_stats_in_deck_b,
    BalanceStat& snd_player_stat, MatchRec& rec, bool is_inverted, int deck_size);
```

## Match Simulation Workflow

### Overview
The match simulation system is the core of the tournament system, handling the execution of games between decks and collecting statistics. Here's the detailed workflow:

### 1. Match Initialization
```cpp
int SimulateSingleMatchBetweenDecks(
    int ai_level,                    // AI level for both players
    vector<Card*>& card_list,        // Complete card pool
    const vector<int>& deck_a_indices, // Deck A card indices
    const vector<int>& deck_b_indices, // Deck B card indices
    vector<BalanceStat>& card_stats, // Card performance stats
    BalanceStat& deck_a_stat,        // Deck A performance stats
    BalanceStat& deck_b_stat,        // Deck B performance stats
    vector<BalanceStat>& card_stats_in_deck_a, // Individual card stats in deck A
    vector<BalanceStat>& card_stats_in_deck_b, // Individual card stats in deck B
    BalanceStat& snd_player_stat,    // Second player advantage stats
    MatchRec& rec,                   // Match record
    bool is_inverted,                // Whether to swap player order
    int deck_size                    // Size of decks
)
```

### 2. Game Setup
1. Deck Construction
   - Create actual card instances from indices
   - Shuffle decks
   - Initialize player states

2. Player Configuration
   - Set AI levels
   - Initialize mana and health
   - Set up starting hands

### 3. Match Execution
```cpp
// Main game loop
while (!game_over) {
    // Process current player's turn
    ProcessPlayerTurn();
    
    // Check for game end conditions
    if (CheckGameEnd()) {
        game_over = true;
        break;
    }
    
    // Switch to next player
    SwitchPlayer();
}
```

### 4. Statistics Collection
1. Card Performance
```cpp
void UpdateCardStats(
    Card* card,
    double participation,    // How much the card contributed
    bool is_winner,         // Whether the card's owner won
    int num_turns          // Number of turns in the match
)
```

2. Deck Performance
```cpp
void UpdateDeckStats(
    const vector<Card*>& deck,
    bool is_winner,
    int num_turns
)
```

3. Match Records
```cpp
void UpdateMatchRecord(
    MatchRec& rec,
    const vector<double>& contribution_a,
    const vector<double>& contribution_b,
    bool is_draw
)
```

### 5. Balance Metrics Calculation

#### Symmetry Score
```cpp
double CalculateSymmetryScore(
    const BalanceStat& first_player_stats,
    const BalanceStat& second_player_stats
)
```
- Measures win rate difference between first and second player
- Considers draw rates
- Evaluates play order impact

#### Strength Score
```cpp
double CalculateStrengthScore(
    const vector<BalanceStat>& card_stats,
    int cost_bracket
)
```
- Evaluates card power level
- Considers cost efficiency
- Measures win contribution

#### Coverage Score
```cpp
double CalculateCoverageScore(
    const vector<BalanceStat>& card_stats,
    const vector<vector<int>>& active_decks
)
```
- Tracks card usage in active decks
- Measures deck diversity
- Evaluates card accessibility

### 6. Evolution Process

#### Deck Selection
```cpp
void SelectDecks(
    vector<vector<int>>& selected_decks,
    const vector<BalanceStat>& deck_stats,
    int num_decks
)
```
- Selects decks based on performance
- Applies selection pressure
- Maintains diversity

#### Crossover Operation
```cpp
void PerformCrossover(
    const vector<int>& parent_a,
    const vector<int>& parent_b,
    vector<int>& child
)
```
- Combines cards from two parent decks
- Maintains deck size constraints
- Preserves card balance

#### Mutation Operation
```cpp
void PerformMutation(
    vector<int>& deck,
    const vector<Card*>& card_pool,
    double mutation_rate
)
```
- Randomly replaces cards
- Maintains deck constraints
- Explores new combinations

### 7. Data Management

#### Match Record Storage
```cpp
void WriteMatchRecords(
    const vector<MatchRec>& recs,
    int deck_size,
    const char* filename
)
```
- Saves match results
- Records card contributions
- Tracks win rates

#### Statistics Analysis
```cpp
void AnalyzeTournamentResults(
    const TournamentState& state,
    const char* output_file
)
```
- Generates performance reports
- Calculates balance metrics
- Identifies trends

### Implementation Notes

1. Performance Considerations
   - Use efficient data structures for card lookup
   - Optimize memory usage during simulations
   - Implement parallel processing for multiple matches

2. Balance Considerations
   - Monitor win rates across different deck types
   - Track card usage patterns
   - Adjust evolution parameters based on results

3. Error Handling
   - Validate deck configurations
   - Handle edge cases in match simulation
   - Implement proper cleanup procedures

### Example Usage

```cpp
// Initialize tournament state
TournamentState state;
state.card_list = LoadCardPool();
state.deck_size = 30;

// Run evolution simulation
EvolutionSimulation(state, 100, 30);  // 100 decks, size 30

// Analyze results
AnalyzeTournamentResults(state, "tournament_results.txt");
```

## Balance Metrics

### Symmetry Score
- Measures game balance between first and second player
- Considers win rates and draw rates
- Evaluates play order impact

### Strength Score
- Evaluates individual card power levels
- Considers cost efficiency
- Measures impact on game outcomes

### Coverage Score
- Tracks card usage in active decks
- Measures deck diversity
- Evaluates card accessibility

### Diversity Score
- Measures card uniqueness
- Evaluates deck variety
- Considers strategic diversity

### Interaction Score
- Measures card synergies
- Evaluates combo potential
- Tracks interactive gameplay

## Tournament Modes

### Evolution Simulation
```cpp
void EvolutionSimulation(TournamentState& tournmnt_state, int deck_pool_size, int deck_size);
```

### Testing Modes
1. New Deck Testing
```cpp
void TestNewDeck(int ai_level, TournamentState& tournmnt_state, int deck_size, double temperature, int num_pair_matches);
```

2. Crossover Testing
```cpp
void TestCrossOver(int ai_level, TournamentState& tournmnt_state, int deck_size, double temperature, int num_pair_matches);
```

3. Mutation Testing
```cpp
void TestMutation(int ai_level, TournamentState& tournmnt_state, int deck_size, double temperature, int num_pair_matches);
```

## Data Management

### File Operations
1. Card Data
```cpp
void WriteCardData(vector<Card*>& cards, const vector<CardRep>& card_reps, const vector<BalanceStat>& card_stats, const char* filename);
void ReadCardData(vector<Card*>& cards, vector<CardRep>& card_reps, vector<BalanceStat>& card_stats, const char* filename);
```

2. Deck Data
```cpp
void WriteDeckData(const vector<vector<int>>& deck_list, const vector<BalanceStat>& deck_stats, const char* filename);
void ReadDeckData(vector<vector<int>>& deck_list, vector<BalanceStat>& deck_stats, const char* filename);
```

3. Match Records
```cpp
void WriteMatchRecords(const vector<MatchRec>& recs, int deck_size, const char* filename);
void ReadMatchRecords(vector<MatchRec>& recs, int deck_size, const char* filename);
```

## Development Notes

### Best Practices
1. Tournament Design
   - Balance between exploration and exploitation
   - Proper statistical analysis
   - Meaningful metric collection

2. Implementation
   - Efficient data structures
   - Proper memory management
   - Robust error handling

### Common Issues
1. Balance
   - Power level disparities
   - Strategy dominance
   - Meta stagnation

2. Performance
   - Simulation speed
   - Memory usage
   - Data management

### Future Improvements
1. Algorithm Enhancements
   - Advanced evolution strategies
   - Better balance metrics
   - Improved deck generation

2. Analysis Tools
   - Better visualization
   - More detailed statistics
   - Advanced pattern recognition

3. Tournament Features
   - More game modes
   - Better matchmaking
   - Enhanced reporting 