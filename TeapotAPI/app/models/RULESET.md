## Database Schema for Rulesets

Given the complex nested structure of rulesets (phases, zones, actions, triggers, etc.), we need a flexible database design that can handle both the full IR structure and efficient querying.

### Approach 1: Hybrid JSON + Relational (Recommended)

Store the complete IR as JSONB for flexibility, with key components extracted to relational tables for efficient querying.

#### Core Ruleset Table
```sql
CREATE TABLE rulesets (
    ruleset_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    owner_id UUID NOT NULL REFERENCES users(user_id),
    name VARCHAR(255) NOT NULL,
    version VARCHAR(50) NOT NULL,
    status VARCHAR(50) DEFAULT 'draft' NOT NULL,
    
    -- Complete IR as JSONB
    ir_data JSONB NOT NULL,
    
    -- Metadata for quick access
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Indexes for common queries
    CONSTRAINT unique_name_version UNIQUE (name, version)
);

-- Indexes for performance
CREATE INDEX idx_rulesets_owner ON rulesets(owner_id);
CREATE INDEX idx_rulesets_status ON rulesets(status);
CREATE INDEX idx_rulesets_ir_gin ON rulesets USING GIN (ir_data);
```

#### Extracted Components Tables
```sql
-- Actions extracted for fast lookup
CREATE TABLE ruleset_actions (
    action_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    ruleset_id UUID NOT NULL REFERENCES rulesets(ruleset_id) ON DELETE CASCADE,
    action_key VARCHAR(100) NOT NULL, -- e.g., "play_card", "attack"
    name VARCHAR(255) NOT NULL,
    timing VARCHAR(50) NOT NULL, -- "stack", "instant", etc.
    action_data JSONB NOT NULL, -- Full action definition
    
    CONSTRAINT unique_ruleset_action UNIQUE (ruleset_id, action_key)
);

-- Phases extracted for phase management
CREATE TABLE ruleset_phases (
    phase_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    ruleset_id UUID NOT NULL REFERENCES rulesets(ruleset_id) ON DELETE CASCADE,
    phase_key VARCHAR(100) NOT NULL, -- e.g., "main", "combat"
    name VARCHAR(255) NOT NULL,
    phase_order INTEGER NOT NULL,
    phase_data JSONB NOT NULL, -- Full phase definition with steps
    
    CONSTRAINT unique_ruleset_phase UNIQUE (ruleset_id, phase_key)
);

-- Zones for game state management
CREATE TABLE ruleset_zones (
    zone_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    ruleset_id UUID NOT NULL REFERENCES rulesets(ruleset_id) ON DELETE CASCADE,
    zone_key VARCHAR(100) NOT NULL, -- e.g., "hand", "battlefield", "graveyard"
    name VARCHAR(255) NOT NULL,
    zone_type VARCHAR(50) NOT NULL, -- "private", "public", "shared"
    zone_data JSONB NOT NULL,
    
    CONSTRAINT unique_ruleset_zone UNIQUE (ruleset_id, zone_key)
);

-- Triggers for reaction discovery
CREATE TABLE ruleset_triggers (
    trigger_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    ruleset_id UUID NOT NULL REFERENCES rulesets(ruleset_id) ON DELETE CASCADE,
    trigger_key VARCHAR(100) NOT NULL,
    event_type VARCHAR(100) NOT NULL, -- e.g., "Damaged", "EnterZone"
    timing VARCHAR(50) NOT NULL, -- "pre", "post"
    trigger_data JSONB NOT NULL,
    
    CONSTRAINT unique_ruleset_trigger UNIQUE (ruleset_id, trigger_key)
);

-- Indexes for fast lookups
CREATE INDEX idx_actions_ruleset ON ruleset_actions(ruleset_id);
CREATE INDEX idx_actions_timing ON ruleset_actions(timing);
CREATE INDEX idx_phases_ruleset ON ruleset_phases(ruleset_id);
CREATE INDEX idx_phases_order ON ruleset_phases(ruleset_id, phase_order);
CREATE INDEX idx_zones_ruleset ON ruleset_zones(ruleset_id);
CREATE INDEX idx_triggers_ruleset ON ruleset_triggers(ruleset_id);
CREATE INDEX idx_triggers_event_type ON ruleset_triggers(event_type);
```

### Approach 2: Fully Relational (Alternative)

If you need maximum query performance and complex relationships:

```sql
-- Actions with full relational structure
CREATE TABLE ruleset_actions (
    action_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    ruleset_id UUID NOT NULL REFERENCES rulesets(ruleset_id),
    action_key VARCHAR(100) NOT NULL,
    name VARCHAR(255) NOT NULL,
    timing VARCHAR(50) NOT NULL,
    description TEXT
);

-- Action preconditions
CREATE TABLE action_preconditions (
    precondition_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    action_id UUID NOT NULL REFERENCES ruleset_actions(action_id) ON DELETE CASCADE,
    precondition_order INTEGER NOT NULL,
    op VARCHAR(100) NOT NULL, -- "has_resource", "in_zone", etc.
    params JSONB NOT NULL
);

-- Action costs
CREATE TABLE action_costs (
    cost_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    action_id UUID NOT NULL REFERENCES ruleset_actions(action_id) ON DELETE CASCADE,
    cost_order INTEGER NOT NULL,
    op VARCHAR(100) NOT NULL, -- "pay_resource", "tap", etc.
    params JSONB NOT NULL
);

-- Action targets
CREATE TABLE action_targets (
    target_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    action_id UUID NOT NULL REFERENCES ruleset_actions(action_id) ON DELETE CASCADE,
    target_key VARCHAR(100) NOT NULL, -- "card", "attacker", etc.
    selector JSONB NOT NULL,
    count INTEGER DEFAULT 1
);

-- Action effects
CREATE TABLE action_effects (
    effect_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    action_id UUID NOT NULL REFERENCES ruleset_actions(action_id) ON DELETE CASCADE,
    effect_order INTEGER NOT NULL,
    op VARCHAR(100) NOT NULL, -- "move_zone", "deal_damage", etc.
    params JSONB NOT NULL
);
```

