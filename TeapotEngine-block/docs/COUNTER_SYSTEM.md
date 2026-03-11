# Counter/Prevention System Design

## Overview

This document describes the design for a future counter/prevention system that will allow pre-reactions to prevent events from being applied to the game state. The system will support preventing individual events as well as atomic event groups.

## Core Concepts

### Event Prevention

An event can be prevented by a pre-reaction before it is applied to the game state. When an event is prevented:

1. The event's status is set to `EventStatus.PREVENTED`
2. The event is not applied to the game state
3. Post-reactions for the prevented event may still trigger (e.g., "whenever an event is prevented")
4. An `EventPrevented` event may be emitted for other reactions to respond to

### Atomic Event Groups

Some operations generate multiple events that should be treated as a single atomic unit. For example:

- **Card Creation with Modifiers**: Creating a card, placing it in a zone, and giving it +2 power
  - Events: `CardCreated`, `CardMoved`, `PowerChanged`
  - If any event in this group is prevented, the entire group should be prevented

- **Spell Casting**: Paying costs, casting spell, resolving effects
  - Events: `ResourceChanged`, `SpellCast`, `SpellResolved`
  - If the spell is countered, all related events should be prevented

## Implementation Design

### Event Grouping

Events can be grouped using a `group_id` field:

```python
@dataclass
class Event:
    # ... existing fields ...
    group_id: Optional[int] = None  # Events with same group_id are atomic
    prevents_group: bool = False  # If True, preventing this event prevents the group
```

### Prevention Mechanism

#### 1. Pre-reaction Prevention

Pre-reactions can prevent events by:

**Option A: Setting Event Status**
```python
# In pre-reaction effect
if should_prevent_event(event):
    event.status = EventStatus.PREVENTED
```

**Option B: Returning Prevention Flag**
```python
# Pre-reaction returns prevention decision
prevention_result = await execute_pre_reaction(reaction, event)
if prevention_result.prevented:
    event.status = EventStatus.PREVENTED
```

**Option C: Emitting Prevention Event**
```python
# Pre-reaction emits CounterEvent
counter_event = Event(
    type="CounterEvent",
    payload={"target_event_id": event.id}
)
# System marks target event as prevented
```

#### Recommended: Option A with Group Propagation

Pre-reactions directly set the event status, and the system automatically propagates prevention to the group:

```python
async def _resolve_event(self, item: StackItem) -> None:
    event = self.event_registry.get(item.ref_id)
    
    # Check if event was prevented by pre-reactions
    if event.status == EventStatus.PREVENTED:
        # Prevent entire group if this event prevents its group
        if event.prevents_group and event.group_id:
            self._prevent_event_group(event.group_id)
        
        # Emit EventPrevented event
        self._emit_event_prevented(event)
        return
    
    # Apply event normally
    self.state.apply_event(event)
    # ... rest of resolution
```

### Group Prevention Logic

```python
def _prevent_event_group(self, group_id: int) -> None:
    """Prevent all events in an atomic group"""
    # Find all events with this group_id that haven't been applied yet
    for event_id in self.event_registry.get_all_event_ids():
        event = self.event_registry.get(event_id)
        if event and event.group_id == group_id:
            if event.status == EventStatus.PENDING:
                event.status = EventStatus.PREVENTED
```

### Example: Card Creation Prevention

**Scenario**: Card A has ability "Prevent any card from entering zone 'battlefield'"

**Card B Action**: Create a card, put it in battlefield, give it +2 power

**Event Flow**:
1. `CardCreated` event (group_id=1, prevents_group=True)
2. `CardMoved` event (group_id=1)
3. `PowerChanged` event (group_id=1)

**Pre-reaction Resolution**:
1. Pre-reaction from Card A matches `CardMoved` event
2. Pre-reaction sets `CardMoved.status = PREVENTED`
3. System detects `CardMoved` has `prevents_group=True` and `group_id=1`
4. System prevents entire group:
   - `CardCreated.status = PREVENTED`
   - `CardMoved.status = PREVENTED` (already set)
   - `PowerChanged.status = PREVENTED`
5. None of the events are applied to state
6. Card B's action is effectively countered

### Stack Resolution with Prevention

The current stack resolution flow needs to check prevention status:

```python
async def _resolve_event(self, item: StackItem) -> None:
    event = self.event_registry.get(item.ref_id)
    
    # Pre-reactions have already been discovered and resolved
    # Check if event was prevented
    if event.status == EventStatus.PREVENTED:
        # Handle group prevention
        if event.prevents_group and event.group_id:
            self._prevent_event_group(event.group_id)
        
        # Emit EventPrevented event for post-reactions
        prevented_event = Event(
            type="EventPrevented",
            payload={"prevented_event_id": event.id, "prevented_event_type": event.type}
        )
        await self._push_event_and_resolve(prevented_event)
        
        # Clean up prevented event
        self.event_registry.unregister(item.ref_id)
        return
    
    # Event not prevented - apply normally
    self.state.apply_event(event)
    # ... rest of resolution
```

## Future Enhancements

### Partial Prevention

Some systems may want to allow partial prevention (e.g., reduce damage instead of preventing it entirely):

```python
# Pre-reaction modifies event payload instead of preventing
if should_reduce_damage(event):
    event.payload["amount"] = max(0, event.payload["amount"] - reduction_amount)
    # Event still applies, but with modified values
```

### Prevention Priority

Multiple pre-reactions may try to prevent the same event. Priority system:

```python
@dataclass
class Reaction:
    # ... existing fields ...
    priority: int = 0  # Higher priority reactions resolve first
    can_prevent: bool = True  # Whether this reaction can prevent events
```

### Prevention Conditions

Pre-reactions may have conditions for when they can prevent:

```python
@dataclass
class Reaction:
    # ... existing fields ...
    prevention_conditions: List[Predicate] = field(default_factory=list)
    # Only prevent if all conditions are met
```

## Testing Considerations

- Events with no pre-reactions should resolve normally
- Pre-reactions that prevent events should prevent the event
- Preventing one event in a group should prevent the entire group
- Post-reactions should still trigger for prevented events (if desired)
- Events that generate new events should handle prevention correctly
- Prevention should work correctly with nested event groups

## Migration Path

1. **Phase 1**: Add `group_id` and `prevents_group` fields to Event (backward compatible)
2. **Phase 2**: Implement prevention checking in `_resolve_event`
3. **Phase 3**: Add group prevention logic
4. **Phase 4**: Add prevention priority and conditions
5. **Phase 5**: Add partial prevention support

