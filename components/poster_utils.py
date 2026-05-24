"""Resolve movie poster/backdrop URLs with a local fallback image."""

import os

_BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NO_POSTER_PATH = os.path.join(_BASE_DIR, "assets", "noPoster.png")
TMDB_BASE = "https://image.tmdb.org/t/p"


def _clean_path(path) -> str:
    if path is None:
        return ""
    s = str(path).strip()
    if not s or s.lower() in ("none", "null", "nan", "n/a"):
        return ""
    return s


def has_poster(path) -> bool:
    return bool(_clean_path(path))


def get_poster_path_from_movie(movie) -> str:
    if isinstance(movie, dict):
        return _clean_path(movie.get("poster_path") or movie.get("poster"))
    return _clean_path(movie)


def tmdb_image_url(path: str, size: str = "w500") -> str:
    """Build TMDB image URL from a path segment, or return no-poster asset."""
    p = _clean_path(path)
    if not p:
        return NO_POSTER_PATH
    if p.startswith("http://") or p.startswith("https://"):
        return p
    if p.startswith("/"):
        return f"{TMDB_BASE}/{size}{p}"
    return f"{TMDB_BASE}/{size}/{p.lstrip('/')}"


def poster_display_url(path_or_movie, size: str = "w500") -> str:
    if isinstance(path_or_movie, dict):
        path = get_poster_path_from_movie(path_or_movie)
    else:
        path = _clean_path(path_or_movie)
    return tmdb_image_url(path, size)


def hero_display_url(backdrop=None, poster=None) -> str:
    """Detail page hero: backdrop, else poster, else no-poster."""
    b = _clean_path(backdrop)
    if b:
        return tmdb_image_url(b, "w1280")
    p = _clean_path(poster)
    if p:
        return tmdb_image_url(p, "w780")
    return NO_POSTER_PATH
