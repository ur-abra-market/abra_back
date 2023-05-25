from __future__ import annotations

import stringcase


def snake_case_to_camel_case_alias_generator(string: str) -> str:
    return stringcase.camelcase(string)
