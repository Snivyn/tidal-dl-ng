from enum import StrEnum

CTX_TIDAL: str = "tidal"
REQUESTS_TIMEOUT_SEC: int = 45
EXTENSION_LYRICS: str = ".lrc"
UNIQUIFY_THRESHOLD: int = 99
FILENAME_SANITIZE_PLACEHOLDER: str = "_"


class QualityVideo(StrEnum):
    P360: str = "360"
    P480: str = "480"
    P720: str = "720"
    P1080: str = "1080"


class MediaType(StrEnum):
    TRACK: str = "track"
    VIDEO: str = "video"
    PLAYLIST: str = "playlist"
    ALBUM: str = "album"
    MIX: str = "mix"


class SkipExisting(StrEnum):
    Disabled: str = "False"
    Filename: str = "exact"
    ExtensionIgnore: str = "extension_ignore"
    Append: str = "append"


class CoverDimensions(StrEnum):
    Px80: str = "80"
    Px160: str = "160"
    Px320: str = "320"
    Px640: str = "640"
    Px1280: str = "1280"


class TidalLists(StrEnum):
    Playlists: str = "Playlists"
    Favorites: str = "Favorites"
    Mixes: str = "Mixes"


class QueueDownloadStatus(StrEnum):
    Waiting: str = "⏳️"
    Downloading: str = "▶️"
    Finished: str = "✅"
    Failed: str = "❌"
    Skipped: str = "↪️"
