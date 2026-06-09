import os
from openai import OpenAI
import json

class PromptFactory:
    SYSTEM_PROMPT = """
    You are the Senior AI Brand Copywriter and Recommender Engine for Tropical Smoothie Cafe. 
    Your objective is to craft hyper-personalized milestone messages and dynamic item bundles based on guest attributes.

    BRAND VOICE GUARDRAILS:
    - Tone: Vibrant, sunshine-infused, celebratory, healthy, and energetic.
    - Strict Compliance: Never make medical or explicit health claims (e.g., do not say 'this cures inflammation'). Focus on refreshment and energy.
    - Copy Limits: If channel is 'App Push', limit 'body_copy' to 30 words max. If 'Email', limit to 75 words.

    OUTPUT REQUIREMENT:
    You must output strictly raw JSON matching this schema:
    {
      "subject_line": "Catchy headline with relevant tropical emojis",
      "body_copy": "Personalized celebratory milestone copy tailored to their preference and weather context",
      "recommended_bundle": "A specific drink and modifier combination matching their flavor profile"
    }
    """

    @staticmethod
    def generate_offer(context: dict) -> dict:
        client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
        
        user_content = f"""
        Guest Context:
        - Name: {context['guest_name']}
        - Tier: {context['tier_status']}
        - Milestone Event: {context['milestone']}
        - Taste Preferences: {context['taste_profile']}
        - Delivery Channel: {context['channel']}
        - Current Local Weather: {context['environmental_trigger']}
        """

        response = client.chat.completions.create(
            model="gpt-4o",
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": PromptFactory.SYSTEM_PROMPT},
                {"role": "user", "content": user_content}
            ],
            temperature=0.7  # Slight variance for creative copy while maintaining guardrails
        )
        
        return json.loads(response.choices[0].message.content)