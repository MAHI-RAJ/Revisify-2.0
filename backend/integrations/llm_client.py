import os
import json
from config import Config

class LLMClient:
    """Unified client for all LLM operations"""
    
    def __init__(self):
        self.provider = Config.LLM_PROVIDER
        self.api_key = Config.LLM_API_KEY or os.environ.get("LLM_API_KEY")
        self.model = Config.LLM_MODEL
        self.temperature = Config.LLM_TEMPERATURE
        self.max_tokens = Config.LLM_MAX_TOKENS
        
        if not self.api_key:
            raise ValueError("LLM_API_KEY not set in environment or config")
    
    def _call_llm(self, prompt, system_prompt=None, temperature=None):
        """
        Generic LLM call method
        
        Args:
            prompt: User prompt
            system_prompt: Optional system prompt
            temperature: Optional temperature override
        
        Returns:
            str: LLM response text
        """
        if self.provider == "openai":
            return self._call_openai(prompt, system_prompt, temperature)
        elif self.provider == "anthropic":
            return self._call_anthropic(prompt, system_prompt, temperature)
        else:
            raise ValueError(f"Unsupported LLM provider: {self.provider}")
    
    def _call_openai(self, prompt, system_prompt=None, temperature=None):
        """Call OpenAI API"""
        try:
            import openai
            client = openai.OpenAI(api_key=self.api_key)
            
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})
            
            response = client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature or self.temperature,
                max_tokens=self.max_tokens
            )
            
            return response.choices[0].message.content
        except ImportError:
            raise ImportError("openai package not installed. Install with: pip install openai")
        except Exception as e:
            raise Exception(f"OpenAI API error: {str(e)}")
    
    def _call_anthropic(self, prompt, system_prompt=None, temperature=None):
        """Call Anthropic (Claude) API"""
        try:
            import anthropic
            client = anthropic.Anthropic(api_key=self.api_key)
            
            system_msg = system_prompt or ""
            
            response = client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                temperature=temperature or self.temperature,
                system=system_msg,
                messages=[{"role": "user", "content": prompt}]
            )
            
            return response.content[0].text
        except ImportError:
            raise ImportError("anthropic package not installed. Install with: pip install anthropic")
        except Exception as e:
            raise Exception(f"Anthropic API error: {str(e)}")
    
    def extract_concepts(self, raw_text):
        """
        Extract key concepts from document text
        
        Returns:
            List of dicts with 'name' and 'description'
        """
        system_prompt = """You are an expert at analyzing educational content and extracting key concepts.
        Identify the main concepts, topics, or learning objectives from the provided text.
        Return a JSON array of objects, each with 'name' (concept name) and 'description' (brief explanation).
        Extract 10-20 key concepts. Be specific and avoid duplicates."""
        
        prompt = f"""Extract key concepts from the following document text:

{raw_text[:8000]}  # Limit context

Return ONLY a valid JSON array, no additional text:
[
  {{"name": "Concept Name", "description": "Brief description"}},
  ...
]"""
        
        response = self._call_llm(prompt, system_prompt)
        
        # Parse JSON response
        try:
            # Extract JSON from response (handle markdown code blocks)
            if "```json" in response:
                response = response.split("```json")[1].split("```")[0].strip()
            elif "```" in response:
                response = response.split("```")[1].split("```")[0].strip()
            
            concepts = json.loads(response)
            if isinstance(concepts, list):
                return concepts
            else:
                return []
        except json.JSONDecodeError:
            # Fallback: try to extract concepts from text
            return self._fallback_extract_concepts(response)
    
    def _fallback_extract_concepts(self, text):
        """Fallback extraction if JSON parsing fails"""
        # Simple fallback - split by lines and extract
        concepts = []
        for line in text.split("\n"):
            line = line.strip()
            if line and len(line) > 3:
                concepts.append({"name": line, "description": ""})
        return concepts[:20]  # Limit
    
    def infer_prerequisites(self, concept_name, concept_description, all_concepts):
        """
        Infer prerequisites for a concept
        
        Args:
            concept_name: Name of the concept
            concept_description: Description of the concept
            all_concepts: List of all concept names in the document
        
        Returns:
            List of prerequisite concept names (2-4 items)
        """
        system_prompt = """You are an expert at analyzing learning dependencies.
        Given a concept and a list of available concepts, identify which concepts are prerequisites.
        Prerequisites are foundational concepts that must be understood before learning the target concept.
        Return 2-4 prerequisite names from the provided list."""
        
        prompt = f"""Concept: {concept_name}
Description: {concept_description}

Available concepts: {', '.join(all_concepts[:50])}  # Limit list

Identify 2-4 prerequisites for "{concept_name}" from the available concepts.
Return ONLY a JSON array of concept names, no additional text:
["Prerequisite 1", "Prerequisite 2", ...]"""
        
        response = self._call_llm(prompt, system_prompt)
        
        try:
            if "```json" in response:
                response = response.split("```json")[1].split("```")[0].strip()
            elif "```" in response:
                response = response.split("```")[1].split("```")[0].strip()
            
            prereqs = json.loads(response)
            if isinstance(prereqs, list):
                # Filter to only include concepts that exist in all_concepts
                return [p for p in prereqs if p in all_concepts][:4]
            return []
        except json.JSONDecodeError:
            # Fallback: extract from text
            prereqs = []
            for concept in all_concepts:
                if concept.lower() in response.lower() and concept != concept_name:
                    prereqs.append(concept)
            return prereqs[:4]
    
    def generate_mcqs(self, concept_name, concept_description, document_context="", num_questions=7):
        """
        Generate multiple choice questions for a concept
        
        Returns:
            List of dicts with 'question', 'options' (dict), 'correct_answer', 'explanation'
        """
        system_prompt = """You are an expert at creating educational multiple-choice questions.
        Create clear, well-structured MCQs that test understanding of the concept.
        Each question should have 4 options (A, B, C, D) with exactly one correct answer.
        Include a brief explanation for the correct answer."""
        
        context_snippet = document_context[:2000] if document_context else ""
        
        prompt = f"""Generate {num_questions} multiple-choice questions about: {concept_name}

Description: {concept_description}

Context from document:
{context_snippet}

Return ONLY a valid JSON array:
[
  {{
    "question": "Question text?",
    "options": {{"A": "Option A", "B": "Option B", "C": "Option C", "D": "Option D"}},
    "correct_answer": "A",
    "explanation": "Brief explanation"
  }},
  ...
]"""
        
        response = self._call_llm(prompt, system_prompt)
        
        try:
            if "```json" in response:
                response = response.split("```json")[1].split("```")[0].strip()
            elif "```" in response:
                response = response.split("```")[1].split("```")[0].strip()
            
            mcqs = json.loads(response)
            if isinstance(mcqs, list):
                return mcqs
            return []
        except json.JSONDecodeError:
            return []
    
    def generate_hint(self, concept_name, concept_description, hint_number, question_context="", previous_hints=None):
        """
        Generate a Socratic hint with micro-question
        
        Returns:
            Dict with 'hint' and 'micro_question'
        """
        system_prompt = """You are a Socratic tutor. Provide hints that guide thinking, not answers.
        Give a brief hint that points the learner in the right direction, followed by a micro-question
        that encourages them to think deeper. NEVER provide the full solution or final answer."""
        
        prev_hints_text = ""
        if previous_hints:
            prev_hints_text = "\nPrevious hints:\n" + "\n".join([
                f"Hint {h['hint_number']}: {h['hint']}"
                for h in previous_hints
            ])
        
        prompt = f"""Concept: {concept_name}
Description: {concept_description}

User's question/struggle: {question_context or 'General understanding'}

{prev_hints_text}

Generate hint #{hint_number} (Socratic style - guide, don't give answers).
Return ONLY a JSON object:
{{
  "hint": "Brief guiding hint (1-2 sentences)",
  "micro_question": "A thought-provoking micro-question to encourage reflection"
}}"""
        
        response = self._call_llm(prompt, system_prompt)
        
        try:
            if "```json" in response:
                response = response.split("```json")[1].split("```")[0].strip()
            elif "```" in response:
                response = response.split("```")[1].split("```")[0].strip()
            
            hint_data = json.loads(response)
            return hint_data
        except json.JSONDecodeError:
            return {
                "hint": "Think about the key principles involved. What foundational knowledge applies here?",
                "micro_question": "What connections can you make between this concept and what you already know?"
            }
    
    def generate_notes(self, concept_name, concept_description, document_context=""):
        """
        Generate full explanation notes for a concept
        
        Returns:
            Dict with 'summary' and 'explanation'
        """
        system_prompt = """You are an expert educator. Create comprehensive, clear explanations
        that help learners fully understand a concept. Include examples and key takeaways."""
        
        context_snippet = document_context[:3000] if document_context else ""
        
        prompt = f"""Create comprehensive notes for: {concept_name}

Description: {concept_description}

Context from document:
{context_snippet}

Return ONLY a JSON object:
{{
  "summary": "Brief 2-3 sentence summary",
  "explanation": "Detailed explanation with examples and key points"
}}"""
        
        response = self._call_llm(prompt, system_prompt)
        
        try:
            if "```json" in response:
                response = response.split("```json")[1].split("```")[0].strip()
            elif "```" in response:
                response = response.split("```")[1].split("```")[0].strip()
            
            notes = json.loads(response)
            return notes
        except json.JSONDecodeError:
            return {
                "summary": f"{concept_name} is an important concept that builds on foundational knowledge.",
                "explanation": f"Detailed explanation of {concept_name}: {concept_description}"
            }
    
    def generate_flashcards(self, concept_name, concept_description, num_cards=5):
        """
        Generate flashcards for a concept
        
        Returns:
            List of dicts with 'front' and 'back'
        """
        system_prompt = """Create educational flashcards with clear questions and concise answers."""
        
        prompt = f"""Create {num_cards} flashcards for: {concept_name}

Description: {concept_description}

Return ONLY a JSON array:
[
  {{"front": "Question or term", "back": "Answer or definition"}},
  ...
]"""
        
        response = self._call_llm(prompt, system_prompt)
        
        try:
            if "```json" in response:
                response = response.split("```json")[1].split("```")[0].strip()
            elif "```" in response:
                response = response.split("```")[1].split("```")[0].strip()
            
            cards = json.loads(response)
            if isinstance(cards, list):
                return cards
            return []
        except json.JSONDecodeError:
            return []
    
    def rag_answer(self, question, context_chunks):
        """
        Generate RAG answer with citations
        
        Args:
            question: User's question
            context_chunks: List of dicts with 'text', 'page', 'chunk_id'
        
        Returns:
            Dict with 'answer' and 'citations'
        """
        system_prompt = """You are a helpful tutor answering questions based on provided document context.
        Always ground your answers in the provided context. Cite specific pages/chunks when referencing information."""
        
        context_text = "\n\n---\n\n".join([
            f"[Page {chunk.get('page', 'N/A')}, Chunk {chunk.get('chunk_id', 'N/A')}]\n{chunk.get('text', '')}"
            for chunk in context_chunks
        ])
        
        prompt = f"""Question: {question}

Document context:
{context_text}

Provide a clear, accurate answer based on the context above.
Include citations in the format: [Page X, Chunk Y] when referencing specific information.

Return ONLY a JSON object:
{{
  "answer": "Your answer with inline citations like [Page 1, Chunk 2]",
  "citations": [
    {{"page": 1, "chunk_id": 2, "snippet": "relevant text snippet"}},
    ...
  ]
}}"""
        
        response = self._call_llm(prompt, system_prompt)
        
        try:
            if "```json" in response:
                response = response.split("```json")[1].split("```")[0].strip()
            elif "```" in response:
                response = response.split("```")[1].split("```")[0].strip()
            
            answer_data = json.loads(response)
            return answer_data
        except json.JSONDecodeError:
            # Fallback: return answer without structured citations
            return {
                "answer": response,
                "citations": [{"page": chunk.get("page", "N/A"), "chunk_id": chunk.get("chunk_id", "N/A"), "snippet": chunk.get("text", "")[:100]} for chunk in context_chunks[:3]]
            }

