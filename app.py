import streamlit as st
import datetime
from data_processor import DataPipeline
from ai_engine import PromptFactory

# Initialize Session State for Adaptive Learning / Feedback Logging
if 'feedback_db' not in st.session_state:
    st.session_state.feedback_db = []

st.set_page_config(page_title="TSC Milestone Engine", layout="wide")
st.title("🍹 Tropical Smoothie Cafe — Virtual Assistant Prototype")
st.caption("Personalized 'Tropic' Milestone Offers Interface for TSC Associates")

# Step 1: Run Pre-processing & Pipeline Simulation
pipeline = DataPipeline("mock_data.csv")
cleaned_data = pipeline.data_cleansing()

# Simulate today's check (Marcus matches June 9th birthday based on 2026 calendar simulation)
current_date = "06-09" 
eligible_guests = pipeline.evaluate_milestones(current_date)

st.sidebar.header("Pipeline Controls")
st.sidebar.info(f"Processing execution date set to: {current_date}")
st.sidebar.metric(label="Eligible Guest Triggers Found", value=len(eligible_guests))

if not eligible_guests.empty:
    # Dropdown simulating the VA selector for TSC Associates
    guest_options = {f"{row['first_name']} ({row['milestone_trigger']})": idx for idx, row in eligible_guests.iterrows()}
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
else:
    st.write("No active milestone triggers for the specified window criteria.")