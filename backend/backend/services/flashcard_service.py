"""Flashcard generation service"""
from extensions import db
from models import Flashcard
from integrations.llm_client import LLMClient


class FlashcardService:
    """Generate and retrieve flashcards"""

    def __init__(self):
        self.llm_client = LLMClient()

    def get_or_generate_flashcards(self, roadmap_step_id, concept_name, concept_description, count=5):
        """Return existing flashcards or generate new ones"""
        existing = Flashcard.query.filter_by(roadmap_step_id=roadmap_step_id).order_by(Flashcard.card_order).all()
        if existing:
            return [
                {"id": card.id, "front": card.front, "back": card.back, "order": card.card_order}
                for card in existing
            ]

        cards_data = self.llm_client.generate_flashcards(
            concept_name=concept_name,
            concept_description=concept_description,
            num_cards=count
        )

        flashcards = []
        for idx, card in enumerate(cards_data):
            fc = Flashcard(
                roadmap_step_id=roadmap_step_id,
                front=card.get("front", ""),
                back=card.get("back", ""),
                card_order=idx
            )
            db.session.add(fc)
            flashcards.append(fc)

        db.session.commit()
        return [
            {"id": card.id, "front": card.front, "back": card.back, "order": card.card_order}
            for card in flashcards
        ]

