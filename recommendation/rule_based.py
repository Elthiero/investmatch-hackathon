from typing import List, Dict, Any
from sqlalchemy import or_, String
from sqlalchemy.sql.expression import type_coerce
from models import ForensicTool
from schemas import ScenarioInput


# Weighted scoring – sort by relevance
def weighted_score(
    tools: List[ForensicTool], scenario: ScenarioInput
) -> List[Dict[str, Any]]:
    """Assign a score (0‑100) to each tool, sort descending, and return enriched dicts."""
    # Weights sum to 1.0
    weights = {
        "capability": 0.35,
        "budget": 0.20,
        "skill": 0.15,
        "platform": 0.10,
        "access": 0.10,
        "region": 0.05,
        "quality": 0.05,
    }

    # Same region mapping as in hard filter
    region_map = {
        "global": "Global",
        "european_union": "European Union",
        "united_states": "United States",
        "canada": "Canada",
        "sweden": "Sweden",
        "israel": "Israel",
    }

    scored = []

    for tool in tools:
        total = 0.0

        # 1. Capability score (intersection ratio)
        if scenario.capabilities_needed:
            needed = {c.lower() for c in scenario.capabilities_needed}
            tool_caps = {c.lower() for c in tool.capability_tags}
            match_ratio = len(needed & tool_caps) / len(needed) if needed else 1.0
        else:
            match_ratio = 1.0
        total += match_ratio * weights["capability"]

        # 2. Budget score
        budget = scenario.budget
        cost_lower = tool.cost_and_licensing.lower()
        if budget == "free":
            if "free" in cost_lower or "open-source" in cost_lower:
                budget_score = 1.0
            elif "freemium" in cost_lower:
                budget_score = 0.5
            else:
                budget_score = 0.0
        elif budget == "paid":
            if any(
                x in cost_lower for x in ("enterprise", "subscription", "proprietary")
            ):
                budget_score = 1.0
            else:
                budget_score = 0.0
        else:  # "both"
            budget_score = 1.0
        total += budget_score * weights["budget"]

        # 3. Skill level score
        skill_map = {"beginner": 0, "intermediate": 1, "expert": 2}
        user_skill = skill_map.get(scenario.skill_level, 1)
        tool_skill = skill_map.get(tool.skill_level.lower(), 1)
        if tool_skill <= user_skill:
            skill_score = 1.0
        else:
            # Penalty for requiring higher skill than user has
            skill_score = max(0.0, 1.0 - (tool_skill - user_skill) * 0.4)
        total += skill_score * weights["skill"]

        # 4. Platform score
        if scenario.platform and scenario.platform != "other":
            platform_score = (
                1.0
                if scenario.platform.lower() in tool.platform_and_integration.lower()
                else 0.0
            )
        else:
            platform_score = 1.0
        total += platform_score * weights["platform"]

        # 5. Access level score
        access_map_user = {"public": 0, "corporate": 1, "law_enforcement": 2}
        user_access = access_map_user.get(scenario.access_level, 0)
        access_str = tool.access_restrictions.lower()
        if "public" in access_str:
            tool_access = 0
        elif any(x in access_str for x in ("vetted", "corporate", "enterprise")):
            tool_access = 1
        elif any(
            x in access_str for x in ("law enforcement", "government", "strictly")
        ):
            tool_access = 2
        else:
            tool_access = 0
        if tool_access <= user_access:
            access_score = 1.0
        else:
            access_score = max(0.0, 1.0 - (tool_access - user_access) * 0.5)
        total += access_score * weights["access"]

        # 6. Region score
        if scenario.region:
            db_region = region_map.get(scenario.region, scenario.region.title())
            region_score = (
                1.0 if db_region.lower() in (tool.region or "").lower() else 0.0
            )
        else:
            region_score = 1.0
        total += region_score * weights["region"]

        # 7. Quality score (based on evidentiary admissibility)
        quality_text = tool.evidentiary_admissibility.lower()
        if "highly admissible" in quality_text or "gold standard" in quality_text:
            quality = 1.0
        elif "widely accepted" in quality_text or "routinely accepted" in quality_text:
            quality = 0.8
        elif "admissible" in quality_text:
            quality = 0.6
        elif (
            "intelligence tool" in quality_text or "investigative lead" in quality_text
        ):
            quality = 0.4
        else:
            quality = 0.5
        total += quality * weights["quality"]

        final_score = int(total * 100)
        # explanation = _generate_explanation(tool, scenario, final_score)
        explanation = generate_explanation(
            match_ratio, budget_score, skill_score, access_score, scenario
        )

        scored.append(
            {
                "name": tool.name,
                "vendor": tool.vendor,
                "url": tool.url or "#",
                "score": final_score,
                "skill_required": tool.skill_level,
                "cost": tool.cost_and_licensing,
                "explanation": explanation,
            }
        )

    # Sort descending by score
    scored.sort(key=lambda x: x["score"], reverse=True)
    return scored


# Helper: simple template‑based explanation (no LLM)
def _generate_explanation(
    tool: ForensicTool, scenario: ScenarioInput, score: int
) -> str:
    """Create a short, human‑readable explanation of why the tool fits."""
    reasons = []

    # Capability match
    if scenario.capabilities_needed:
        matched = [
            c
            for c in scenario.capabilities_needed
            if c.lower() in (tc.lower() for tc in tool.capability_tags)
        ]
        if matched:
            reasons.append(f"supports {', '.join(matched[:2])}")

    # Budget match
    if scenario.budget == "free" and (
        "free" in tool.cost_and_licensing.lower()
        or "open-source" in tool.cost_and_licensing.lower()
    ):
        reasons.append("is free/open‑source")
    elif scenario.budget == "paid" and any(
        x in tool.cost_and_licensing.lower()
        for x in ("enterprise", "subscription", "proprietary")
    ):
        reasons.append("fits your paid budget")

    # Skill level match
    if tool.skill_level.lower() == scenario.skill_level:
        reasons.append(f"matches your {scenario.skill_level} skill level")

    if reasons:
        return f"**{tool.name}** is a strong fit because it {', '.join(reasons)}."
    else:
        return f"**{tool.name}** meets your core requirements with a score of {score}."


def generate_explanation(
    match_ratio: float,
    budget_score: float,
    skill_score: float,
    access_score: float,
    scenario: ScenarioInput,
) -> str:  # Return a string, not a list
    explanation_parts = []

    if match_ratio == 1.0:
        explanation_parts.append("Matches all required capabilities.")
    elif match_ratio > 0.5:
        explanation_parts.append(
            f"Supports {int(match_ratio*100)}% of requested features."
        )

    if budget_score == 1.0:
        explanation_parts.append(f"Fits your {scenario.budget} budget.")
    elif budget_score == 0.5:
        explanation_parts.append("Available as a freemium version.")

    if skill_score == 1.0:
        explanation_parts.append(f"Ideal for {scenario.skill_level} users.")
    elif skill_score < 1.0:
        explanation_parts.append("Note: Requires higher technical expertise.")

    if access_score == 1.0 and scenario.access_level != "public":
        explanation_parts.append(
            f"Meets {scenario.access_level.replace('_', ' ')} requirements."
        )

    # Join with periods for better readability
    return (
        " ".join(explanation_parts)
        if explanation_parts
        else "General match for your criteria."
    )
