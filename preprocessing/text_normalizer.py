import re


class TextNormalizer:
    @staticmethod
    def normalize_apostrophes(text: str) -> str:
        text = text.replace("'", "’")
        text = text.replace("ʼ", "’")

        return text

    @staticmethod
    def fix_line_breaks(text: str) -> str:
        # PROTECT article headers FIRST (THIS WAS MISSING)
        text = re.sub(
            r"(Стаття\s+\d+(?:-\d+)?\.)",
            r"\n\1\n",
            text
        )

        # Fix hyphenated words split over lines
        text = re.sub(r"(\w+)-\s*\n\s*(\w+)", r"\1-\2", text)

        # Join lines broken mid-sentence (now SAFE)
        text = re.sub(
            r"([^\n])\n(?!\s*(Стаття\s+\d+|Розділ\s+[IVXLC]+|ЗАГАЛЬНА ЧАСТИНА|ОСОБЛИВА ЧАСТИНА))",
            r"\1 ",
            text
        )

        # Clean up spaces
        text = re.sub(r" +\n", "\n", text)
        text = re.sub(r"\n +", "\n", text)
        text = re.sub(r"  +", " ", text)

        return text

    @staticmethod
    def enforce_headings(text: str) -> str:
        # Major parts
        text = re.sub(r"\s*(ЗАГАЛЬНА ЧАСТИНА|ОСОБЛИВА ЧАСТИНА|ПЕРЕХІДНІ ТА ПРИКІНЦЕВІ ПОЛОЖЕННЯ)\s*", r"\n\n\1\n\n",
                      text)

        # Normalize article numbers like "336 - 1" → "336-1"
        text = re.sub(
            r"(Стаття\s+\d+(?:-\d+)?\.)",
            r"\n\1\n",
            text
        )

        # Sections (only if NOT preceded by "{")
        text = re.sub(r"(?<!\{)\s*(Розділ [IVXLC]+(?:\s*-\s*\d+)?)\s*\.?\s*", r"\n\1\n", text)

        # Section titles (ALL CAPS) - ensure they're on their own line
        text = re.sub(r"([А-ЯІЇЄҐ][А-ЯІЇЄҐ\s,]{3,})\s+(Стаття|\{)", r"\1\n\n\2", text)

        # Articles - newline before Стаття that has a title (not just deletion notes)
        text = re.sub(r"(\})\s*(Стаття \d+[-\d]*\.\s+[А-ЯІЇЄҐА-я])", r"\1\n\2", text)
        text = re.sub(r"\s*(Стаття \d+[-\d]*\.)\s+([А-ЯІЇЄҐ])", r"\n\1 \2", text)

        # Cleanup
        text = re.sub(r"\n{3,}", "\n\n", text)

        return text.strip()
