from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import asyncio
from tcg_server_exp import trigger_agent, effect_agent, target_agent, Runner, check_amount_data, process_amount_queries, update_processed_amounts

app = FastAPI(title="TCG Ability Parser API")

class AbilityRequest(BaseModel):
    description: str

class AbilityResponse(BaseModel):
    trigger: dict
    effect: dict
    target: dict

@app.post("/parse-ability", response_model=AbilityResponse)
async def parse_ability(request: AbilityRequest):
    try:
        # Run the agents in parallel
        Trigger_res, Effect_res, Target_res = await asyncio.gather(
            Runner.run(trigger_agent, request.description),
            Runner.run(effect_agent, request.description),
            Runner.run(target_agent, request.description),
        )

        outputs = {
            "trigger": Trigger_res.final_output,
            "effect": Effect_res.final_output,
            "target": Target_res.final_output,
        }

        # Collect initial amount queries
        initial_queries = []
        for output_type, output in outputs.items():
            initial_queries.extend(await check_amount_data(output_type, output))
        
        # Process amount queries recursively
        processed_results = await process_amount_queries(initial_queries)
        
        # Update outputs with processed results
        for output_type, output in outputs.items():
            await update_processed_amounts(output_type, output, processed_results)

        return AbilityResponse(
            trigger=outputs["trigger"],
            effect=outputs["effect"],
            target=outputs["target"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
