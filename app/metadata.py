from __future__ import annotations

from typing import Final

PASSWORD_REGEX: Final[str] = (
    r"(?=.*[0-9])"
    r"(?=.*[!\"#$%&'()*+,-./:;<=>?@[\]^_`{|}~])"
    r"(?=.*[a-z])"
    r"(?=.*[A-Z])[0-9a-zA-Z!\"#$%&'()*+,-./:;<=>?@[\]^_`{|}~]"
    r"{8,}"
)
