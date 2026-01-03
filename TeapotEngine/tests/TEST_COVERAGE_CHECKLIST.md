# TeapotEngine Test Coverage Checklist

This document tracks test coverage for the TeapotEngine codebase. Use this checklist to identify gaps in testing and ensure comprehensive test coverage.

**Last Updated:** January 2, 2026

---

## Legend
- ✅ Tested (test exists and covers this functionality)
- ⚠️ Partially Tested (some coverage, but missing edge cases)
- ❌ Not Tested (no test coverage)
- 🔧 Needs Refactoring (test exists but may be outdated)

---

## Core Module (`TeapotEngine/core/`)

### 1. Component.py
**Test File:** `test_component.py`

#### Component Class
| Feature | Status | Notes |
|---------|--------|-------|
| `__init__` / creation | ✅ | Basic creation tested |
| `add_trigger` | ✅ | Single trigger add tested |
| `is_active` | ✅ | Tests ACTIVE, INACTIVE, DESTROYED states |
| `set_zone` | ✅ | Basic zone set tested |
| `set_controller` | ✅ | Basic controller set tested |
| `update_metadata` / `get_metadata` | ✅ | Basic operations tested |
| `add_resource_instance` | ✅ | Basic add tested |
| `get_resource_instances` | ✅ | Multiple instances tested |
| `get_resource_by_instance` | ✅ | Basic retrieval tested |
| `gain_resource` | ❌ | Not tested |
| `spend_resource` | ❌ | Not tested |
| `get_current_workflow_node` | ❌ | Not tested |
| Workflow integration | ❌ | Component + WorkflowState not tested |
| ComponentStatus transitions | ⚠️ | Only basic states tested |

#### ComponentManager Class
| Feature | Status | Notes |
|---------|--------|-------|
| `create_component` | ✅ | With zone/controller tested |
| `get_component` | ✅ | Including nonexistent |
| `remove_component` | ✅ | Including nonexistent |
| `get_components_by_type` | ✅ | Basic functionality |
| `get_component_by_type_and_id` | ✅ | Basic functionality |
| `get_components_by_zone` | ✅ | Multiple components |
| `get_components_by_controller` | ✅ | Multiple components |
| `move_component` | ✅ | Including controller change |
| `get_all_components` | ✅ | Basic functionality |
| ID auto-increment | ✅ | Verified sequential IDs |

**Missing Tests:**
- [ ] Component with workflow state integration
- [ ] Resource operations (gain/spend) with limits
- [ ] Concurrent component modifications
- [ ] Component cloning/copying

---

### 2. MatchActor.py
**Test File:** `test_match_actor.py`

| Feature | Status | Notes |
|---------|--------|-------|
| `__init__` | ✅ | Basic creation with seed |
| `begin_game` | ✅ | Basic game start |
| `process_action` | ✅ | Valid and invalid actions |
| `advance_phase` | ✅ | Basic phase advancement |
| `end_turn` | ✅ | Basic turn end |
| `get_current_state` | ✅ | State serialization |
| `get_available_actions` | ✅ | Basic retrieval |
| `get_actions_for_object` | ✅ | Object-specific actions |
| `submit_input` | ✅ | Valid and invalid input |
| `_resolve_stack` | ⚠️ | Only indirectly tested |
| `_resolve_event` | ⚠️ | Only indirectly tested |
| `_resolve_reaction` | ❌ | Not directly tested |
| `_check_state_based_actions` | ❌ | Not tested |
| `discover_reactions` | ❌ | Not directly tested |
| `register_component_triggers` | ❌ | Not tested |
| `unregister_component_triggers` | ❌ | Not tested |
| `register_system_triggers` | ❌ | Not tested |
| `run_until_blocked` | ⚠️ | Indirectly via begin_game |
| Max recursion depth | ✅ | Tests RecursionError |
| Pre/Post reaction ordering | ❌ | Not tested |
| Action cost payment | ❌ | Not tested |

**Missing Tests:**
- [ ] Complex trigger chains
- [ ] Pre-reaction and post-reaction ordering
- [ ] State-based actions triggering
- [ ] Multi-player turn rotation
- [ ] Action costs and preconditions
- [ ] Workflow executor integration
- [ ] Component initialization from ruleset
- [ ] Event ordering and priorities

