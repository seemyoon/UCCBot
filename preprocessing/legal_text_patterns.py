import re


class LegalTextPatterns:
    PART_PATTERN = re.compile(
        r"(ЗАГАЛЬНА ЧАСТИНА|ОСОБЛИВА ЧАСТИНА|ПРИКІНЦЕВІ ТА ПЕРЕХІДНІ ПОЛОЖЕННЯ)"
    )

    SECTION_PATTERN_MAIN_PART = re.compile(
        r"(?m)^\s*(Розділ [IVXLC]+)\s*$"
    )

    SECTION_PATTERN_ADDITIONAL_PART = re.compile(
        r"""
        ^\s*(Розділ\s+[IVXLC]+)\s*$   # section header on its own line
        \s*                            # skip any whitespace/newlines
        (.*?)(?=^\s*Розділ\s+[IVXLC]+|\Z)  # capture body until next section or end
        """,
        re.MULTILINE | re.DOTALL | re.VERBOSE
    )

    ARTICLE_PATTERN_MAIN_PART = re.compile(
        r"""
        (?ms)
        ^\s*Стаття\s+
        (?P<number>\d+(?:-\d+)?)\.\s*
        (?P<title>[^\n]+)
        \n+
        (?P<body>.*?)
        (?=^\s*Стаття\s+\d+(?:-\d+)?\.|\Z)
        """,
        re.VERBOSE
    )
