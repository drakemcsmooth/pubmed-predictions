from typing import List, Set, Optional, Callable
from collections import Counter

from analysis.data_processing_utils import DASH, SPACE, SLASH
import logging

log = logging.getLogger(__name__)


class TokenProcessor:
    MIN_TOKEN_LENGTH = 3

    filter_chars = {
        ".", ",", ";", "%",
        "(", ")", "[", "]",
        u"\xa0", u"\u2009", u"\u200a",
    }

    replacement_chars = [
        ("α", "a"), ("β", "B"),

        ("₀", "0"), ("₁", "1"), ("₂", "2"), ("₃", "3"), ("₄", "4"),
        ("₅", "5"), ("₆", "6"), ("₇", "7"), ("₈", "8"), ("₉", "9"),
        ("₍", "("), ("₎", ")"), ("₊", "+"), ("₋", "-"), ("₌", "="),

        ("⁰", "0"), ("¹", "1"), ("²", "2"), ("³", "3"), ("⁴", "4"),
        ("⁵", "5"), ("⁶", "6"), ("⁷", "7"), ("⁸", "8"), ("⁹", "9"),
        ("⁺", "+"), ("⁻", "-"), ("⁼", "="), ("⁽", "("), ("⁾", ")"),
        ("ⁱ", "i"), ("ⁿ", "n"),

    ]

    def __init__(self, filter_words: Set[str], lemmatize: Optional[Callable] = None):
        self.filter_words = filter_words
        self.lemmatize = lemmatize

    @classmethod
    def is_numeric(cls, s: str) -> bool:
        try:
            float(s)
            return True
        except ValueError:
            return False

    @classmethod
    def is_mixed_case(cls, s: str) -> bool:
        if s.isupper() or s[1:].islower():
            return False
        return True

    @classmethod
    def is_capitalization_idiomatic(cls, s: str) -> bool:
        if s.isupper() or cls.is_mixed_case(s):
            return True
        return False

    @classmethod
    def is_date_like(cls, s: str) -> bool:
        if SLASH in s:
            return all(term.isdigit() for term in s.split(SLASH))
        elif DASH in s and s.count(DASH) < 3:
            return all(term.isdigit() for term in s.split(DASH))
        else:
            return False

    @classmethod
    def filter_dashes(cls, s: str) -> str:
        return s.replace(DASH, "")

    def extract(self, s: str) -> Counter:
        min_token_length = self.MIN_TOKEN_LENGTH
        filter_words = self.filter_words

        terms = Counter()

        for token in self._tokenize(s):
            if len(token) < min_token_length:
                continue

            # exclude numbers (integer and floating-point)
            if self.is_numeric(token):
                continue

            # exclude dates
            if self.is_date_like(token):
                continue

            lower_token = token.lower()
            lemmatized_token = self.lemmatize(lower_token) if self.lemmatize else None

            if self.is_capitalization_idiomatic(token):
                terms[token] += 1

                terms[lower_token] += 1

                if self.lemmatize and lemmatized_token != lower_token:
                    terms[lemmatized_token] += 1

            elif lower_token not in filter_words:
                terms[lower_token] += 1

                if self.lemmatize and lemmatized_token != lower_token:
                    terms[lemmatized_token] += 1

        return terms

    def _tokenize(self, s: str) -> List[str]:
        tokens = []
        # remove uninformative characters
        for char in self.filter_chars:
            s = s.replace(char, SPACE)

        # replace special (e.g., Latin or Greek) characters with common variant
        for char_from, char_to in self.replacement_chars:
            s = s.replace(char_from, char_to)

        tokens.extend(w.strip() for w in s.split(SPACE))

        # if the token has dashes, add each sub-term for processing
        if DASH in s:
            dashed_tokens = [w.strip() for w in s.split(DASH)]
            tokens.extend(w for w in dashed_tokens if w)

        return tokens
