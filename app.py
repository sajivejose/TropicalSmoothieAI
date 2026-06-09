import streamlit as st
import datetime
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from data_processor import DataPipeline
from ai_engine import PromptFactory

# Initialize Session State for Adaptive Learning / Feedback Logging
if 'feedback_db' not in st.session_state:
    st.session_state.feedback_db = []

st.set_page_config(page_title="TSC Milestone Engine", layout="wide")
st.title("🍹 Tropical Smoothie Cafe — Virtual Assistant Prototype")
st.caption("Personalized 'Tropic' Milestone Offers Interface for TSC Associates")

# Display which provider is being used
use_ollama = os.environ.get("USE_OLLAMA", "true").lower() == "true"
if use_ollama:
    model = os.environ.get("OLLAMA_MODEL", "mistral")
    st.sidebar.info(f"🤖 Running with: **Ollama** ({model})")
else:
    st.sidebar.info("🤖 Running with: **OpenAI API**")

# Step 1: Run Pre-processing & Pipeline Simulation
pipeline = DataPipeline("mock_data.csv")
cleaned_data = pipeline.data_cleansing()

# Simulate today's check
current_date = "06-09"
date_range = 7  # 7-day window for birthdays
eligible_guests = pipeline.evaluate_milestones(current_date, date_range_days=date_range)

# Get pipeline statistics
stats = pipeline.get_pipeline_stats()

# Display pipeline statistics in sidebar
st.sidebar.header("📊 Data Pipeline Stats")
with st.sidebar.expander("Data Quality Metrics", expanded=True):
    st.metric(label="Total Records Loaded", value=stats['total_records'])
    st.metric(label="After Deduplication", value=stats['after_deduplication'])
    st.metric(label="Opt-In Members", value=stats['opt_in_count'])
    st.metric(label="Opt-Out (Filtered)", value=stats['opt_out_count'])
    st.divider()
    st.metric(label="Eligible for Offers", value=stats['eligible_offers'])
    st.metric(label="Eligibility Rate", value=stats['eligibility_rate'])

st.sidebar.header("🎯 Pipeline Controls")
st.sidebar.info(f"Processing execution date: **{current_date}** (±{date_range} days window)")

# Display filter info
st.sidebar.markdown("### 🔍 Active Filters:")
st.sidebar.markdown("""
- ✅ **Opt-in Status**: Must be True
- 🎂 **Birthday**: Within ±7 days
- 🎯 **Visit Milestones**: 10, 25, 50, 100, 150, 200+
- 🌞 **Weather**: Hot days + Tropical/Berry prefs
- 🆕 **New Members**: <5 visits (acquisition)
""")

if not eligible_guests.empty:
    # Main content area
    st.markdown(f"### ✨ Found {len(eligible_guests)} Eligible Customers for Offers")
    
    # Dropdown simulating the VA selector for TSC Associates
    guest_options = {f"{row['first_name']} ({row['tier'].upper()}, {int(row['nth_visit_count'])} visits) - {row['milestone_trigger']}": idx 
                     for idx, row in eligible_guests.iterrows()}
    selected_guest_label = st.selectbox("Select Active Loyalty Member Event:", list(guest_options.keys()))
    
    selected_idx = guest_options[selected_guest_label]
    raw_guest_data = eligible_guests.loc[selected_idx].to_dict()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📋 Feature Engineered Input Matrix")
        context = DataPipeline.feature_engineer_prompt_context(raw_guest_data)
        st.json(context)
        
    with col2:
        st.subheader("✨ GenAI Generated Engine Outputs")
        if st.button("Run Engine & Generate Custom Bundle"):
            with st.spinner("AI Engine generating tailored bundles..."):
                try:
                    # Run the AI execution step
                    ai_output = PromptFactory.generate_offer(context)
                    
                    st.success("Generation Complete!")
                    st.metric(label="Target Delivery Method", value=context['channel'])
                    
                    # Render the copy cards
                    st.markdown(f"**Subject Line:** `{ai_output['subject_line']}`")
                    st.info(f"**Body Copy:**\n{ai_output['body_copy']}")
                    st.warning(f"🎁 **Tailored Reward Bundle:** {ai_output['recommended_bundle']}")
                    
                    # Step 5: Adaptive Feedback Loop (Bottom line item of diagram)
                    st.divider()
                    st.subheader("🔄 Feedback Loop & Adaptive Learning")
                    f_col1, f_col2 = st.columns(2)
                    with f_col1:
                        if st.button("👍 Accept & Deploy to CRM"):
                            st.session_state.feedback_db.append({"member_id": raw_guest_data['member_id'], "status": "Approved"})
                            st.success("Sent directly via API to marketing distribution channel simulation.")
                    with f_col2:
                        if st.button("👎 Reject Copy / Flag Guardrail"):
                            st.session_state.feedback_db.append({"member_id": raw_guest_data['member_id'], "status": "Rejected"})
                            st.error("Flagged. Copy metrics routed back into pre-processing adjustment engine.")
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
                    st.info("💡 Make sure Ollama is running: `ollama serve` in another terminal")
    
    # Show feedback summary at bottom
    if st.session_state.feedback_db:
        st.divider()
        st.subheader("📈 Session Feedback Summary")
        approved = sum(1 for f in st.session_state.feedback_db if f['status'] == 'Approved')
        rejected = sum(1 for f in st.session_state.feedback_db if f['status'] == 'Rejected')
        col_a, col_b = st.columns(2)
        col_a.metric("Approved Offers", approved)
        col_b.metric("Rejected Offers", rejected)
else:
    st.warning("⚠️ No eligible customers found with current filters.")
    st.info(f"Tried to find customers with birthdays near {current_date} or visit milestones.")
