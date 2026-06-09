# 🍹 Tropical Smoothie Cafe Marketing AI Agent

A production-ready prototype for hyper-personalized marketing offers powered by AI, designed for Tropical Smoothie Cafe loyalty members.

## Overview

This system combines data processing, AI-driven copywriting, and a virtual assistant interface to deliver personalized milestone offers to TSC Associates and loyalty members. The architecture integrates:

- **1st-party loyalty data** (member profiles, visit history, preferences)
- **3rd-party environmental signals** (weather, local events)
- **GenAI-powered personalization** (milestone detection & custom offer generation)
- **Feedback loop integration** (adaptive learning from TSC Associate approvals/rejections)

## Architecture Components

### 1. Data Pipeline (`data_processor.py`)
- **Cleansing**: Deduplication, consent filtering, missing value imputation
- **Milestone Detection**: Birthday, Nth-visit milestones, local events
- **Feature Engineering**: Transforms raw data into LLM-ready context

### 2. AI Engine (`ai_engine.py`)
- **Prompt Factory**: System prompts with brand voice guardrails
- **Structured Outputs**: JSON Mode ensures safe downstream API integration
- **Copy Guardrails**: Prevents medical claims, enforces channel-specific length limits

### 3. Virtual Assistant UI (`app.py`)
- **Streamlit Interface**: Dashboard for TSC Associates to review AI-generated offers
- **Feedback Loop**: Approve/Reject mechanism for adaptive learning
- **Real-time Analytics**: Pipeline metrics and eligibility counts

### 4. Mock Data (`mock_data.csv`)
Sample loyalty member and environmental data for local simulation

## Data Contracts

### Loyalty Member Schema
```json
{
  "member_id": "STRING (PK)",
  "first_name": "STRING",
  "tier": "STRING [Orange, loyalty_member, VIP]",
  "birthday": "DATE (MM-DD)",
  "nth_visit_count": "INTEGER",
  "favorite_flavor_category": "STRING [Tropical, Berry, Green, Creamy]",
  "favorite_modifier": "STRING [Whey Protein, Chia Seeds, Extra Ginger]",
  "preferred_channel": "STRING [App Push, Email]",
  "opt_in_status": "BOOLEAN"
}
```

### Environmental Signals Schema
```json
{
  "store_id": "STRING",
  "weather_condition": "STRING [Hot/Sunny, Rainy, Overcast]",
  "temperature_f": "INTEGER",
  "local_event": "STRING_OR_NULL"
}
```

## Setup & Installation

### Prerequisites
- Python 3.9+
- OpenAI API key

### Local Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/sajivejose/TropicalSmoothieAI.git
   cd TropicalSmoothieAI
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env and add your OpenAI API key
   export OPENAI_API_KEY="your-api-key-here"
   ```

5. **Run the application**
   ```bash
   streamlit run app.py
   ```

The UI will open at `http://localhost:8501`

## Execution Flow

```
mock_data.csv 
    ↓
data_processor.py (Cleansing, Deduplication, Milestone Evaluation)
    ↓
feature_engineer_prompt_context() → Feature Matrix
    ↓
ai_engine.py (PromptFactory with System Prompts & Guardrails)
    ↓
gpt-4o (JSON Mode Structured Output)
    ↓
app.py (Streamlit UI for TSC Associate Review)
    ↓
Feedback Loop (Approve/Reject → Adaptive Learning)
```

## Key Features

### 1. Milestone Detection
- Birthday-based offers
- Nth-visit milestones (e.g., 50th visit)
- Anniversary dates
- Local event triggers

### 2. Hyper-Personalization
- Flavor category preferences (Tropical, Berry, Green, Creamy)
- Modifier preferences (Whey Protein, Chia Seeds, Extra Ginger)
- Tier-based rewards (Orange, loyalty_member, VIP)
- Channel-optimized copy (App Push: 30 words max, Email: 75 words max)

### 3. Environmental Awareness
- Real-time weather conditions
- Temperature-based recommendations
- Local event integration

### 4. Brand Voice Compliance
- Vibrant, sunshine-infused tone
- No medical/health claims
- Energetic, celebratory messaging
- Consistent TSC brand identity