### Recommended Implementation Strategy

#### 1. Start with Hybrid Approach
```python
# Pydantic models for validation
from pydantic import BaseModel
from typing import List, Dict, Any, Optional

class RulesetIR(BaseModel):
    version: str
    metadata: Dict[str, Any]
    turnStructure: Dict[str, Any]
    actions: List[Dict[str, Any]]
    triggers: List[Dict[str, Any]]
    zones: List[Dict[str, Any]]
    keywords: List[Dict[str, Any]]
    # ... other components

class RulesetModel(BaseModel):
    ruleset_id: UUID
    owner_id: UUID
    name: str
    version: str
    status: str
    ir_data: RulesetIR
    
    class Config:
        from_attributes = True
```

#### 2. Database Operations
```python
# Repository pattern for ruleset operations
class RulesetRepository:
    async def create_ruleset(self, ruleset_data: RulesetIR, owner_id: UUID) -> Ruleset:
        # Validate IR structure
        validated_ir = RulesetIR(**ruleset_data)
        
        # Create ruleset record
        ruleset = Ruleset(
            owner_id=owner_id,
            name=validated_ir.metadata["name"],
            version=validated_ir.version,
            ir_data=validated_ir.dict()
        )
        
        # Save to database
        await self.db.add(ruleset)
        await self.db.commit()
        
        # Extract components for fast lookup
        await self._extract_components(ruleset.ruleset_id, validated_ir)
        
        return ruleset
    
    async def _extract_components(self, ruleset_id: UUID, ir_data: RulesetIR):
        # Extract actions
        for action in ir_data.actions:
            await self.db.add(RulesetAction(
                ruleset_id=ruleset_id,
                action_key=action["id"],
                name=action["name"],
                timing=action["timing"],
                action_data=action
            ))
        
        # Extract phases
        for phase in ir_data.turnStructure["phases"]:
            await self.db.add(RulesetPhase(
                ruleset_id=ruleset_id,
                phase_key=phase["id"],
                name=phase["name"],
                phase_order=phase.get("order", 0),
                phase_data=phase
            ))
        
        # Extract zones, triggers, etc.
        # ... similar extraction logic
        
        await self.db.commit()
    
    async def get_available_actions(self, ruleset_id: UUID, game_state: Dict) -> List[Dict]:
        # Query extracted actions for fast lookup
        actions = await self.db.query(RulesetAction).filter(
            RulesetAction.ruleset_id == ruleset_id
        ).all()
        
        # Filter by game state and return
        available_actions = []
        for action in actions:
            if self._can_take_action(action, game_state):
                available_actions.append({
                    "id": action.action_key,
                    "name": action.name,
                    "timing": action.timing,
                    "data": action.action_data
                })
        
        return available_actions
```

#### 3. Migration Strategy
```python
# Alembic migration for the hybrid approach
def upgrade():
    # Create main tables
    op.create_table('rulesets', ...)
    op.create_table('ruleset_actions', ...)
    op.create_table('ruleset_phases', ...)
    op.create_table('ruleset_zones', ...)
    op.create_table('ruleset_triggers', ...)
    
    # Create indexes
    op.create_index('idx_rulesets_owner', 'rulesets', ['owner_id'])
    op.create_index('idx_rulesets_ir_gin', 'rulesets', ['ir_data'], postgresql_using='gin')
    # ... other indexes

def downgrade():
    op.drop_table('ruleset_triggers')
    op.drop_table('ruleset_zones')
    op.drop_table('ruleset_phases')
    op.drop_table('ruleset_actions')
    op.drop_table('rulesets')
```

### Benefits of Hybrid Approach

1. **Flexibility**: Full IR stored as JSONB for complex nested structures
2. **Performance**: Key components extracted for fast queries
3. **Validation**: Pydantic models ensure IR structure integrity
4. **Scalability**: Can add more extracted tables as needed
5. **Migration**: Easy to evolve schema without breaking existing data

### Query Examples

```python
# Get all actions for a ruleset
actions = await db.query(RulesetAction).filter(
    RulesetAction.ruleset_id == ruleset_id
).all()

# Get phases in order
phases = await db.query(RulesetPhase).filter(
    RulesetPhase.ruleset_id == ruleset_id
).order_by(RulesetPhase.phase_order).all()

# Search within IR data
rulesets = await db.query(Ruleset).filter(
    Ruleset.ir_data['metadata']['name'].astext.ilike('%magic%')
).all()

# Get triggers for specific event type
triggers = await db.query(RulesetTrigger).filter(
    RulesetTrigger.ruleset_id == ruleset_id,
    RulesetTrigger.event_type == 'Damaged'
).all()
```

This hybrid approach gives you the best of both worlds: the flexibility of JSON storage for complex nested data, with the performance of relational queries for common operations.

---