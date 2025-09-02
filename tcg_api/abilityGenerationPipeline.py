import asyncio
from agents import Runner, trace
from openai import OpenAI
from abilityData import *
from abilityDefinitions import *
from dotenv import load_dotenv
from AmountProcessors.amount_processing import AmountProcessor
from Agents.agent_registry import agent_registry
from Agents.CardAgents import register_agents
from SnapComponents.SnapComponent import SnapComponent, SnapComponentType
from AbilityResponse import AbilityResponse, AbilityDefinition
from SnapComponents.SnapComponentDefinition import SnapConditionDefinition, SnapActionDefinition, SnapComponentDefinition, SnapTriggerDefinition, SnapComponentUnion

# Load environment variables from .env file
load_dotenv()

class AbilityGenerationPipeline:
    """
    A class that handles the complete pipeline for generating card abilities.
    This includes ability decomposition, art generation, component processing, and result compilation.
    """
    
    def __init__(self):
        """Initialize the pipeline with required components."""
        self.amount_processor = AmountProcessor()
        self.client = OpenAI()
    
    async def generate_art(self, card_description: str):
        """
        Generate art for a card based on its description.
        
        Args:
            card_description (str): Description of the card for art generation
            
        Returns:
            str: URL of the generated art
        """
        prompt = f"""Create a detailed, high-fantasy illustration in the style of Magic: The Gathering trading cards. 
        The scene features: {card_description}. Use dramatic lighting, simple color palette, and painterly textures. 
        The composition should be dynamic and focused on the main subject, with a complementary and simple background. 
        The mood should match the description. Do not include any text or borders—only the illustration.
        """

        result = self.client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            size="1024x1792"
        )

        return result.data[0].url
    
    async def decompose_ability(self, ability_description: str):
        """
        Decompose an ability description into its components.
        
        Args:
            ability_description (str): The ability description to decompose
            
        Returns:
            list: List of ability components
        """
        ability_decomposition_agent = agent_registry.get_agent('ability_decomposition_agent')
        ability_decomposition_res = await Runner.run(ability_decomposition_agent, ability_description)

        return ability_decomposition_res.final_output
    
    async def process_component(self, component: SnapComponent, index: int, ability_description: str):
        """
        Process a single component through the triage agent.
        
        Args:
            component (SnapComponent): The component to process
            index (int): Index of the component
            ability_description (str): Full ability description for context
            
        Returns:
            dict: Processing result for the component
        """
        print(f"\nProcessing component {index+1}: {component}")
        
        trigger_agent = agent_registry.get_agent('trigger_agent')
        effect_agent = agent_registry.get_agent('effect_agent')
        target_agent = agent_registry.get_agent('target_agent')
        requirement_agent = agent_registry.get_agent('requirement_agent')

        if component.componentType == SnapComponentType.TRIGGER:
            result = await Runner.run(trigger_agent, component.componentDescription)
            return SnapTriggerDefinition(componentType=SnapComponentType.TRIGGER, trigger=result.final_output)
        elif component.componentType == SnapComponentType.Action:
            effect_res = await Runner.run(effect_agent, component.componentDescription)
            target_res = await Runner.run(target_agent, component.componentDescription)
            return SnapActionDefinition(componentType=SnapComponentType.Action, effect=effect_res.final_output.effectType, amount=effect_res.final_output.amount , targetDefinition=[target_res.final_output])
        elif component.componentType == SnapComponentType.IF:
            result = await Runner.run(requirement_agent, component.componentDescription)
            return SnapConditionDefinition(componentType=SnapComponentType.IF, requirement=result.final_output, requirementTarget=result.final_output.target)
        elif component.componentType == SnapComponentType.WHILE:
            result = await Runner.run(requirement_agent, component.componentDescription)
            return SnapConditionDefinition(componentType=SnapComponentType.WHILE, requirement=result.final_output, requirementTarget=result.final_output.target)
        elif component.componentType == SnapComponentType.ELSE:
            return SnapComponentDefinition(componentType=SnapComponentType.ELSE)
        # elif component.componentType == SnapComponentType.CHOICE:
        #     return SnapComponentDefinition(componentType=SnapComponentType.CHOICE)
        elif component.componentType == SnapComponentType.ENDCONDITION:
            return SnapComponentDefinition(componentType=SnapComponentType.ENDCONDITION)
    
    async def process_components_and_art_parallel(self, components: list[SnapComponent], ability_description: str, card_description: str):
        """
        Process all components and generate art in parallel.
        
        Args:
            components (list): List of components to process
            ability_description (str): Full ability description for context
            card_description (str): Description of the card for art generation
            
        Returns:
            tuple: (art_url, processed_components)
        """
        # Create tasks for all components
        component_tasks = [
            self.process_component(component, i, ability_description)
            for i, component in enumerate(components)
        ]
        
        # Create task for art generation
        art_task = self.generate_art(card_description)
        
        # Run all tasks in parallel (components + art)
        all_tasks = component_tasks + [art_task]
        results = await asyncio.gather(*all_tasks)
        
        # Separate results
        processed_components = results[:-1]  # All except the last result
        art_url = results[-1]  # Last result is the art URL
        
        print(f"\nProcessed {len(processed_components)} components and generated art in parallel:")
        for i, component in enumerate(processed_components):
            print(f"{i+1}. {component}")
        return art_url, processed_components
    
    async def run_fallback_processing(self, ability_description: str):
        """
        Run the original approach as fallback to ensure complete results.
        
        Args:
            ability_description (str): The ability description to process
            
        Returns:
            dict: Dictionary containing trigger, effect, target, and requirement results
        """
        trigger_agent = agent_registry.get_agent('trigger_agent')
        effect_agent = agent_registry.get_agent('effect_agent')
        target_agent = agent_registry.get_agent('target_agent')
        requirement_agent = agent_registry.get_agent('requirement_agent')
        
        print("\nRunning fallback processing to ensure complete results...")
        Trigger_res, Effect_res, Target_res, Requirement_res = await asyncio.gather(
            Runner.run(trigger_agent, ability_description),
            Runner.run(effect_agent, ability_description),
            Runner.run(target_agent, ability_description),
            Runner.run(requirement_agent, ability_description)
        )
        
        return {
            "trigger": Trigger_res.final_output,
            "effect": Effect_res.final_output,
            "target": Target_res.final_output,
            "requirement": Requirement_res.final_output,
        }
    
    async def process_amount_data(self, components: list[SnapComponentUnion]):
        """
        Process amount data in the components and update them with processed results.
        
        Args:
            components (list): List of processed component results
            
        Returns:
            list: Updated components with processed amount data
        """
        # Collect initial amount queries from all components
        initial_queries = []
        for component in components:
            if component is not None:  # Skip None results from failed processing
                  initial_queries.extend(self.amount_processor.check_amount_data(component))
        
        # Process amount queries recursively
        processed_results = await self.amount_processor.process_amount_data(initial_queries)
        
        # Update components with processed results
        for component in components:
            if component is not None:  # Skip None results from failed processing
                self.amount_processor.update_processed_amounts(component, processed_results)
        
        return components
    
    async def generate_ability(self, ability_description: str, card_description: str):
        """
        Main method to generate a complete ability with art and processed components.
        
        Args:
            ability_description (str): Description of the ability to generate
            card_description (str): Description of the card for art generation
            
        Returns:
            AbilityResponse: Complete ability response with definition and art URL
        """
        result = None
        with trace("Ability Configuration"):
            # Step 1: Decompose the ability into components
            components = await self.decompose_ability(ability_description)
            
            print("Decomposed Components:")
            # for i, component in enumerate(components):
            #     print(f"{i+1}. {component}")
            
            # Step 2 & 3: Generate art and process all components in parallel
            art_url, processed_components = await self.process_components_and_art_parallel(
                components, ability_description, card_description
            )
            
            # Step 4: Analyze processed components and run fallback if needed
            valid_results = [result for result in processed_components if result is not None]
            print(f"Successfully processed {len(valid_results)} out of {len(components)} components")
            
            # Process amount data for components
            processed_components = await self.process_amount_data(processed_components)
            
            # Run fallback processing to ensure complete results
            # outputs = await self.run_fallback_processing(ability_description)

            trigger_res = next((c for c in processed_components if c.componentType == SnapComponentType.TRIGGER), None)
            
            other_components = [component for component in processed_components if component.componentType != SnapComponentType.TRIGGER]
        
            result = AbilityResponse(
                AbilityDefinition=AbilityDefinition(
                    triggerDefinition=trigger_res,
                    snapComponentDefinitions=other_components
                ),
                CardArtUrl=art_url,
            )

            print(result)
        return result 