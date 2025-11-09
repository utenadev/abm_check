"""Unit tests for domain exceptions."""

import pytest

from abm_check.domain.exceptions import (
    AbmCheckError,
    FetchError,
    InvalidProgramIdError,
    ProgramNotFoundError,
    SeasonDetectionError,
    StorageError,
    YtdlpError,
)


class TestExceptions:
    """Test custom exception classes."""

    def test_abm_check_error_base(self) -> None:
        """Test base exception class."""
        error = AbmCheckError("Test error")
        assert str(error) == "Test error"
        assert isinstance(error, Exception)

    def test_program_not_found_error(self) -> None:
        """Test ProgramNotFoundError exception."""
        error = ProgramNotFoundError("26-249")
        assert error.program_id == "26-249"
        assert "26-249" in str(error)
        assert "not found" in str(error).lower()

    def test_invalid_program_id_error(self) -> None:
        """Test InvalidProgramIdError exception."""
        error = InvalidProgramIdError("invalid-id", "Invalid format")
        assert error.program_id == "invalid-id"
        assert error.reason == "Invalid format"
        assert "invalid-id" in str(error)
        assert "Invalid format" in str(error)

    def test_invalid_program_id_error_without_reason(self) -> None:
        """Test InvalidProgramIdError without reason."""
        error = InvalidProgramIdError("invalid-id")
        assert error.program_id == "invalid-id"
        assert error.reason == ""
        assert "invalid-id" in str(error)

    def test_season_detection_error(self) -> None:
        """Test SeasonDetectionError exception."""
        error = SeasonDetectionError("26-249", 2, "No episodes found")
        assert error.program_id == "26-249"
        assert error.season == 2
        assert error.reason == "No episodes found"
        assert "26-249" in str(error)
        assert "2" in str(error)
        assert "No episodes found" in str(error)

    def test_season_detection_error_without_reason(self) -> None:
        """Test SeasonDetectionError without reason."""
        error = SeasonDetectionError("26-249", 3)
        assert error.program_id == "26-249"
        assert error.season == 3
        assert error.reason == ""

    def test_fetch_error(self) -> None:
        """Test FetchError exception."""
        error = FetchError("26-249", "Network timeout")
        assert error.program_id == "26-249"
        assert error.reason == "Network timeout"
        assert "26-249" in str(error)
        assert "Network timeout" in str(error)

    def test_ytdlp_error(self) -> None:
        """Test YtdlpError exception."""
        error = YtdlpError("yt-dlp extraction failed")
        assert "yt-dlp" in str(error).lower()
        assert "extraction failed" in str(error).lower()

    def test_storage_error(self) -> None:
        """Test StorageError exception."""
        error = StorageError("save_program", "Permission denied")
        assert error.operation == "save_program"
        assert error.reason == "Permission denied"
        assert "save_program" in str(error)
        assert "Permission denied" in str(error)

    @pytest.mark.parametrize("program_id,expected_in_message", [
        ("26-249", "26-249"),
        ("189-85", "189-85"),
        ("test-123", "test-123"),
    ])
    def test_program_not_found_various_ids(self, program_id: str, expected_in_message: str) -> None:
        """Test ProgramNotFoundError with various program IDs."""
        error = ProgramNotFoundError(program_id)
        assert expected_in_message in str(error)

    def test_exception_inheritance(self) -> None:
        """Test that all custom exceptions inherit from AbmCheckError."""
        assert issubclass(ProgramNotFoundError, AbmCheckError)
        assert issubclass(InvalidProgramIdError, AbmCheckError)
        assert issubclass(SeasonDetectionError, AbmCheckError)
        assert issubclass(FetchError, AbmCheckError)
        assert issubclass(YtdlpError, AbmCheckError)
        assert issubclass(StorageError, AbmCheckError)

    def test_exception_catching(self) -> None:
        """Test that custom exceptions can be caught as AbmCheckError."""
        with pytest.raises(AbmCheckError):
            raise ProgramNotFoundError("26-249")
        
        with pytest.raises(AbmCheckError):
            raise FetchError("26-249", "Test error")

    def test_storage_error_operations(self) -> None:
        """Test StorageError with different operations."""
        operations = ["save_program", "load_programs", "delete_program", "find_program"]
        
        for op in operations:
            error = StorageError(op, "Test error")
            assert error.operation == op
            assert op in str(error)
