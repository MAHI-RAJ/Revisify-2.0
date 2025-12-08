import re

class AntiSpoonfeedFilter:
    """Filter to prevent full solutions in hint mode"""
    
    def __init__(self):
        # Patterns that indicate full solutions
        self.solution_indicators = [
            r"the answer is",
            r"the correct answer",
            r"here's the solution",
            r"the final answer",
            r"answer:\s*[A-D]",
            r"solution:\s*",
            r"therefore.*answer",
            r"thus.*answer",
            r"hence.*answer"
        ]
        
        # Phrases that should be removed or replaced
        self.spoonfeed_phrases = [
            (r"the answer is\s+[A-D]", "think about which option makes sense"),
            (r"the correct answer is\s+[A-D]", "consider which option aligns with the concept"),
            (r"here's the solution:", "here's a hint:"),
            (r"the final answer", "a possible approach")
        ]
    
    def filter_hint(self, text):
        """
        Filter hint text to remove full solutions
        
        Args:
            text: Hint text to filter
        
        Returns:
            Filtered text
        """
        if not text:
            return text
        
        filtered = text
        
        # Replace spoonfeed phrases
        for pattern, replacement in self.spoonfeed_phrases:
            filtered = re.sub(pattern, replacement, filtered, flags=re.IGNORECASE)
        
        # Check for solution indicators
        for indicator in self.solution_indicators:
            if re.search(indicator, filtered, re.IGNORECASE):
                # Remove or modify the solution part
                # Try to keep the hint part but remove the answer
                sentences = filtered.split(".")
                filtered_sentences = []
                for sentence in sentences:
                    if not re.search(indicator, sentence, re.IGNORECASE):
                        filtered_sentences.append(sentence)
                    else:
                        # Replace with guiding phrase
                        filtered_sentences.append("Consider what you know about this concept.")
                filtered = ". ".join(filtered_sentences)
        
        # Ensure hint doesn't end with explicit answers
        filtered = self._remove_trailing_answer(filtered)
        
        return filtered.strip()
    
    def _remove_trailing_answer(self, text):
        """Remove trailing answer statements"""
        # Check last sentence for answer patterns
        sentences = text.split(".")
        if len(sentences) > 1:
            last_sentence = sentences[-1].strip()
            for indicator in self.solution_indicators:
                if re.search(indicator, last_sentence, re.IGNORECASE):
                    # Remove last sentence or replace with guiding phrase
                    sentences = sentences[:-1]
                    sentences.append("What connections can you make?")
                    return ". ".join(sentences)
        
        return text
    
    def validate_hint(self, text):
        """
        Validate that hint doesn't contain full solutions
        
        Returns:
            tuple: (is_valid, issues)
        """
        issues = []
        
        for indicator in self.solution_indicators:
            if re.search(indicator, text, re.IGNORECASE):
                issues.append(f"Contains solution indicator: {indicator}")
        
        # Check for direct answer options
        if re.search(r"\b([A-D])\s+is\s+(correct|right|the answer)", text, re.IGNORECASE):
            issues.append("Contains direct answer statement")
        
        return (len(issues) == 0, issues)

