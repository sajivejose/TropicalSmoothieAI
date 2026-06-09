import pandas as pd
from datetime import datetime

class DataPipeline:
    def __init__(self, file_path: str):
        self.df = pd.read_csv(file_path)
        self.total_records = len(self.df)
        self.opt_in_count = 0
        self.deduplicated_count = 0
        self.eligible_count = 0
        
    def data_cleansing(self):
        """Executes deduplication, PII/Consent filtering, and missing data imputation."""
        # 1. Deduplication based on Primary Key
        initial_count = len(self.df)
        self.df.drop_duplicates(subset=['member_id'], keep='first', inplace=True)
        self.deduplicated_count = len(self.df)
        
        # 2. Consent Filter (Diagram Guardrail: Consent, PII checks)
        self.df = self.df[self.df['opt_in_status'] == True]
        self.opt_in_count = len(self.df)
        
        # 3. Missing Value Imputation
        self.df['favorite_flavor_category'].fillna('Tropical', inplace=True)
        self.df['favorite_modifier'].fillna('None', inplace=True)
        return self.df

    def evaluate_milestones(self, current_date_mm_dd: str, date_range_days: int = 7):
        """
        Enhanced Milestone & eligibility logic engine with flexible date range.
        
        Triggers:
        1. Birthday within date_range_days (default 7 days)
        2. Visit count thresholds (10, 25, 50, 100, 150, 200+)
        3. Hot weather + Tropical/Berry preferences
        4. New members (< 5 visits) for acquisition campaigns
        """
        active_offers = []
        
        # Parse current date
        current_month_day = current_date_mm_dd  # Format: MM-DD
        
        for _, row in self.df.iterrows():
            triggers = []
            
            # Trigger 1: Birthday within window
            if self._is_birthday_near(row['birthday'], current_month_day, date_range_days):
                triggers.append("Birthday Celebration")
            
            # Trigger 2: Visit milestones
            visit_trigger = self._check_visit_milestone(row['nth_visit_count'])
            if visit_trigger:
                triggers.append(visit_trigger)
            
            # Trigger 3: Weather-based
            if row['weather_condition'] in ['Hot/Sunny', 'Rainy'] and \
               row['favorite_flavor_category'] in ['Tropical', 'Berry']:
                triggers.append("Weather-Triggered Offer")
            
            # Trigger 4: New member acquisition
            if row['nth_visit_count'] < 5 and row['tier'] == 'loyalty_member':
                triggers.append("New Member Incentive")
            
            # Add to eligible if any trigger matched
            if triggers:
                offer_row = row.to_dict()
                offer_row['milestone_trigger'] = " + ".join(triggers)
                active_offers.append(offer_row)
        
        self.eligible_count = len(active_offers)
        return pd.DataFrame(active_offers)
    
    @staticmethod
    def _is_birthday_near(birthday: str, current_date: str, days_range: int = 7) -> bool:
        """
        Check if birthday is within date_range of current date.
        Handles month wraparound (e.g., Dec 30 near Jan 2)
        """
        try:
            birth_month, birth_day = map(int, birthday.split('-'))
            curr_month, curr_day = map(int, current_date.split('-'))
            
            # Simple check: within ±days_range
            for offset in range(-days_range, days_range + 1):
                check_day = curr_day + offset
                check_month = curr_month
                
                # Handle month boundaries
                if check_day < 1:
                    check_month -= 1
                    if check_month < 1:
                        check_month = 12
                    check_day += 31
                elif check_day > 31:
                    check_month += 1
                    if check_month > 12:
                        check_month = 1
                    check_day -= 31
                
                if birth_month == check_month and birth_day == check_day:
                    return True
            return False
        except:
            return False
    
    @staticmethod
    def _check_visit_milestone(visit_count: int) -> str:
        """
        Check if visit count triggers a milestone offer.
        """
        milestones = {
            200: "Diamond Tier (200+ Visits)",
            150: "Platinum Tier (150+ Visits)",
            100: "Gold Tier (100+ Visits)",
            50: "Silver Tier (50+ Visits)",
            25: "Bronze Tier (25+ Visits)",
            10: "Bronze Tier (10+ Visits)"
        }
        
        for threshold in sorted(milestones.keys(), reverse=True):
            if visit_count >= threshold:
                return milestones[threshold]
        return None

    @staticmethod
    def feature_engineer_prompt_context(guest_row: dict) -> dict:
        """Transforms structured attributes explicitly for the LLM context."""
        return {
            "guest_name": guest_row['first_name'],
            "tier_status": guest_row['tier'],
            "milestone": guest_row['milestone_trigger'],
            "visit_count": int(guest_row['nth_visit_count']),
            "taste_profile": f"{guest_row['favorite_flavor_category']} profiles with {guest_row['favorite_modifier']}",
            "channel": guest_row['preferred_channel'],
            "environmental_trigger": f"{guest_row['weather_condition']} and {guest_row['temperature_f']}°F"
        }
    
    def get_pipeline_stats(self) -> dict:
        """Return data quality and pipeline statistics."""
        return {
            "total_records": self.total_records,
            "after_deduplication": self.deduplicated_count,
            "opt_in_count": self.opt_in_count,
            "opt_out_count": self.deduplicated_count - self.opt_in_count,
            "eligible_offers": self.eligible_count,
            "eligibility_rate": f"{(self.eligible_count / self.opt_in_count * 100):.1f}%" if self.opt_in_count > 0 else "0%"
        }