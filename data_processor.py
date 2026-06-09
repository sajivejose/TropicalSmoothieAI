import pandas as pd
from datetime import datetime

class DataPipeline:
    def __init__(self, file_path: str):
        self.df = pd.read_csv(file_path)
        
    def data_cleansing(self):
        """Executes deduplication, PII/Consent filtering, and missing data imputation."""
        # 1. Deduplication based on Primary Key
        self.df.drop_duplicates(subset=['member_id'], keep='first', inplace=True)
        
        # 2. Consent Filter (Diagram Guardrail: Consent, PII checks)
        self.df = self.df[self.df['opt_in_status'] == True]
        
        # 3. Missing Value Imputation
        self.df['favorite_flavor_category'].fillna('Tropical', inplace=True)
        self.df['favorite_modifier'].fillna('None', inplace=True)
        return self.df

    def evaluate_milestones(self, current_date_mm_dd: str):
        """Milestone & eligibility logic engine."""
        active_offers = []
        for _, row in self.df.iterrows():
            trigger = None
            # Check Birthday
            if row['birthday'] == current_date_mm_dd:
                trigger = "Birthday"
            # Check Nth Visit Threshold (e.g., hitting the 50th visit milestone)
            elif row['nth_visit_count'] == 49: 
                trigger = "Nth-Visit (50th Near)"
                
            if trigger:
                active_offers.append({**row.to_dict(), "milestone_trigger": trigger})
        return pd.DataFrame(active_offers)

    @staticmethod
    def feature_engineer_prompt_context(guest_row: dict) -> dict:
        """Transforms structured attributes explicitly for the LLM context."""
        return {
            "guest_name": guest_row['first_name'],
            "tier_status": guest_row['tier'],
            "milestone": guest_row['milestone_trigger'],
            "taste_profile": f"{guest_row['favorite_flavor_category']} profiles with {guest_row['favorite_modifier']}",
            "channel": guest_row['preferred_channel'],
            "environmental_trigger": f"{guest_row['weather_condition']} and {guest_row['temperature_f']}°F"
        }