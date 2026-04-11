from pydantic import BaseModel, ConfigDict
from typing import List

class ScenarioInput(BaseModel):
    investigation_type: str
    region: str
    capabilities_needed: List[str]
    budget: str
    skill_level: str
    platform: str
    access_level: str
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "investigation_type": "csam_distribution",
                "region": "global",
                "capabilities_needed": ["image_analysis", "hash_matching"],
                "budget": "free",
                "skill_level": "intermediate",
                "platform": "windows",
                "access_level": "law_enforcement"
            }
        }
    )
    
class ToolBase(BaseModel):
    name: str
    vendor: str
    capability_tags: List[str]
    jurisdictional_legality: str
    evidentiary_admissibility: str
    cost_and_licensing: str
    access_restrictions: str
    skill_level: str
    platform_and_integration: str
    last_verified: str
    documentation_and_support: str
    additional_metadata: dict = None
    url: str = None
    region: str = None
    investigation_type: str = None

class ToolRecommendationResponse(BaseModel):
    name: str
    score: int
    explanation: str
    url: str = None
    vendor: str = None
    skill_required: str = None
    cost: str = None