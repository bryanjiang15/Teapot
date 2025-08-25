import asyncio
from agents import Runner
from abilityDefinitions import *
from Agents.agent_registry import agent_registry
from SnapComponents.SnapComponentDefinition import *

class AmountProcessor:
    def __init__(self):
        pass

    def check_amount_data(self, data: SnapTriggerDefinition | SnapActionDefinition | SnapConditionDefinition | SnapComponentDefinition) -> list[str]:
        """Process the amount data for the given data type."""
        if isinstance(data, SnapActionDefinition):
            return data.effect.get_processable_queries() + data.targetDefinition.get_processable_queries()
        elif isinstance(data, SnapConditionDefinition):
            return data.condition.get_processable_queries()
        elif isinstance(data, SnapTriggerDefinition):
            return data.trigger.get_processable_queries()
        return []
    
    async def process_amount_data(self, amount_queries: list[str], depth: int = 0) -> dict[str, dict]:
        """Process the amount data for the given amount queries."""
        if depth >= 2 or not amount_queries:
            return {}
        
        target_agent = agent_registry.get_agent("target_agent")

        # Process current level of amount queries
        amount_res = await asyncio.gather(
            *[Runner.run(target_agent, query) for query in amount_queries]
        )
        
        # Create mapping of queries to their results
        processed_results = {query: res.final_output for query, res in zip(amount_queries, amount_res)}

        # Check for nested amount data in the results
        nested_queries = []
        query_to_parent = {}  # Map nested queries to their parent queries

        for query, result in zip(amount_queries, amount_res):
            nested = self.check_amount_data(result.final_output)
            nested_queries.extend(nested)
            # Map each nested query to its parent query
            for nested_query in nested:
                query_to_parent[nested_query] = query

        # Recursively process nested queries
        if nested_queries:
            nested_results = await self.process_amount_data(nested_queries, depth + 1)
            # Update parent results with nested results
            for query, result in processed_results.items():
                self.update_processed_amounts(result, nested_results)
        
        return processed_results
    
    def update_processed_amounts(self, data: SnapTriggerDefinition | SnapActionDefinition | SnapConditionDefinition | SnapComponentDefinition, processed_results: dict[str, dict]) -> None:
        """Update the processed amount data for the given data."""
        if isinstance(data, SnapActionDefinition):
            data.effect.update_data(processed_results)
        elif isinstance(data, SnapConditionDefinition):
            data.condition.update_data(processed_results)
        elif isinstance(data, SnapTriggerDefinition):
            data.trigger.update_data(processed_results)
        elif isinstance(data, SnapComponentDefinition):
            pass
        else:
            raise ValueError(f"Unsupported data type: {type(data)}")