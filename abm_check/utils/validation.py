"""Validation utility functions."""
import re
from abm_check.domain.exceptions import InvalidProgramIdError

def validate_program_id(program_id: str) -> None:
    """
    Validates a program ID to ensure it contains only safe characters.
    A valid program ID should consist of alphanumeric characters and hyphens.

    Args:
        program_id: The program ID to validate.

    Raises:
        InvalidProgramIdError: If the program ID is invalid.
    """
    # Allow alphanumeric characters and hyphens. Example: '26-249'
    if not re.fullmatch(r'[a-zA-Z0-9\-]+', program_id):
        raise InvalidProgramIdError(
            program_id,
            reason="contains invalid characters."
        )
