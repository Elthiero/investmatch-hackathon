import streamlit as st
from database import SessionLocal
from models import ForensicTool

st.set_page_config(page_title="Tool Details", layout="centered")
st.title("🛠️ Tool Details")

# Get tool name from URL query parameter
query_params = st.query_params
name = query_params.get("name")

if not name:
    st.error("No tool specified. Go back to the main page.")
    st.stop()

# Fetch tool from database
db = SessionLocal()
tool = db.query(ForensicTool).filter(ForensicTool.name == name).first()
db.close()

if not tool:
    st.error(f"Tool '{name}' not found.")
    st.stop()

# Display all fields
st.header(tool.name)
st.caption(f"by {tool.vendor}")

col1, col2 = st.columns(2)
with col1:
    #st.metric(f"**Score (from recommendation):**", "N/A - this is a static detail view")
    st.write(f"**Cost:** {tool.cost_and_licensing}")
    st.write(f"**Skill Level:** {tool.skill_level}")
    st.write(f"**Platform:** {tool.platform_and_integration}")
    st.write(f"**Access Restrictions:** {tool.access_restrictions}")
with col2:
    st.write(f"**Region:** {tool.region or 'Global'}")
    st.write(f"**Investigation Type:** {tool.investigation_type or 'General'}")
    st.write(f"**Last Verified:** {tool.last_verified}")
    if tool.url and tool.url != "#":
        st.link_button("Official Website", tool.url)

st.subheader("Capabilities")
st.write(", ".join(tool.capability_tags) if tool.capability_tags else "None")

st.subheader("Legal & Admissibility")
st.write(f"**Jurisdictional Legality:** {tool.jurisdictional_legality}")
st.write(f"**Evidentiary Admissibility:** {tool.evidentiary_admissibility}")

st.subheader("Documentation & Support")
st.write(tool.documentation_and_support)

if tool.additional_metadata:
    st.subheader("Additional Metadata")
    st.json(tool.additional_metadata)

# Back link
st.page_link("app.py", label="← Back to Search", icon="🏠")