---

### 3. GameState.py
**Test File:** `test_state.py`

| Feature | Status | Notes |
|---------|--------|-------|
| `from_ruleset` | ✅ | Basic creation |
| `allocate_resource_instance_id` | ✅ | Sequential IDs |
| `create_component` | ✅ | With definition |
| `get_component` | ✅ | By ID |
| `remove_component` | ✅ | Basic removal |
| `get_components_by_type` | ✅ | Type filtering |
| `get_game_component_instance` | ⚠️ | Basic test (may need MatchActor) |
| `get_components_by_zone` | ⚠️ | Zone is component ID now |
| `get_components_by_controller` | ✅ | Controller filtering |
| `move_component` | ✅ | Zone movement |
| `apply_event` (PhaseStarted) | ✅ | Event log tested |
| `apply_event` (PhaseEnded) | ✅ | Event log tested |
| `apply_event` (TurnEnded) | ✅ | Event log tested |
| `apply_event` (CardMoved) | ✅ | Legacy zones |
| `apply_event` (ResourceChanged) | ✅ | Resource definition |
| `current_phase` property | ✅ | Getter tested |
| `turn_number` property | ✅ | Getter/setter tested |
| `get_player` | ⚠️ | Basic test exists |
| `find_resource_instance` | ✅ | Component + resource def |
| `gain_resource_instance` | ❌ | Not tested |
| `spend_resource_instance` | ❌ | Not tested |
| `find_zone_component_by_name` | ❌ | Not tested |
| `to_dict` | ❌ | Not tested |
| `from_events` (event sourcing) | ❌ | Not tested |
| `_deal_damage` | ❌ | Not tested |
| `get_card_location` | ❌ | Not tested |
| `get_player_zone` | ❌ | Not tested |

**Missing Tests:**
- [ ] Full event sourcing (from_events)
- [ ] State serialization/deserialization
- [ ] Zone-based queries with component IDs
- [ ] Resource instance gain/spend
- [ ] Damage tracking
- [ ] Card location tracking

---

### 4. Events.py
**Test File:** `test_events.py`

| Feature | Status | Notes |
|---------|--------|-------|
| Event creation | ✅ | Basic and with ID/order |
| Event `to_dict` | ✅ | Serialization |
| Event `from_dict` | ✅ | Deserialization |
| EventStatus enum | ✅ | Via Event tests |
| Reaction creation | ✅ | Basic with caused_by |
| Reaction `to_dict` | ✅ | Serialization |
| Reaction `from_dict` | ✅ | Deserialization |
| StackItem creation | ✅ | EVENT and REACTION types |
| StackItem `to_dict` | ✅ | Serialization |
| StackItem `from_dict` | ✅ | Deserialization |
| PendingInput creation | ✅ | With/without expiry |
| PendingInput `to_dict` | ✅ | Serialization |
| PendingInput `from_dict` | ✅ | Deserialization |

**Missing Tests:**
- [ ] All EventStatus transitions
- [ ] StackItemType edge cases

---

### 5. EventBus.py
**Test File:** `test_eventBus.py`

| Feature | Status | Notes |
|---------|--------|-------|
| `subscribe` | ✅ | Single and multiple |
| `unsubscribe` | ✅ | Including nonexistent |
| `unsubscribe_all_from_component` | ✅ | Component cleanup |
| `get_subscriptions_for_component` | ✅ | Component filtering |
| `get_all_subscriptions` | ✅ | Full listing |
| `dispatch` (matching event) | ✅ | With filters |
| `dispatch` (non-matching) | ✅ | Filter mismatch |
| `dispatch` (wildcard) | ✅ | "*" event type |
| Subscription ID auto-increment | ✅ | Sequential IDs |

**Missing Tests:**
- [ ] Complex filter conditions
- [ ] Priority-based trigger ordering
- [ ] Component status checking during dispatch

---

### 6. EventRegistry.py
**Test File:** `test_registry.py`

