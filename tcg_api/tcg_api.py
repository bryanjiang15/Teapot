from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import asyncio
from tcg_server_exp import Generate_Ability
from abilityDefinitions import *
app = FastAPI(title="TCG Ability Parser API")

@app.post("/parse-ability", response_model=AbilityResponse)
async def parse_ability(request: AbilityRequest):

    # Temporary: return a hardcoded ability
    # return AbilityResponse(
    #     triggerDefinition=AbilityTrigger(
    #         triggerType=TriggerType.ON_REVEAL,
    #         triggerSource=[TargetData(
    #             targetType=TargetType.SELF,
    #             targetRange=TargetRange.NONE,
    #             targetSort=TargetSort.NONE,
    #             targetRequirements=RequirementData(
    #                 requirementAmount=AmountData(amountType=AbilityAmountType.CONSTANT, value=0, targetValueProperty=RequirementType.NONE, multiplierCondition=""),
    #                 requirementComparator=RequirementComparator.NONE,
    #                 requirementType=RequirementType.NONE
    #             )
    #         )]
    #     ),
    #     targetDefinition=[TargetData(
    #         targetType=TargetType.DECK,
    #         targetRange=TargetRange.FIRST,
    #         targetSort=TargetSort.NONE,
    #         targetRequirements=RequirementData(
    #             requirementAmount=AmountData(amountType=AbilityAmountType.CONSTANT, value=0, targetValueProperty=RequirementType.NONE, multiplierCondition=""),
    #             requirementComparator=RequirementComparator.NONE,
    #             requirementType=RequirementType.NONE
    #         )
    #     )],
    #     effect=EffectType.GAIN_POWER,
    #     amount=AmountData(amountType=AbilityAmountType.CONSTANT, value=2, targetValueProperty=RequirementType.NONE, multiplierCondition="")
    # )
    try:
       return await Generate_Ability(request.abilityDescription, request.cardDescription)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        # ssl_keyfile="ssl/key.pem",
        # ssl_certfile="ssl/cert.pem"
    )
