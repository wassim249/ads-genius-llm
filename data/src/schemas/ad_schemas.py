"""Pydantic schemas for data validation in the ad generation pipeline."""

from pydantic import BaseModel, Field


class DataEntry(BaseModel):
    """Schema for a single ad data entry."""

    prompt: str = Field(
        description="User-generated prompt for ad creation, describing a specific product and its unique features in 1-4 sentences."
    )
    ad_text: str = Field(
        description="Generated ad text, highlighting key selling points and a call to action, using emojis and markdown for emphasis, should sound human-like."
    )


class DataEntryList(BaseModel):
    """Schema for a list of ad data entries."""

    entries: list[DataEntry] = Field(description="A list of data entries for ad generation")


# Example data for few-shot learning
EXAMPLE_DATA = [
    DataEntryList(
        entries=[
            DataEntry(
                prompt="Hey I want an ad for my new AI-powered keyboard called Keyboard.AI that not only enhances typing speed and accuracy but also features customizable backlighting, ergonomic design, and seamless integration with popular software applications. This keyboard learns from your typing habits to provide personalized shortcuts and suggestions, making it the ultimate tool for both casual users and professionals alike.",
                ad_text="""Transform Your Typing Forever 🎯\n\nIntroducing KeyGenius AI: Where Speed Meets Intelligence\n\n\"I never knew typing could feel this effortless\" - Tech Weekly\n\nYour keyboard isn't just a tool anymore. It's your partner in productivity.\n\n→ 3X Faster Typing Speed\n→ 98% Reduction in Errors\n→ 85% of Users Report Better Workflow\n\nWhat Makes KeyGenius Different:\n\n• Learns YOUR Style: Adapts to how YOU write, not the other way around\n• Real-Time Enhancement: Suggests better phrasing as you type\n• Smart Context: Understands your industry jargon and terminology\n• Zero Learning Curve: Start typing faster from day one\n\nLimited Time Launch Offer:\n✓ 60-Day Money-Back Guarantee\n✓ Free Premium Features for 3 Months\n✓ Priority Customer Support\n\nJoin 10,000+ Early Adopters Already Typing Smarter\n\n⚡ SAVE 40% TODAY ONLY ⚡\n\nClick Now to Upgrade Your Typing Experience\n[Order Now]\n\n\"Best keyboard innovation since mechanical switches\" - TechPro Magazine\n\n#WorkSmarter #ProductivityTools #AIKeyboard""",
            )
        ]
    ),
    DataEntryList(
        entries=[
            DataEntry(
                prompt="Can you create an ad for my new fitness app called FitOverAll that helps users stay in shape at home?",
                ad_text="""💪 Your Body, Your Time, Your Results!\n\nIntroducing FitAI: The Home Fitness Revolution!\n\n\"Finally, a fitness app that truly understands my schedule!\" - Sarah M., Lost 30 lbs\n\n🔥 Users are averaging 12 lbs lost in just 30 days!\n🔥 92% of users stick to their program!\n🔥 Enjoy 15-45 minute workouts that fit YOUR schedule!\n\nWhy FitAI is a Game Changer:\n\n• AI crafts your perfect workout based on your goals, space, and equipment.\n• Get real-time form correction, just like having a personal trainer, 24/7!\n• Experience progressive evolution: your workout adapts as you do.\n• Nutrition made easy with meal plans tailored to your lifestyle.\n\nProven Results:\n→ Over 50,000 active users!\n→ 4.9⭐ rating on the App Store!\n→ Featured in Women's Health & Men's Fitness!\n\nLaunch Special:\n✓ Enjoy a 30-day free trial!\n✓ Personal goal-setting session included!\n✓ Access to our premium workout library!\n\nStart your transformation today!\n\n⚡ CLAIM YOUR FREE MONTH NOW! ⚡\n\nTap to kickstart your fitness journey!\n[Download Now]\n\n\"The only fitness app that kept me consistent!\" - Mike R., 90-Day Success Story\n\n#FitnessMadeSimple #HomeWorkouts #HealthyLifestyle""",
            )
        ]
    ),
]