### 5. Feedback Loop Integration
- TSC Associate review interface
- Approval/rejection tracking
- Guardrail violation flagging
- Metrics routing for continuous improvement

## API Integration Points

The prototype is designed for seamless integration with:

1. **Loyalty Platform APIs** → Load real member data
2. **Weather Services** → Dynamic environmental triggers
3. **CRM Systems** → Distribute approved offers
4. **Analytics Pipelines** → Track feedback and performance

## Example Workflow

1. **Pipeline Load**: Read `mock_data.csv` with 1st-party and 3rd-party signals
2. **Cleansing**: Filter opt-in members, deduplicate records
3. **Milestone Check**: Detect Marcus's birthday (06-09)
4. **Feature Engineering**: Build context: "Marcus, VIP, Green smoothies with Chia Seeds, App Push channel, Hot/Sunny 88°F"
5. **AI Generation**: PromptFactory creates personalized offer via gpt-4o
6. **UI Review**: TSC Associate sees generated subject line, body copy, and bundle recommendation
7. **Feedback**: Associate approves → offer routed to CRM distribution pipeline
8. **Adaptive Learning**: Rejection flagged for guardrail analysis

## Code Structure

```
TropicalSmoothieAI/
├── mock_data.csv           # Sample loyalty and environmental data
├── data_processor.py       # Data pipeline, cleansing, milestone detection
├── ai_engine.py            # Prompt factory, LLM integration
├── app.py                  # Streamlit UI and feedback loop
├── requirements.txt        # Python dependencies
├── .env.example            # Environment variables template
└── README.md              # This file
```

## Testing

### Manual Testing

```python
# Test data pipeline
from data_processor import DataPipeline

pipeline = DataPipeline("mock_data.csv")
cleaned = pipeline.data_cleansing()
milestones = pipeline.evaluate_milestones("06-09")

# Test feature engineering
context = DataPipeline.feature_engineer_prompt_context(milestones.iloc[0].to_dict())
print(context)

# Test AI engine
from ai_engine import PromptFactory
offer = PromptFactory.generate_offer(context)
print(offer)
```

## Performance Considerations

- **Data Pipeline**: O(n) complexity for deduplication and filtering
- **LLM Calls**: ~3-5 seconds per offer generation (gpt-4o latency)
- **UI Responsiveness**: Streamlit spinner provides feedback during AI generation
- **Scalability**: Ready for batch processing with asyncio for 1000+ members

## Future Enhancements

1. **Real API Integration**: Replace mock data with live loyalty platform connections
2. **Advanced ML**: Incorporate predictive models for offer acceptance rates
3. **Multi-channel Distribution**: SMS, WhatsApp, In-app notifications
4. **A/B Testing Framework**: Systematic testing of copy variants
5. **Analytics Dashboard**: Track offer performance, redemption rates, ROI
6. **Compliance Monitoring**: Automated guardrail violation detection
7. **Batch Processing**: Process thousands of members in parallel
8. **Fallback Strategies**: Handle API failures gracefully

## Brand Voice Guidelines

✅ **DO**:
- Use vibrant, tropical emojis and language
- Celebrate milestones enthusiastically
- Reference their taste preferences naturally
- Adapt tone to weather and local context

❌ **DON'T**:
- Make medical or health claims
- Exceed word limits per channel
- Ignore consent/opt-in status
- Generic copy without personalization

## Troubleshooting

### "OpenAI API Key not found"
```bash
export OPENAI_API_KEY="your-key-here"
```

### "Module not found" errors
```bash
pip install -r requirements.txt
```

### Streamlit connection issues
```bash
streamlit run app.py --logger.level=debug
```

## Contributing

Contributions are welcome! Please follow these guidelines:
1. Create feature branches from `develop`
2. Write tests for new functionality
3. Ensure code follows PEP 8 standards
4. Update documentation with changes

## License

Proprietary - Tropical Smoothie Cafe

## Support

For questions or issues, contact the development team or open a GitHub issue.

---

**Built with ❤️ for Tropical Smoothie Cafe**