| Feature | Status | Notes |
|---------|--------|-------|
| EventRegistry creation | ✅ | Empty registry |
| EventRegistry `register` | ✅ | ID assignment |
| EventRegistry `get` | ✅ | Including nonexistent |
| EventRegistry `unregister` | ✅ | Including nonexistent |
| EventRegistry `clear` | ✅ | Full clear |
| ReactionRegistry creation | ✅ | Empty registry |
| ReactionRegistry `register` | ✅ | ID assignment |
| ReactionRegistry `get` | ✅ | Including nonexistent |
| ReactionRegistry `unregister` | ✅ | Including nonexistent |
| ReactionRegistry `clear` | ✅ | Full clear |

---

### 7. Stack.py
**Test File:** `test_stack.py`

| Feature | Status | Notes |
|---------|--------|-------|
| Stack creation | ✅ | Empty stack |
| `push` | ✅ | Single item |
| `pop` | ✅ | Including empty stack |
| `peek` | ✅ | Including empty stack |
| LIFO ordering | ✅ | Multiple items |
| `push_multiple` | ✅ | Batch push |
| `get_next_order` | ✅ | Sequential ordering |
| `clear` | ✅ | Full clear |
| Mixed item types | ✅ | EVENT and REACTION |
| `to_dict` | ✅ | Serialization |
| `from_dict` | ✅ | Deserialization |

---

### 8. Interpreter.py
**Test File:** `test_interpreter.py`

| Feature | Status | Notes |
|---------|--------|-------|
| RuleExecutor creation | ✅ | Basic creation |
| `execute_rule` | ✅ | With effects |
| `execute_rule` (nonexistent) | ✅ | Returns empty list |
| `execute_rule` (nested) | ✅ | Recursive rule execution |
| RulesetInterpreter creation | ✅ | Basic creation |
| `get_available_actions` | ✅ | Player filtering |
| `validate_action` | ✅ | Valid and invalid |
| `get_phase_steps` | ✅ | Phase steps retrieval |
| `get_actions_for_object` | ✅ | Object-specific |
| Precondition evaluation | ❌ | Not tested |
| Cost validation | ❌ | Not tested |
| Target selection validation | ❌ | Not tested |

**Missing Tests:**
- [ ] Complex precondition evaluation
- [ ] Action cost checking
- [ ] Target selector validation
- [ ] Phase-based action filtering

---

### 9. EffectInterpreter.py
**Test File:** ❌ **NO TEST FILE**

| Feature | Status | Notes |
|---------|--------|-------|
| `process_effects` | ❌ | Not tested |
| `_process_execute_rule` | ❌ | Not tested |
| `_process_emit_event` | ❌ | Not tested |
| `_process_sequence` | ❌ | Not tested |
| `_process_if` | ❌ | Not tested |
| `_process_for_each` | ❌ | Not tested |
| `_process_modify_state` | ❌ | Not tested |
| `_process_legacy_effect` | ❌ | Not tested |
| `_create_eval_context` | ❌ | Not tested |

**Required Tests:**
- [ ] Create `test_effect_interpreter.py`
- [ ] Test each effect kind (execute_rule, emit_event, sequence, if, for_each, modify_state)
- [ ] Test legacy effect compatibility
- [ ] Test evaluation context creation
- [ ] Test conditional execution (if/else)
- [ ] Test iteration (for_each)

---

### 10. WorkflowExecutor.py
**Test File:** ❌ **NO TEST FILE**

| Feature | Status | Notes |
|---------|--------|-------|
| `get_valid_transitions` | ❌ | Not tested |
| `_evaluate_edge_condition` | ❌ | Not tested |
| `transition_to_node` | ❌ | Not tested |
| `initialize_workflow` | ❌ | Not tested |
| `enter_workflow` | ❌ | Not tested |
| `exit_workflow` | ❌ | Not tested |
| `get_current_node` | ❌ | Not tested |
| `can_exit_workflow` | ❌ | Not tested |
| `advance_workflow` | ❌ | Not tested |
| `step_workflow` | ❌ | Not tested |
| `_advance_to_next` | ❌ | Not tested |
| `_execute_procedure` | ❌ | Not tested |
| StepResult enum | ❌ | Not tested |

