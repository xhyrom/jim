from ..base import Entity


class NumberEntity(Entity):
    WORD_TO_NUMBER = {
        "one": 1,
        "two": 2,
        "three": 3,
        "four": 4,
        "five": 5,
        "six": 6,
        "seven": 7,
        "eight": 8,
        "nine": 9,
        "ten": 10,
        "twenty": 20,
        "thirty": 30,
        "forty": 40,
        "fifty": 50,
        "hundred": 100,
        "thousand": 1000,
    }

    def process_value(self, raw_value):
        lower_value = raw_value.lower()

        if lower_value in self.WORD_TO_NUMBER:
            number = self.WORD_TO_NUMBER[lower_value]
            return {"value": number, "type": "integer", "raw": raw_value}

        try:
            if "." in raw_value:
                number = float(raw_value)
                return {"value": number, "type": "float", "raw": raw_value}
            else:
                number = int(raw_value)
                return {"value": number, "type": "integer", "raw": raw_value}
        except ValueError:
            pass

        return {"value": raw_value, "type": "unknown", "raw": raw_value}
