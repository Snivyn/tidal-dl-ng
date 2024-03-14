import glob
import math
import os
import re
from pathlib import Path

from pathvalidate import sanitize_filename, sanitize_filepath
from pathvalidate.error import ValidationError
from tidalapi import Album, Mix, Playlist, Track, UserPlaylist, Video

from tidal_dl_ng import __name_display__
from tidal_dl_ng.constants import AudioExtensions, MediaType
from tidal_dl_ng.helper.tidal import name_builder_artist, name_builder_title


def path_home() -> str:
    if "XDG_CONFIG_HOME" in os.environ:
        return os.environ["XDG_CONFIG_HOME"]
    elif "HOME" in os.environ:
        return os.environ["HOME"]
    elif "HOMEDRIVE" in os.environ and "HOMEPATH" in os.environ:
        return os.path.join(os.environ["HOMEDRIVE"], os.environ["HOMEPATH"])
    else:
        return os.path.abspath("./")


def path_config_base() -> str:
    path_config: str = ".config"
    path_base: str = os.path.join(path_home(), path_config, __name_display__)

    return path_base


def path_file_log() -> str:
    # TODO: Remove this soon. Only for migration to new dir.
    old = os.path.join(path_home(), ".tidal-dl-ng.log")
    if os.path.isfile(old):
        os.makedirs(path_config_base(), exist_ok=True)
        os.rename(old, os.path.join(path_config_base(), "app.log"))

    return os.path.join(path_config_base(), "app.log")


def path_file_token() -> str:
    # TODO: Remove this soon. Only for migration to new dir.
    old = os.path.join(path_home(), ".tidal-dl-ng_token.json")
    if os.path.isfile(old):
        os.makedirs(path_config_base(), exist_ok=True)
        os.rename(old, os.path.join(path_config_base(), "token.json"))

    return os.path.join(path_config_base(), "token.json")


def path_file_settings() -> str:
    # TODO: Remove this soon. Only for migration to new dir.
    old = os.path.join(path_home(), ".tidal-dl-ng_settings.json")
    if os.path.isfile(old):
        os.makedirs(path_config_base(), exist_ok=True)
        os.rename(old, os.path.join(path_config_base(), "settings.json"))

    return os.path.join(path_config_base(), "settings.json")


def format_path_media(fmt_template: str, media: Track | Album | Playlist | UserPlaylist | Video | Mix) -> str:
    result = fmt_template

    # Search track format template for placeholder.
    regex = r"\{(.+?)\}"
    matches = re.finditer(regex, fmt_template, re.MULTILINE)

    for _matchNum, match in enumerate(matches, start=1):
        template_str = match.group()
        result_fmt = format_str_media(match.group(1), media)

        if result_fmt != match.group(1):
            value = sanitize_filename(result_fmt)
            result = result.replace(template_str, value)

    return result


def format_str_media(name: str, media: Track | Album | Playlist | UserPlaylist | Video | Mix) -> str:
    result: str = name

    try:
        if name == "artist_name":
            if hasattr(media, "artists"):
                result = name_builder_artist(media)
            elif hasattr(media, "artist"):
                result = media.artist.name
        elif name == "track_title":
            if isinstance(media, Track | Video):
                result = name_builder_title(media)
        elif name == "mix_name":
            if isinstance(media, Mix):
                result = media.title
        elif name == "playlist_name":
            if isinstance(media, Playlist | UserPlaylist):
                result = media.name
        elif name == "album_title":
            if isinstance(media, Album):
                result = media.name
            elif isinstance(media, Track):
                result = media.album.name
        elif name == "album_track_num":
            if isinstance(media, Track | Video):
                num_tracks: int = media.album.num_tracks if hasattr(media, "album") else 1
                count_digits: int = int(math.log10(num_tracks)) + 1
                result = str(media.track_num).zfill(count_digits)
        elif name == "album_num_tracks":
            if isinstance(media, Track | Video):
                result = str(media.album.num_tracks if hasattr(media, "album") else 1)
        elif name == "track_id":
            if isinstance(media, Track | Video):
                result = media.id
        elif name == "playlist_id":
            if isinstance(media, Playlist):
                result = media.id
        elif name == "track_duration_seconds":
            if isinstance(media, Track | Video):
                result = str(media.duration)
        elif name == "track_duration_minutes":
            if isinstance(media, Track | Video):
                m, s = divmod(media.duration, 60)
                result = f"{m:01d}:{s:02d}"
        elif name == "album_duration_seconds":
            if isinstance(media, Album):
                result = str(media.duration)
        elif name == "album_duration_minutes":
            if isinstance(media, Album):
                m, s = divmod(media.duration, 60)
                result = f"{m:01d}:{s:02d}"
        elif name == "playlist_duration_seconds":
            if isinstance(media, Album):
                result = str(media.duration)
        elif name == "playlist_duration_minutes":
            if isinstance(media, Album):
                m, s = divmod(media.duration, 60)
                result = f"{m:01d}:{s:02d}"
        elif name == "album_year":
            if isinstance(media, Album):
                result = str(media.release_date.year)
        elif name == "video_quality":
            if isinstance(media, Video):
                result = media.video_quality
        elif name == "track_quality":
            if isinstance(media, Track):
                result = ", ".join(tag for tag in media.media_metadata_tags)
    except Exception as e:
        # TODO: Implement better exception logging.
        print(e)

        pass

    return result


def get_format_template(
    media: Track | Album | Playlist | UserPlaylist | Video | Mix | MediaType, settings
) -> str | bool:
    result = False

    if isinstance(media, Track) or media == MediaType.TRACK:
        result = settings.data.format_track
    elif isinstance(media, Album) or media == MediaType.ALBUM:
        result = settings.data.format_album
    elif isinstance(media, Playlist | UserPlaylist) or media == MediaType.PLAYLIST:
        result = settings.data.format_playlist
    elif isinstance(media, Mix) or media == MediaType.MIX:
        result = settings.data.format_mix
    elif isinstance(media, Video) or media == MediaType.VIDEO:
        result = settings.data.format_video

    return result


def path_file_sanitize(path_file: str, adapt: bool = False) -> (bool, str):
    # Split into path and filename
    pathname, filename = os.path.split(path_file)

    # Sanitize path
    try:
        pathname_sanitized = sanitize_filepath(
            pathname, replacement_text=" ", validate_after_sanitize=True, platform="auto"
        )
    except ValidationError:
        # If adaption of path is allowed in case of an error set path to HOME.
        if adapt:
            pathname_sanitized = Path.home()
        else:
            raise

    # Sanitize filename
    try:
        filename_sanitized = sanitize_filename(
            filename, replacement_text=" ", validate_after_sanitize=True, platform="auto"
        )
        filename_sanitized_extension = Path(filename_sanitized).suffix

        # Check if the file extension was removed by shortening the filename length
        if filename_sanitized_extension == "":
            # Add the original file extension
            file_extension = "_" + Path(path_file).suffix
            filename_sanitized = filename_sanitized[: -len(file_extension)] + file_extension
    except ValidationError as e:
        # TODO: Implement proper exception handling and logging.
        print(e)

        raise

    # Join path and filename
    result = os.path.join(pathname_sanitized, filename_sanitized)

    return result


def check_file_exists(path_file: str, extension_ignore: bool = False):
    if extension_ignore:
        path_file_stem: str = Path(path_file).stem
        path_files: [str] = []

        for extension in AudioExtensions:
            path_files.append(path_file_stem + extension.value)
    else:
        path_files: [str] = [path_file]

    result = bool(sum([glob.glob(_file) for _file in path_files], []))

    return result