**Required Tests:**
- [ ] Create `test_workflow_executor.py`
- [ ] Test workflow initialization
- [ ] Test valid transitions with/without conditions
- [ ] Test node transitions
- [ ] Test workflow stepping (ADVANCED, BLOCKED, ENDED)
- [ ] Test procedure execution
- [ ] Test nested workflows (Game → Turn → Phase)

---

### 11. PhaseManager.py
**Test File:** `test_phase_manager.py`

| Feature | Status | Notes |
|---------|--------|-------|
| TurnType enum values | ✅ | SINGLE_PLAYER, SYNCHRONOUS |
| TurnType from string | ✅ | String conversion |
| TurnType iteration | ✅ | All values accessible |

**Note:** PhaseManager class was removed. Turn/phase state is now in GameState.

---

### 12. StateWatcherEngine.py
**Test File:** `test_state_watcher.py`

| Feature | Status | Notes |
|---------|--------|-------|
| Engine creation | ✅ | Empty engine |
| `register_watcher` | ✅ | Single and multiple |
| `unregister_watchers_from_source` | ✅ | Including nonexistent |
| `mark_dirty` | ✅ | Dirty flag |
| `check_watchers` (not dirty) | ✅ | Returns empty |
| `check_watchers` (clears dirty) | ✅ | Flag reset |
| `check_watchers` (no condition) | ✅ | No trigger |
| `get_watchers_for_component` | ✅ | Including nonexistent |
| `clear` | ✅ | Full clear |
| TriggerType enum | ✅ | EVENT, STATE_BASED |
| TriggerDefinition with trigger_type | ✅ | Serialization |
| Condition evaluation | ❌ | Not tested |

**Missing Tests:**
- [ ] State-based condition evaluation
- [ ] Multiple watchers triggering
- [ ] Priority ordering (when implemented)

---

### 13. rng.py
**Test File:** `test_rng.py`

| Feature | Status | Notes |
|---------|--------|-------|
| Creation with seed | ✅ | Seed stored |
| `random` | ✅ | Float 0-1 |
| Deterministic `random` | ✅ | Same seed = same values |
| `randint` | ✅ | Integer in range |
| Deterministic `randint` | ✅ | Same seed = same values |
| `choice` | ✅ | Selects from sequence |
| Deterministic `choice` | ✅ | Same seed = same values |
| `shuffle` | ✅ | In-place modification |
| Deterministic `shuffle` | ✅ | Same seed = same order |
| `sample` | ✅ | k unique elements |
| Deterministic `sample` | ✅ | Same seed = same sample |
| `getstate` / `setstate` | ✅ | State preservation |
| `reseed` | ✅ | Seed change |
| Different seeds | ✅ | Different sequences |

---

### 14. Engine.py
**Test File:** `test_engine.py`

| Feature | Status | Notes |
|---------|--------|-------|
| GameEngine creation | ✅ | Via fixture |
| `create_match` | ✅ | Basic creation |
| `get_match` | ✅ | Including nonexistent |
| `remove_match` | ✅ | Basic removal |
| `list_matches` | ✅ | Empty and populated |
| `process_action` | ✅ | Including nonexistent match |
| `get_match_state` | ✅ | Including nonexistent |
| `get_available_actions` | ✅ | Including nonexistent |
| `get_actions_for_object` | ⚠️ | Basic test |
| Duplicate match creation | ✅ | Raises ValueError |

---

### 15. GameLoopResult.py
**Test File:** ❌ **NO TEST FILE**

| Feature | Status | Notes |
|---------|--------|-------|
| Enum values | ❌ | Not tested |

**Note:** Simple enum, may not need dedicated tests.

---

## Ruleset Module (`TeapotEngine/ruleset/`)

### 1. IR.py (RulesetIR)
**Test File:** ❌ **NO DEDICATED TEST FILE** (tested indirectly)

