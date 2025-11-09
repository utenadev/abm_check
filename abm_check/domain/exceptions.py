"""Custom exceptions for abm_check."""


class AbmCheckError(Exception):
    """Base exception for abm_check."""
    pass


class ProgramNotFoundError(AbmCheckError):
    """Program not found."""
    
    def __init__(self, program_id: str):
        self.program_id = program_id
        super().__init__(f"Program not found: {program_id}")


class InvalidProgramIdError(AbmCheckError):
    """Invalid program ID format."""
    
    def __init__(self, program_id: str, reason: str = ""):
        self.program_id = program_id
        self.reason = reason
        msg = f"Invalid program ID: {program_id}"
        if reason:
            msg += f" ({reason})"
        super().__init__(msg)


class SeasonDetectionError(AbmCheckError):
    """Season detection failed."""
    
    def __init__(self, program_id: str, season: int, reason: str = ""):
        self.program_id = program_id
        self.season = season
        self.reason = reason
        msg = f"Failed to detect season {season} for program {program_id}"
        if reason:
            msg += f": {reason}"
        super().__init__(msg)


class UrlExtractionError(AbmCheckError):
    """URL extraction failed."""
    
    def __init__(self, url: str, reason: str = ""):
        self.url = url
        self.reason = reason
        msg = f"Failed to extract program ID from URL: {url}"
        if reason:
            msg += f" ({reason})"
        super().__init__(msg)


class DownloadRestrictionError(AbmCheckError):
    """Episode download is restricted."""
    
    def __init__(self, episode_id: str, reason: str = "Premium only"):
        self.episode_id = episode_id
        self.reason = reason
        super().__init__(f"Download restricted for episode {episode_id}: {reason}")


class FetchError(AbmCheckError):
    """Failed to fetch program information."""
    
    def __init__(self, program_id: str, reason: str = ""):
        self.program_id = program_id
        self.reason = reason
        msg = f"Failed to fetch program {program_id}"
        if reason:
            msg += f": {reason}"
        super().__init__(msg)


class StorageError(AbmCheckError):
    """Storage operation failed."""
    
    def __init__(self, operation: str, reason: str = ""):
        self.operation = operation
        self.reason = reason
        msg = f"Storage operation failed: {operation}"
        if reason:
            msg += f" ({reason})"
        super().__init__(msg)


class YtdlpError(AbmCheckError):
    """yt-dlp related error."""
    
    def __init__(self, reason: str = ""):
        self.reason = reason
        msg = "yt-dlp error"
        if reason:
            msg += f": {reason}"
        super().__init__(msg)
