from __future__ import annotations

from typing import Final, Pattern

PASSWORD_REGEX: Final[
    Pattern
] = r"(?=.*[0-9])(?=.*[!\"#$%&'()*+,-./:;<=>?@[\]^_`{|}~])(?=.*[a-z])(?=.*[A-Z])[0-9a-zA-Z!\"#$%&'()*+,-./:;<=>?@[\]^_`{|}~]{8,}"