| Feature | Status | Notes |
|---------|--------|-------|
| `to_dict` | ⚠️ | Indirectly via helpers |
| `from_dict` | ⚠️ | Indirectly via helpers |
| `_deserialize_component` | ❌ | Not tested |
| `get_action` | ❌ | Not tested |
| `get_phase` | ❌ | Not tested |
| `get_zone` | ❌ | Not tested |
| `get_keyword` | ❌ | Not tested |
| `get_resource` | ❌ | Not tested |
| `get_rule` | ❌ | Not tested |
| `get_all_triggers` | ❌ | Not tested |
| `get_all_zones` | ❌ | Not tested |
| `get_all_resources` | ❌ | Not tested |
| `get_component_by_id` | ❌ | Not tested |
| `get_components_by_type` | ❌ | Not tested |
| `get_turn_components` | ❌ | Not tested |
| `get_phase_components` | ❌ | Not tested |

**Required Tests:**
- [ ] Create `test_ruleset_ir.py`
- [ ] Test serialization/deserialization
- [ ] Test component polymorphic deserialization
- [ ] Test all getter methods
- [ ] Test component type filtering

---

### 2. Validator.py
**Test File:** ❌ **NO TEST FILE**

| Feature | Status | Notes |
|---------|--------|-------|
| `validate` | ❌ | Not tested |
| `_validate_metadata` | ❌ | Not tested |
| `_validate_turn_structure` | ❌ | Not tested |
| `_validate_phase` | ❌ | Not tested |
| `_validate_actions` | ❌ | Not tested |
| `_validate_action` | ❌ | Not tested |
| `_validate_triggers` | ❌ | Not tested |
| `_validate_trigger` | ❌ | Not tested |
| `_validate_zones` | ❌ | Not tested |
| `_validate_zone` | ❌ | Not tested |
| `_validate_keywords` | ❌ | Not tested |
| `_validate_components` | ❌ | Not tested |
| `get_errors` / `get_warnings` | ❌ | Not tested |

**Required Tests:**
- [ ] Create `test_validator.py`
- [ ] Test valid ruleset passes
- [ ] Test metadata validation (missing name)
- [ ] Test turn structure validation (duplicate IDs, missing phases)
- [ ] Test action validation (invalid timing)
- [ ] Test trigger validation (missing when)
- [ ] Test zone validation (invalid type)
- [ ] Test component validation

---

### 3. ComponentDefinition.py
**Test File:** ❌ **NO DEDICATED TEST FILE**

#### ComponentDefinition (base)
| Feature | Status | Notes |
|---------|--------|-------|
| `to_dict` | ❌ | Not tested |
| `from_dict` | ❌ | Not tested |
| `get_trigger` | ❌ | Not tested |
| `get_resource` | ❌ | Not tested |
| `add_sub_component_reference` | ❌ | Not tested |
| `remove_sub_component_reference` | ❌ | Not tested |
| `get_all_triggers` | ❌ | Not tested |
| `get_all_resources` | ❌ | Not tested |

#### ComponentRegistry
| Feature | Status | Notes |
|---------|--------|-------|
| `register` | ❌ | Not tested |
| `get` | ❌ | Not tested |
| `get_by_type` | ❌ | Not tested |
| `unregister` | ❌ | Not tested |
| `list_all` | ❌ | Not tested |
| `clear` | ❌ | Not tested |

**Required Tests:**
- [ ] Create `test_component_definition.py`
- [ ] Test each component type (Game, Player, Card, Zone, Turn, Phase, Procedure, Custom)
- [ ] Test ComponentRegistry operations

---

### 4. ComponentType.py (Specific Component Definitions)
**Test File:** ❌ **NO TEST FILE**

| Class | Status | Notes |
|-------|--------|-------|
| GameComponentDefinition | ❌ | Not tested |
| PlayerComponentDefinition | ❌ | Not tested |
| CardComponentDefinition | ❌ | Not tested |
| ZoneComponentDefinition | ❌ | Not tested |
| TurnComponentDefinition | ❌ | Not tested |
| PhaseComponentDefinition | ❌ | Not tested |
| ProcedureComponentDefinition | ❌ | Not tested |
| ActionComponentDefinition | ❌ | Not tested |
| CustomComponentDefinition | ❌ | Not tested |

**Required Tests:**
- [ ] Create `test_component_types.py`
- [ ] Test each component type's specific fields
- [ ] Test `validate_component()` for each type
- [ ] Test `get_component_specific_data()` for each type

---

### 5. ExpressionModel.py
**Test File:** ❌ **NO TEST FILE**

