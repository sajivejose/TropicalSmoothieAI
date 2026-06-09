import os
import json
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()

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
    def get_client():
        """Returns OpenAI client configured for either OpenAI API or local Ollama."""
        use_ollama = os.environ.get("USE_OLLAMA", "true").lower() == "true"
        
        print(f"[DEBUG] USE_OLLAMA: {use_ollama}")
        
        if use_ollama:
            # Use local Ollama server
            print("[INFO] Using Ollama (local)")
            return OpenAI(
                api_key="ollama",  # Dummy key for local Ollama
                base_url="http://localhost:11434/v1"
            ), "ollama"
        else:
            # Use OpenAI API
            api_key = os.environ.get("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("OPENAI_API_KEY not set and USE_OLLAMA is false")
            print("[INFO] Using OpenAI API")
            return OpenAI(api_key=api_key), "openai"

    @staticmethod
    def generate_offer(context: dict) -> dict:
        client, provider = PromptFactory.get_client()
        
        # Select model based on provider
        if provider == "ollama":
            model = os.environ.get("OLLAMA_MODEL", "mistral")
        else:
            model = "gpt-4o"
        
        user_content = f"""
        Guest Context:
        - Name: {context['guest_name']}
        - Tier: {context['tier_status']}
        - Milestone Event: {context['milestone']}
        - Taste Preferences: {context['taste_profile']}
        - Delivery Channel: {context['channel']}
        - Current Local Weather: {context['environmental_trigger']}
        """

        try:
            print(f"[INFO] Generating offer using {provider} ({model})...")
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": PromptFactory.SYSTEM_PROMPT},
                    {"role": "user", "content": user_content}
                ],
                temperature=0.7  # Slight variance for creative copy while maintaining guardrails
            )
            
            # Parse the response
            response_text = response.choices[0].message.content
            
            # Try to extract JSON from the response
            try:
                return json.loads(response_text)
            except json.JSONDecodeError:
                # If response is not valid JSON, wrap it gracefully
                return {
                    "subject_line": "🌴 Special Milestone Offer Just for You! 🌴",
                    "body_copy": response_text[:75],  # Truncate to fit
                    "recommended_bundle": "Green Smoothie with Chia Seeds"
                }
                
        except Exception as e:
            print(f"[ERROR] Error calling {provider}: {str(e)}")
            # Return mock data on error
            return {
                "subject_line": "🌴 Celebrate Your Milestone! 🌴",
                "body_copy": f"We're thrilled to celebrate {context['guest_name']}! Enjoy a special reward on us.",
                "recommended_bundle": f"{context['taste_profile']} Smoothie - Your Favorite!"
            }
