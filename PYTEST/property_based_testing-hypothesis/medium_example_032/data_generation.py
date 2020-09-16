from typing import Dict, Optional, List
from dataclasses import dataclass
from hypothesis import strategies as st


@dataclass
class PdfInfo:
    path: str
    is_errornous: bool
    is_encrypted: bool
    nb_pages: int
    nb_toc_top_level: int
    nb_characters: int
    user_attributes: Dict[str, Optional[str]]
    user_data: List[int]


if __name__ == '__main__':
    # Usage in test to generate one PdfInfo:
    # @given(st.builds(PdfInfo))

    # Now show some samples:
    for _ in range(10):
        print(st.builds(PdfInfo).example())