| Feature | Status | Notes |
|---------|--------|-------|
| EvalContext | ❌ | Not tested |
| ConstNumber | ❌ | Not tested |
| PropNumber | ❌ | Not tested |
| Add / Sub | ❌ | Not tested |
| Gt / Eq | ❌ | Not tested |
| And | ❌ | Not tested |
| Func | ❌ | Not tested |
| ZoneSelector | ❌ | Not tested |
| FilterSelector | ❌ | Not tested |
| UnionSelector | ❌ | Not tested |

**Required Tests:**
- [ ] Create `test_expression_model.py`
- [ ] Test numeric expressions (ConstNumber, PropNumber, Add, Sub)
- [ ] Test boolean expressions (Gt, Eq, And)
- [ ] Test selectors (ZoneSelector, FilterSelector, UnionSelector)
- [ ] Test evaluation context creation and usage

---

### 6. workflow/WorkflowGraph.py
**Test File:** ❌ **NO TEST FILE**

| Feature | Status | Notes |
|---------|--------|-------|
| NodeType enum | ❌ | Not tested |
| WorkflowNode creation | ❌ | Not tested |
| WorkflowNode `to_dict`/`from_dict` | ❌ | Not tested |
| WorkflowEdge creation | ❌ | Not tested |
| WorkflowEdge `to_dict`/`from_dict` | ❌ | Not tested |
| WorkflowGraph creation | ❌ | Not tested |
| WorkflowGraph `start_node`/`end_node` | ❌ | Not tested |
| WorkflowGraph `get_node` | ❌ | Not tested |
| WorkflowGraph `get_first_nodes`/`get_last_nodes` | ❌ | Not tested |
| WorkflowGraph `get_outgoing_edges`/`get_incoming_edges` | ❌ | Not tested |
| WorkflowGraph `validate` | ❌ | Not tested |
| WorkflowGraph `to_dict`/`from_dict` | ❌ | Not tested |
| WorkflowState creation | ❌ | Not tested |
| WorkflowState `get_current_node` | ❌ | Not tested |
| WorkflowState `enter_node`/`exit_node` | ❌ | Not tested |
| WorkflowState `reset` | ❌ | Not tested |
| WorkflowState `to_dict`/`from_dict` | ❌ | Not tested |

**Required Tests:**
- [ ] Create `test_workflow_graph.py`
- [ ] Test WorkflowNode CRUD operations
- [ ] Test WorkflowEdge with conditions
- [ ] Test WorkflowGraph traversal
- [ ] Test WorkflowGraph validation rules
- [ ] Test WorkflowState lifecycle
- [ ] Test implicit start/end nodes

---

### 7. rule_definitions/RuleDefinition.py
**Test File:** ❌ **NO DEDICATED TEST FILE**

| Class | Status | Notes |
|-------|--------|-------|
| TargetDefinition | ❌ | Not tested |
| StepDefinition | ❌ | Not tested |
| PhaseDefinition | ❌ | Not tested |
| TurnStructure | ❌ | Not tested |
| ActionTarget | ❌ | Not tested |
| ActionDefinition | ❌ | Not tested |
| RuleDefinition | ❌ | Not tested |
| TriggerDefinition | ⚠️ | Partially via state_watcher tests |
| ZoneDefinition | ❌ | Not tested |
| KeywordDefinition | ❌ | Not tested |

**Required Tests:**
- [ ] Create `test_rule_definitions.py`
- [ ] Test each definition class serialization/deserialization
- [ ] Test ActionDefinition preconditions and targets
- [ ] Test TriggerDefinition with conditions

---

### 8. rule_definitions/EffectDefinition.py
**Test File:** ❌ **NO TEST FILE**

| Feature | Status | Notes |
|---------|--------|-------|
| EffectDefinition (all kinds) | ❌ | Not tested |

**Required Tests:**
- [ ] Test EffectDefinition for each kind
- [ ] Test serialization/deserialization

---

### 9. models/ResourceModel.py
**Test File:** ❌ **NO DEDICATED TEST FILE**

