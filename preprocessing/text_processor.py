class TextProcessor:
    @staticmethod
    def remove_header(text: str) -> str:
        try:
            marker = "ЗАГАЛЬНА ЧАСТИНА"
            idx = text.find(marker)
            print('idx:', idx)

            if idx == -1:
                return text

            return text[idx:]
        except Exception as e:
            print(f"error while finding header marker: {e}")
            return text

    @staticmethod
    def split_main_and_footer(text: str):
        """
        splits text into: main_text: everything BEFORE 'Президент України Л.КУЧМА ...' footer_text: everything FROM 'Президент України Л.КУЧМА ...' to the end
        """

        marker = 'Президент України Л.КУЧМА'
        idx = text.find(marker)

        if idx == -1:
            raise Exception(f"Marker '{marker}' not found in text")

        main_text = text[:idx]
        footer_text = text[idx:]

        return main_text, footer_text

    @staticmethod
    def split_main_into_2_parts(main_text: str):
        marker = 'ПРИКІНЦЕВІ ТА ПЕРЕХІДНІ ПОЛОЖЕННЯ'

        idx = main_text.find(marker)

        if idx == -1:
            raise Exception(f"Marker '{marker}' not found in text")

        first_part_of_text = main_text[:idx]
        second_part_of_text = main_text[idx:]

        return first_part_of_text, second_part_of_text
