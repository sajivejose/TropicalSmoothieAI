import streamlit as st
import datetime
import os
import json
import pandas as pd
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
load_dotenv()

from data_processor import DataPipeline
from ai_engine import PromptFactory

# Initialize Session State for Adaptive Learning / Feedback Logging
if 'feedback_db' not in st.session_state:
    st.session_state.feedback_db = []
if 'current_generated_offer' not in st.session_state:
    st.session_state.current_generated_offer = None
if 'current_context' not in st.session_state:
    st.session_state.current_context = None

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
- 🏆 **Visit Milestones**: 10, 25, 50, 100, 150, 200+
- ☀️ **Weather**: Hot days + Tropical/Berry prefs
- 🆕 **New Members**: <5 visits (acquisition)
""")

# Feedback database functions with UTF-8 encoding
def load_feedback_log():
    """Load feedback log from JSON file with UTF-8 encoding."""
    if Path("feedback_log.json").exists():
        try:
            with open("feedback_log.json", "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            st.error(f"Error loading feedback log: {str(e)}")
            return []
    return []

def save_feedback_log(feedback_list):
    """Save feedback log to JSON file with UTF-8 encoding."""
    try:
        with open("feedback_log.json", "w", encoding="utf-8") as f:
            json.dump(feedback_list, f, indent=2, ensure_ascii=False)
    except Exception as e:
        st.error(f"Error saving feedback log: {str(e)}")

def add_feedback(member_id, first_name, tier, status, reason, offer_data, timestamp=None):
    """Add feedback record to persistent log."""
    if timestamp is None:
        timestamp = datetime.datetime.now().isoformat()
    
    feedback_record = {
        "timestamp": timestamp,
        "member_id": member_id,
        "first_name": first_name,
        "tier": tier,
        "status": status,
        "reason": reason,
        "offer": offer_data
    }
    
    # Load existing, add new, save
    feedback_log = load_feedback_log()
    feedback_log.append(feedback_record)
    save_feedback_log(feedback_log)
    return feedback_record

# Tabs for main content
tab1, tab2, tab3 = st.tabs(["🎯 Offer Generator", "📊 Feedback Dashboard", "📈 Analytics & Insights"])

with tab1:
    if not eligible_guests.empty:
        # Main content area
        st.markdown(f"### ✨ Found {len(eligible_guests)} Eligible Customers for Offers")
        
        # Dropdown simulating the VA selector for TSC Associates
        guest_options = {f"{row['first_name']} ({row['tier'].upper()}, {int(row['nth_visit_count'])} visits) - {row['milestone_trigger'][:40]}...": idx 
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
                        
                        # Store in session for feedback
                        st.session_state.current_generated_offer = ai_output
                        st.session_state.current_context = context
                        st.session_state.current_raw_data = raw_guest_data
                        
                        st.success("✅ Generation Complete!")
                        st.metric(label="Target Delivery Method", value=context['channel'])
                        
                        # Render the copy cards
                        st.markdown(f"**Subject Line:** `{ai_output['subject_line']}`")
                        st.info(f"**Body Copy:**\n{ai_output['body_copy']}")
                        st.warning(f"🎁 **Tailored Reward Bundle:** {ai_output['recommended_bundle']}")
                        
                        # Step 5: Adaptive Feedback Loop
                        st.divider()
                        st.subheader("🔄 Feedback Loop & Adaptive Learning")
                        
                        # Reason options for rejection
                        rejection_reasons = [
                            "Medical/Health Claim",
                            "Off-Brand Tone",
                            "Inaccurate Information",
                            "Missing Personalization",
                            "Poor Copy Quality",
                            "Channel Mismatch",
                            "Other/Custom"
                        ]
                        
                        f_col1, f_col2 = st.columns(2)
                        
                        with f_col1:
                            if st.button("👍 Accept & Deploy to CRM"):
                                # Add to feedback log
                                add_feedback(
                                    member_id=raw_guest_data['member_id'],
                                    first_name=raw_guest_data['first_name'],
                                    tier=raw_guest_data['tier'],
                                    status="Approved",
                                    reason="Ready for deployment",
                                    offer_data=ai_output
                                )
                                st.session_state.feedback_db.append({
                                    "member_id": raw_guest_data['member_id'],
                                    "status": "Approved",
                                    "reason": "Ready for deployment"
                                })
                                st.success("✅ Sent directly via API to marketing distribution channel simulation.")
                        
                        with f_col2:
                            st.markdown("**👎 Flag for Review**")
                            rejection_reason = st.selectbox(
                                "Select rejection reason:",
                                rejection_reasons,
                                key=f"reject_{raw_guest_data['member_id']}"
                            )
                            
                            custom_notes = ""
                            if rejection_reason == "Other/Custom":
                                custom_notes = st.text_area(
                                    "Provide details:",
                                    placeholder="Describe the issue...",
                                    key=f"notes_{raw_guest_data['member_id']}"
                                )
                            
                            if st.button("🚩 Submit Rejection & Flag"):
                                final_reason = custom_notes if rejection_reason == "Other/Custom" else rejection_reason
                                
                                # Add to feedback log
                                add_feedback(
                                    member_id=raw_guest_data['member_id'],
                                    first_name=raw_guest_data['first_name'],
                                    tier=raw_guest_data['tier'],
                                    status="Rejected",
                                    reason=final_reason,
                                    offer_data=ai_output
                                )
                                st.session_state.feedback_db.append({
                                    "member_id": raw_guest_data['member_id'],
                                    "status": "Rejected",
                                    "reason": final_reason
                                })
                                st.error(f"🚩 Flagged for review: **{final_reason}**")
                                st.info("📝 Rejection logged and routed to compliance review queue.")
                            
                            # Option to regenerate
                            if st.button("🔄 Regenerate with Feedback"):
                                st.info(f"📊 Regenerating with feedback: {final_reason}")
                                # Could enhance prompt here based on feedback
                                
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")
                        st.info("💡 Make sure Ollama is running: `ollama serve` in another terminal")
    else:
        st.warning("⚠️ No eligible customers found with current filters.")
        st.info(f"Tried to find customers with birthdays near {current_date} or visit milestones.")

with tab2:
    st.header("📊 Feedback & Rejection Dashboard")
    
    # Load feedback log
    feedback_log = load_feedback_log()
    
    if feedback_log:
        # Summary metrics
        col1, col2, col3, col4 = st.columns(4)
        
        approved_count = sum(1 for f in feedback_log if f['status'] == 'Approved')
        rejected_count = sum(1 for f in feedback_log if f['status'] == 'Rejected')
        total_offers = len(feedback_log)
        approval_rate = (approved_count / total_offers * 100) if total_offers > 0 else 0
        
        col1.metric("Total Offers Reviewed", total_offers)
        col2.metric("Approved ✅", approved_count)
        col3.metric("Rejected 🚩", rejected_count)
        col4.metric("Approval Rate", f"{approval_rate:.1f}%")
        
        st.divider()
        
        # Rejection reasons breakdown
        if rejected_count > 0:
            st.subheader("🔴 Rejection Reasons Breakdown")
            rejection_reasons = {}
            for record in feedback_log:
                if record['status'] == 'Rejected':
                    reason = record['reason']
                    rejection_reasons[reason] = rejection_reasons.get(reason, 0) + 1
            
            # Create dataframe for visualization
            reason_df = pd.DataFrame(list(rejection_reasons.items()), columns=['Reason', 'Count'])
            reason_df = reason_df.sort_values('Count', ascending=False)
            
            col1, col2 = st.columns([2, 1])
            with col1:
                st.bar_chart(reason_df.set_index('Reason'))
            with col2:
                st.dataframe(reason_df, hide_index=True, use_container_width=True)
        
        st.divider()
        
        # Detailed feedback log table
        st.subheader("📋 Detailed Feedback Log")
        
        # Convert to display format
        display_data = []
        for record in feedback_log:
            display_data.append({
                "Timestamp": record['timestamp'][:10],  # Date only
                "Member": record['first_name'],
                "Tier": record['tier'].upper(),
                "Status": record['status'],
                "Reason": record['reason'][:40] + "..." if len(record['reason']) > 40 else record['reason']
            })
        
        df_display = pd.DataFrame(display_data)
        st.dataframe(df_display, hide_index=True, use_container_width=True)
        
        # Export options
        st.divider()
        st.subheader("📥 Export Feedback Log")
        col1, col2 = st.columns(2)
        
        with col1:
            csv = df_display.to_csv(index=False)
            st.download_button(
                label="📊 Download as CSV",
                data=csv,
                file_name=f"feedback_log_{datetime.date.today()}.csv",
                mime="text/csv"
            )
        
        with col2:
            json_str = json.dumps(feedback_log, indent=2, ensure_ascii=False)
            st.download_button(
                label="📄 Download as JSON",
                data=json_str,
                file_name=f"feedback_log_{datetime.date.today()}.json",
                mime="application/json"
            )
    else:
        st.info("📭 No feedback recorded yet. Generate and review offers to populate this dashboard.")

with tab3:
    st.header("📈 Analytics & Insights")
    
    feedback_log = load_feedback_log()
    
    if feedback_log:
        # Convert to DataFrame for analysis
        df = pd.DataFrame(feedback_log)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df['date'] = df['timestamp'].dt.date
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📊 Status Distribution")
            status_counts = df['status'].value_counts()
            # Use bar chart instead of pie chart for compatibility
            st.bar_chart(status_counts)
        
        with col2:
            st.subheader("📈 Approval Trend by Date")
            daily_stats = df.groupby('date')['status'].apply(lambda x: (x == 'Approved').sum()).reset_index()
            daily_stats.columns = ['Date', 'Approved']
            st.line_chart(daily_stats.set_index('Date'))
        
        st.divider()
        
        # Top rejection reasons
        st.subheader("🔴 Top Rejection Reasons")
        rejected_df = df[df['status'] == 'Rejected']
        if len(rejected_df) > 0:
            top_reasons = rejected_df['reason'].value_counts().head(10)
            st.bar_chart(top_reasons)
        else:
            st.info("No rejections yet!")
        
        st.divider()
        
        # Tier-wise approval rate
        st.subheader("🏆 Approval Rate by Tier")
        tier_stats = df.groupby('tier').apply(
            lambda x: {
                'Total': len(x),
                'Approved': (x['status'] == 'Approved').sum(),
                'Approval Rate': f"{(x['status'] == 'Approved').sum() / len(x) * 100:.1f}%"
            }
        ).reset_index()
        tier_stats.columns = ['Tier', 'Stats']
        
        tier_display = []
        for idx, row in tier_stats.iterrows():
            tier_display.append({
                'Tier': row['Tier'].upper(),
                'Total': row['Stats']['Total'],
                'Approved': row['Stats']['Approved'],
                'Approval Rate': row['Stats']['Approval Rate']
            })
        
        st.dataframe(pd.DataFrame(tier_display), hide_index=True, use_container_width=True)
        
        st.divider()
        
        # Guardrail violations summary
        st.subheader("⚠️ Guardrail Violations Summary")
        violation_keywords = {
            'Medical/Health Claim': ['medical', 'health', 'cure', 'lose weight', 'prevent'],
            'Off-Brand Tone': ['tone', 'brand', 'voice', 'style', 'crazy', 'lit', 'yo', 'dude'],
            'Inaccurate': ['inaccurate', 'wrong', 'incorrect', 'false'],
        }
        
        violations = {}
        for record in feedback_log:
            if record['status'] == 'Rejected':
                reason = record['reason'].lower()
                for vtype, keywords in violation_keywords.items():
                    if any(k in reason for k in keywords):
                        violations[vtype] = violations.get(vtype, 0) + 1
        
        if violations:
            violations_df = pd.DataFrame(list(violations.items()), columns=['Violation Type', 'Count'])
            st.dataframe(violations_df, hide_index=True, use_container_width=True)
        else:
            st.info("No guardrail violations detected in rejections.")
        
    else:
        st.info("📭 No data available yet. Generate and review offers to see analytics.")

# Show session feedback summary at bottom (if in tab1)
if st.session_state.feedback_db:
    st.divider()
    st.subheader("📋 Session Summary")
    col_a, col_b = st.columns(2)
    approved = sum(1 for f in st.session_state.feedback_db if f['status'] == 'Approved')
    rejected = sum(1 for f in st.session_state.feedback_db if f['status'] == 'Rejected')
    col_a.metric("Session Approved Offers", approved)
    col_b.metric("Session Rejected Offers", rejected)