| Feature | Status | Notes |
|---------|--------|-------|
| ResourceDefinition | ❌ | Not tested |
| ResourceScope enum | ❌ | Not tested |
| ResourceType enum | ❌ | Not tested |

**Required Tests:**
- [ ] Create `test_resource_model.py`
- [ ] Test ResourceDefinition creation with all scopes and types

---

### 10. state_watcher/__init__.py
**Test File:** `test_state_watcher.py`

| Feature | Status | Notes |
|---------|--------|-------|
| TriggerType enum | ✅ | Tested in state_watcher tests |

---

## Integration Tests

**Currently:** ❌ **NO DEDICATED INTEGRATION TEST FILE**

| Test Scenario | Status | Notes |
|---------------|--------|-------|
| Full game loop (begin → actions → end) | ❌ | Not tested |
| Multi-turn game | ❌ | Not tested |
| Trigger chains | ❌ | Not tested |
| State-based action loop | ❌ | Not tested |
| Workflow traversal (Game → Turn → Phase) | ❌ | Not tested |
| Resource management across turns | ❌ | Not tested |
| Player input/response cycle | ❌ | Not tested |
| Event sourcing (replay from events) | ❌ | Not tested |

**Required Tests:**
- [ ] Create `test_integration.py`
- [ ] Test complete game scenarios
- [ ] Test complex trigger interactions
- [ ] Test workflow execution end-to-end

---

## Test Helpers

**File:** `helpers/ruleset_helper.py`

| Helper Method | Status | Notes |
|---------------|--------|-------|
| `create_minimal_ruleset` | ✅ | Used in tests |
| `create_ruleset_with_phases` | ✅ | Used in tests |
| `create_ruleset_with_actions` | ✅ | Used in tests |
| `create_ruleset_with_components` | ⚠️ | May need expansion |
| `create_ruleset_with_resources` | ⚠️ | May need expansion |
| `create_ruleset_with_player_component` | ✅ | Used in tests |
| `create_ruleset_with_game_component` | ✅ | Used in tests |
| `create_ruleset_with_triggers` | ⚠️ | May need expansion |
| `create_ruleset_ir` | ✅ | Used in tests |

**Needed Helpers:**
- [ ] Helper for creating complex trigger chains
- [ ] Helper for creating workflow graphs
- [ ] Helper for creating game with multiple phases

---

## Priority Test Creation Order

### High Priority (Core Functionality)
1. `test_effect_interpreter.py` - Effects are fundamental to game logic
2. `test_workflow_executor.py` - Workflow drives game flow
3. `test_workflow_graph.py` - Workflow structure definitions
4. `test_expression_model.py` - Conditions and selectors

### Medium Priority (Ruleset Definitions)
5. `test_ruleset_ir.py` - Ruleset loading/parsing
6. `test_validator.py` - Ruleset validation
7. `test_component_types.py` - Component type specifics
8. `test_rule_definitions.py` - Rule/action definitions

### Lower Priority (Supporting Systems)
9. `test_resource_model.py` - Resource definitions
10. `test_integration.py` - Full integration scenarios

---

## Testing Standards

### Naming Conventions
- Test files: `test_<module_name>.py`
- Test classes: `Test<ClassName>`
- Test methods: `test_<functionality>_<scenario>`

### Test Structure
```python
class TestClassName:
    """Tests for ClassName"""
    
    def test_feature_success_case(self):
        """Test feature with valid input"""
        pass
    
    def test_feature_edge_case(self):
        """Test feature with edge case input"""
        pass
    
    def test_feature_error_case(self):
        """Test feature with invalid input"""
        pass
```

### Async Tests
Use `@pytest.mark.asyncio` for async functions:
```python
@pytest.mark.asyncio
async def test_async_feature(self):
    result = await some_async_function()
    assert result is not None
```

---

## Running Tests

```bash
# Run all tests
cd TeapotEngine
pytest tests/

# Run specific test file
pytest tests/test_component.py

# Run with verbose output
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=TeapotEngine

# Run only async tests
pytest tests/ -m asyncio
```

---

## Notes

- Tests use the `RulesetHelper` class for creating test data
- Most tests are unit tests; integration tests are needed
- Async tests require `pytest-asyncio` plugin
- Component-based workflow system is the primary test gap

