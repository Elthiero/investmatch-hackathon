import streamlit as st
from database import SessionLocal
from recommendation.rule_based import weighted_score
from models import ForensicTool
from schemas import ScenarioInput

st.set_page_config(page_title="INVESTMATCH Recommender", layout="wide")
st.title("🔍 INVESTMATCH: Tool Recommender")
st.markdown(
    "Describe your investigation needs – we'll find the best tools (soft matching, no hard exclusions)."
)

with st.form("input_form"):
    col1, col2 = st.columns(2)
    with col1:
        inv_type = st.selectbox(
            "Investigation Focus",
            [
                "osint",
                "digital_forensics",
                "csam_detection",
                "crypto_tracing",
                "incident_response",
            ],
        )
        region = st.selectbox(
            "Region / Jurisdiction",
            ["global", "european_union", "united_states", "canada", "sweden", "israel"],
        )
        capabilities = st.multiselect(
            "Required Capabilities",
            [
                "osint",
                "link_analysis",
                "digital_forensics",
                "mobile_extraction",
                "csam_detection",
                "hash_matching",
                "deepfake_detection",
                "blockchain_tracing",
            ],
        )
    with col2:
        budget = st.radio("Budget", ["free", "paid", "both"], horizontal=True)
        skill = st.select_slider("Skill Level", ["beginner", "intermediate", "expert"])
        platform = st.selectbox(
            "Platform", ["windows", "macos", "linux", "web_based", "other"]
        )
        access = st.selectbox(
            "Access Level", ["public", "corporate", "law_enforcement"]
        )

    submitted = st.form_submit_button("Find Tools")

if submitted:
    with st.spinner("Scoring tools..."):
        # Build scenario
        scenario = ScenarioInput(
            investigation_type=inv_type,
            region=region,
            capabilities_needed=capabilities,
            budget=budget,
            skill_level=skill,
            platform=platform,
            access_level=access,
        )

        # Get all tools from DB
        db = SessionLocal()
        all_tools = db.query(ForensicTool).all()
        db.close()

        if not all_tools:
            st.warning("No tools found in database. Please run admin import first.")
        else:
            # Soft scoring (no hard filters) – we use weighted_score on all tools
            scored = weighted_score(all_tools, scenario)

            if not scored:
                st.warning("No tools could be scored. Check your data.")
            else:
                st.success(
                    f"Top {len(scored[:5])} recommendations based on your criteria"
                )
                for tool in scored[:5]:
                    with st.container():
                        col_a, col_b = st.columns([3, 1])
                        with col_a:
                            st.subheader(f"{tool['name']} – Score: {tool['score']}")
                            st.write(f"**Vendor:** {tool['vendor']}")
                            st.write(
                                f"**Cost:** {tool['cost']}  |  **Skill:** {tool['skill_required']}"
                            )
                            st.caption(tool["explanation"])
                        with col_b:
                            # Link to detail page using query parameters
                            st.page_link(
                                "pages/detail.py",
                                label="View Details",
                                icon="🔍",
                                query_params={"name": tool["name"]},
                            )
                        st.divider()
