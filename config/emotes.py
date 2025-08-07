"""
Emote configuration and lookup for the Twitch AI Bot.
Includes standard Twitch emotes, BTTV, FFZ, and 7TV emotes.
"""

import requests
from json import load, dump
from typing import Dict, List, Set, Optional, Any
from pathlib import Path
import time

# Cache emote data for performance
_emote_cache = {
    "data": {},
    "categories": {},
    "last_updated": 0,
    "cache_duration": 86400  # 24 hours in seconds
}


def get_emotes(force_reload: bool = False) -> Dict[str, Any]:
    """
    Get all available emotes

    Args:
        force_reload: Force reload of emotes from sources

    Returns:
        Dictionary of emotes organized by source and code
    """
    global _emote_cache

    # Check if we need to reload
    current_time = time.time()
    cache_expired = (current_time - _emote_cache["last_updated"]) > _emote_cache["cache_duration"]

    if not _emote_cache["data"] or force_reload or cache_expired:
        _load_emotes()

    return _emote_cache["data"]


def get_emote_categories() -> Dict[str, Set[str]]:
    """
    Get categorized sets of emote codes

    Returns:
        Dictionary of emote categories with sets of emote codes
    """
    global _emote_cache

    # Ensure emotes are loaded
    if not _emote_cache["data"]:
        _load_emotes()

    return _emote_cache["categories"]


def _load_emotes() -> None:
    """
    Load emotes from various sources and cache them
    """
    global _emote_cache

    emotes = {}
    categories = {
        "all": set(),
        "twitch": set(),
        "bttv": set(),
        "ffz": set(),
        "7tv": set(),
        "animated": set(),
        "static": set(),
        "common": set(),  # Common/popular emotes
        "rare": set(),  # Less frequently used emotes
        "faces": set(),  # Emotes representing faces/expressions
        "memes": set(),  # Meme-based emotes
        "custom": set()  # Custom channel-specific emotes
    }

    # First try to load from cache file
    cache_file = Path("cache/emotes.json")
    if cache_file.exists():
        try:
            with open(cache_file, 'r', encoding='utf-8') as f:
                cached_data = load(f)
                emotes = cached_data.get("emotes", {})

                # Convert category lists back to sets
                for category, emote_list in cached_data.get("categories", {}).items():
                    categories[category] = set(emote_list)

                _emote_cache["data"] = emotes
                _emote_cache["categories"] = categories
                _emote_cache["last_updated"] = cached_data.get("last_updated", time.time())

                # If cache is still valid, return early
                if (time.time() - _emote_cache["last_updated"]) <= _emote_cache["cache_duration"]:
                    return
        except Exception as e:
            print(f"Error loading emote cache: {e}")

    # Load default/built-in emotes
    _load_default_emotes(emotes, categories)

    # Try to fetch from APIs (with fallbacks to built-in lists)
    _fetch_twitch_emotes(emotes, categories)
    _fetch_bttv_emotes(emotes, categories)
    _fetch_ffz_emotes(emotes, categories)
    _fetch_7tv_emotes(emotes, categories)

    # Update the cache
    _emote_cache["data"] = emotes
    _emote_cache["categories"] = categories
    _emote_cache["last_updated"] = time.time()

    # Save to cache file
    try:
        cache_file.parent.mkdir(parents=True, exist_ok=True)

        # Convert sets to lists for JSON serialization
        serializable_categories = {
            category: list(emote_set)
            for category, emote_set in categories.items()
        }

        with open(cache_file, 'w', encoding='utf-8') as f:
            dump({
                "emotes": emotes,
                "categories": serializable_categories,
                "last_updated": _emote_cache["last_updated"]
            }, f, indent=2)
    except Exception as e:
        print(f"Error saving emote cache: {e}")


def _load_default_emotes(emotes: Dict[str, Any], categories: Dict[str, Set[str]]) -> None:
    """
    Load default built-in emotes

    Args:
        emotes: Emote dictionary to update
        categories: Emote categories to update
    """
    # Common Twitch global emotes
    default_twitch_emotes = {
        "Kappa": {"id": "25", "animated": False, "source": "twitch", "category": ["faces", "common"]},
        "PogChamp": {"id": "88", "animated": False, "source": "twitch", "category": ["faces", "common"]},
        "LUL": {"id": "425618", "animated": False, "source": "twitch", "category": ["faces", "common"]},
        "BibleThump": {"id": "86", "animated": False, "source": "twitch", "category": ["faces", "common"]},
        "HeyGuys": {"id": "30259", "animated": False, "source": "twitch", "category": ["faces", "common"]},
        "ResidentSleeper": {"id": "245", "animated": False, "source": "twitch", "category": ["faces", "common"]},
        "Kreygasm": {"id": "41", "animated": False, "source": "twitch", "category": ["faces", "common"]},
        "4Head": {"id": "354", "animated": False, "source": "twitch", "category": ["faces", "common"]},
        "SwiftRage": {"id": "34", "animated": False, "source": "twitch", "category": ["faces", "common"]},
        "TriHard": {"id": "120232", "animated": False, "source": "twitch", "category": ["faces", "common"]},
        "DansGame": {"id": "33", "animated": False, "source": "twitch", "category": ["faces", "common"]},
        "Jebaited": {"id": "114836", "animated": False, "source": "twitch", "category": ["faces", "memes"]},
        "CoolStoryBob": {"id": "123171", "animated": False, "source": "twitch", "category": ["faces", "common"]},
        "SMOrc": {"id": "52", "animated": False, "source": "twitch", "category": ["faces", "common"]},
        "FrankerZ": {"id": "65", "animated": False, "source": "twitch", "category": ["common"]},
        "BabyRage": {"id": "22639", "animated": False, "source": "twitch", "category": ["faces", "common"]},
        "VoHiYo": {"id": "81274", "animated": False, "source": "twitch", "category": ["faces", "common"]},
        "TTours": {"id": "38436", "animated": False, "source": "twitch", "category": ["common"]},
        "WutFace": {"id": "28087", "animated": False, "source": "twitch", "category": ["faces", "common"]},
        "DatSheffy": {"id": "170", "animated": False, "source": "twitch", "category": ["faces", "common"]},
        "CoolCat": {"id": "58127", "animated": False, "source": "twitch", "category": ["common"]},
        "NotLikeThis": {"id": "58765", "animated": False, "source": "twitch", "category": ["faces", "common"]},
        "FailFish": {"id": "360", "animated": False, "source": "twitch", "category": ["faces", "common"]},
        "KappaPride": {"id": "55338", "animated": False, "source": "twitch", "category": ["faces", "common"]},
        "PJSalt": {"id": "36", "animated": False, "source": "twitch", "category": ["common"]},
    }

    # Common BTTV emotes
    default_bttv_emotes = {
        "OMEGALUL": {"id": "583089f4d46190f14cf7b00d", "animated": False, "source": "bttv",
                     "category": ["faces", "common"]},
        "pepeHands": {"id": "59f27b3f4ebd8047f54dee29", "animated": False, "source": "bttv",
                      "category": ["faces", "common", "memes"]},
        "monkaS": {"id": "56e9f494fff3cc5c35e5287e", "animated": False, "source": "bttv",
                   "category": ["faces", "common", "memes"]},
        "PepeLaugh": {"id": "5c548025009a2e73916b3a37", "animated": False, "source": "bttv",
                      "category": ["faces", "common", "memes"]},
        "Pepega": {"id": "5aca62163e290877a25481ad", "animated": False, "source": "bttv",
                   "category": ["faces", "common", "memes"]},
        "gachiBASS": {"id": "57719a9a6bdecd592c3ad59b", "animated": False, "source": "bttv",
                      "category": ["faces", "common"]},
        "forsenCD": {"id": "5d3e250a6d68672adc1bae83", "animated": False, "source": "bttv",
                     "category": ["faces", "memes"]},
        "PogU": {"id": "5c1a8f28d48f3302e186363f", "animated": False, "source": "bttv",
                 "category": ["faces", "common"]},
        "KEKW": {"id": "5e9c6c187e090362f8b0b9e8", "animated": False, "source": "bttv",
                 "category": ["faces", "common"]},
        "WeirdChamp": {"id": "5d20a55de1cfde376e532972", "animated": False, "source": "bttv",
                       "category": ["faces", "common"]},
        "catJAM": {"id": "5f1b0186cf6d2144653d2970", "animated": True, "source": "bttv",
                   "category": ["animated", "common"]},
        "PepeHands": {"id": "59f27b3f4ebd8047f54dee29", "animated": False, "source": "bttv",
                      "category": ["faces", "common", "memes"]},
        "sadge": {"id": "5f63a86572a9d16c8fde6f04", "animated": False, "source": "bttv",
                  "category": ["faces", "common", "memes"]},
        "monkaW": {"id": "59ca6551b27c823d5b1fd872", "animated": False, "source": "bttv",
                   "category": ["faces", "common", "memes"]},
        "LULW": {"id": "5dc79d1b27360247dd6516ec", "animated": False, "source": "bttv",
                 "category": ["faces", "common"]},
    }

    # Add default emotes to the main collection
    if "twitch" not in emotes:
        emotes["twitch"] = {}
    emotes["twitch"].update(default_twitch_emotes)

    if "bttv" not in emotes:
        emotes["bttv"] = {}
    emotes["bttv"].update(default_bttv_emotes)

    # Update categories
    for source, source_emotes in [("twitch", default_twitch_emotes), ("bttv", default_bttv_emotes)]:
        for code, data in source_emotes.items():
            # Add to 'all' category
            categories["all"].add(code)

            # Add to source category
            categories[source].add(code)

            # Add to animated/static categories
            if data.get("animated", False):
                categories["animated"].add(code)
            else:
                categories["static"].add(code)

            # Add to other specified categories
            for category in data.get("category", []):
                if category in categories:
                    categories[category].add(code)


def _fetch_twitch_emotes(emotes: Dict[str, Any], categories: Dict[str, Set[str]]) -> None:
    """
    Fetch Twitch global emotes

    Args:
        emotes: Emote dictionary to update
        categories: Emote categories to update
    """
    # Initialize the Twitch emotes dictionary if not exists
    if "twitch" not in emotes:
        emotes["twitch"] = {}

    try:
        # Use Twitch API (requires authentication)
        # This is a simplified example; actual implementation would use proper auth
        # headers = {"Client-ID": client_id, "Authorization": f"Bearer {access_token}"}
        # response = requests.get("https://api.twitch.tv/helix/chat/emotes/global", headers=headers)

        # As a fallback, load from a static file if API call fails
        fallback_file = Path("config/static/twitch_emotes.json")
        if fallback_file.exists():
            with open(fallback_file, 'r', encoding='utf-8') as f:
                twitch_emotes_data = load(f)

                for emote_data in twitch_emotes_data.get("data", []):
                    code = emote_data.get("name")
                    if code:
                        emotes["twitch"][code] = {
                            "id": emote_data.get("id"),
                            "animated": emote_data.get("format", []).count("animated") > 0,
                            "source": "twitch",
                            "category": _categorize_emote(code, emote_data)
                        }

                        # Update categories
                        categories["all"].add(code)
                        categories["twitch"].add(code)

                        if emotes["twitch"][code]["animated"]:
                            categories["animated"].add(code)
                        else:
                            categories["static"].add(code)

                        for category in emotes["twitch"][code]["category"]:
                            if category in categories:
                                categories[category].add(code)
    except Exception as e:
        print(f"Error fetching Twitch emotes: {e}")


def _fetch_bttv_emotes(emotes: Dict[str, Any], categories: Dict[str, Set[str]]) -> None:
    """
    Fetch BTTV global emotes

    Args:
        emotes: Emote dictionary to update
        categories: Emote categories to update
    """
    # Initialize the BTTV emotes dictionary if not exists
    if "bttv" not in emotes:
        emotes["bttv"] = {}

    try:
        # Try to fetch from BTTV API
        response = requests.get("https://api.betterttv.net/3/cached/emotes/global", timeout=5)

        if response.status_code == 200:
            bttv_emotes_data = response.json()

            for emote_data in bttv_emotes_data:
                code = emote_data.get("code")
                if code:
                    emotes["bttv"][code] = {
                        "id": emote_data.get("id"),
                        "animated": emote_data.get("imageType") == "gif",
                        "source": "bttv",
                        "category": _categorize_emote(code, emote_data)
                    }

                    # Update categories
                    categories["all"].add(code)
                    categories["bttv"].add(code)

                    if emotes["bttv"][code]["animated"]:
                        categories["animated"].add(code)
                    else:
                        categories["static"].add(code)

                    for category in emotes["bttv"][code]["category"]:
                        if category in categories:
                            categories[category].add(code)
        else:
            # Fallback to static file
            fallback_file = Path("config/static/bttv_emotes.json")
            if fallback_file.exists():
                with open(fallback_file, 'r', encoding='utf-8') as f:
                    bttv_emotes_data = load(f)

                    for emote_data in bttv_emotes_data:
                        code = emote_data.get("code")
                        if code:
                            emotes["bttv"][code] = {
                                "id": emote_data.get("id"),
                                "animated": emote_data.get("imageType") == "gif",
                                "source": "bttv",
                                "category": _categorize_emote(code, emote_data)
                            }

                            # Update categories
                            categories["all"].add(code)
                            categories["bttv"].add(code)

                            if emotes["bttv"][code]["animated"]:
                                categories["animated"].add(code)
                            else:
                                categories["static"].add(code)

                            for category in emotes["bttv"][code]["category"]:
                                if category in categories:
                                    categories[category].add(code)
    except Exception as e:
        print(f"Error fetching BTTV emotes: {e}")


def _fetch_ffz_emotes(emotes: Dict[str, Any], categories: Dict[str, Set[str]]) -> None:
    """
    Fetch FrankerFaceZ global emotes

    Args:
        emotes: Emote dictionary to update
        categories: Emote categories to update
    """
    # Initialize the FFZ emotes dictionary if not exists
    if "ffz" not in emotes:
        emotes["ffz"] = {}

    try:
        # Try to fetch from FFZ API
        response = requests.get("https://api.frankerfacez.com/v1/set/global", timeout=5)

        if response.status_code == 200:
            ffz_data = response.json()

            # FFZ has a unique structure with sets
            for set_id in ffz_data.get("default_sets", []):
                set_data = ffz_data.get("sets", {}).get(str(set_id), {})

                for emote_data in set_data.get("emoticons", []):
                    code = emote_data.get("name")
                    if code:
                        emotes["ffz"][code] = {
                            "id": emote_data.get("id"),
                            "animated": False,  # FFZ emotes are typically not animated
                            "source": "ffz",
                            "category": _categorize_emote(code, emote_data)
                        }

                        # Update categories
                        categories["all"].add(code)
                        categories["ffz"].add(code)
                        categories["static"].add(code)

                        for category in emotes["ffz"][code]["category"]:
                            if category in categories:
                                categories[category].add(code)
        else:
            # Fallback to static file
            fallback_file = Path("config/static/ffz_emotes.json")
            if fallback_file.exists():
                with open(fallback_file, 'r', encoding='utf-8') as f:
                    ffz_data = load(f)

                    # Process FFZ data
                    for set_id in ffz_data.get("default_sets", []):
                        set_data = ffz_data.get("sets", {}).get(str(set_id), {})

                        for emote_data in set_data.get("emoticons", []):
                            code = emote_data.get("name")
                            if code:
                                emotes["ffz"][code] = {
                                    "id": emote_data.get("id"),
                                    "animated": False,
                                    "source": "ffz",
                                    "category": _categorize_emote(code, emote_data)
                                }

                                # Update categories
                                categories["all"].add(code)
                                categories["ffz"].add(code)
                                categories["static"].add(code)

                                for category in emotes["ffz"][code]["category"]:
                                    if category in categories:
                                        categories[category].add(code)
    except Exception as e:
        print(f"Error fetching FFZ emotes: {e}")


def _fetch_7tv_emotes(emotes: Dict[str, Any], categories: Dict[str, Set[str]]) -> None:
    """
    Fetch 7TV global emotes

    Args:
        emotes: Emote dictionary to update
        categories: Emote categories to update
    """
    # Initialize the 7TV emotes dictionary if not exists
    if "7tv" not in emotes:
        emotes["7tv"] = {}

    try:
        # Try to fetch from 7TV API
        response = requests.get("https://api.7tv.app/v2/emotes/global", timeout=5)

        if response.status_code == 200:
            seventv_emotes_data = response.json()

            for emote_data in seventv_emotes_data:
                code = emote_data.get("name")
                if code:
                    emotes["7tv"][code] = {
                        "id": emote_data.get("id"),
                        "animated": emote_data.get("animated", False),
                        "source": "7tv",
                        "category": _categorize_emote(code, emote_data)
                    }

                    # Update categories
                    categories["all"].add(code)
                    categories["7tv"].add(code)

                    if emotes["7tv"][code]["animated"]:
                        categories["animated"].add(code)
                    else:
                        categories["static"].add(code)

                    for category in emotes["7tv"][code]["category"]:
                        if category in categories:
                            categories[category].add(code)
        else:
            # Fallback to static file
            fallback_file = Path("config/static/7tv_emotes.json")
            if fallback_file.exists():
                with open(fallback_file, 'r', encoding='utf-8') as f:
                    seventv_emotes_data = load(f)

                    for emote_data in seventv_emotes_data:
                        code = emote_data.get("name")
                        if code:
                            emotes["7tv"][code] = {
                                "id": emote_data.get("id"),
                                "animated": emote_data.get("animated", False),
                                "source": "7tv",
                                "category": _categorize_emote(code, emote_data)
                            }

                            # Update categories
                            categories["all"].add(code)
                            categories["7tv"].add(code)

                            if emotes["7tv"][code]["animated"]:
                                categories["animated"].add(code)
                            else:
                                categories["static"].add(code)

                            for category in emotes["7tv"][code]["category"]:
                                if category in categories:
                                    categories[category].add(code)
    except Exception as e:
        print(f"Error fetching 7TV emotes: {e}")


def _categorize_emote(code: str, emote_data: Dict[str, Any]) -> List[str]:
    """
    Categorize an emote based on its code and data

    Args:
        code: Emote code
        emote_data: Emote metadata

    Returns:
        List of category names the emote belongs to
    """
    categories = []

    # Check if emote is already categorized by its source
    if "category" in emote_data:
        # Some APIs might provide category data
        return emote_data["category"]

    # Simple heuristic categorization based on name patterns
    code_lower = code.lower()

    # Common/popular emotes - based on usage statistics or recognition
    common_emotes = ["kappa", "pogchamp", "lul", "pog", "omegalul", "pepe", "monka", "kekw"]
    if any(common in code_lower for common in common_emotes):
        categories.append("common")
    else:
        categories.append("rare")  # Assume rare if not matching common patterns

    # Face/expression emotes
    face_patterns = ["pog", "kappa", "lul", "pepe", "monka", "kek", "peepo", "smile", "sad",
                    "cry", "laugh", "angry", "rage", "weird", "cool", "think", "hmm", "smug"]
    if any(pattern in code_lower for pattern in face_patterns):
        categories.append("faces")

    # Meme-based emotes
    meme_patterns = ["pepe", "monka", "kek", "peepo", "widepeepo", "5head", "pepega", "forsen"]
    if any(pattern in code_lower for pattern in meme_patterns):
        categories.append("memes")

    # Default to 'other' if no categories assigned
    if not categories:
        categories.append("other")

    return categories


def get_emote_info(emote_code: str) -> Optional[Dict[str, Any]]:
    """
    Get information about a specific emote by its code

    Args:
        emote_code: The code/name of the emote

    Returns:
        Dictionary with emote information or None if not found
    """
    emotes = get_emotes()

    # Search through all sources
    for source, source_emotes in emotes.items():
        if emote_code in source_emotes:
            result = source_emotes[emote_code].copy()
            result["code"] = emote_code
            return result

    return None


def get_emotes_by_category(category: str) -> Set[str]:
    """
    Get all emote codes in a specific category

    Args:
        category: Category name

    Returns:
        Set of emote codes
    """
    categories = get_emote_categories()
    return categories.get(category, set())


def get_emote_url(emote_code: str, size: str = "medium") -> Optional[str]:
    """
    Get URL for an emote image

    Args:
        emote_code: The code/name of the emote
        size: Size of the emote image ('small', 'medium', 'large')

    Returns:
        URL to the emote image or None if not found
    """
    emote_info = get_emote_info(emote_code)
    if not emote_info:
        return None

    source = emote_info.get("source")
    emote_id = emote_info.get("id")
    animated = emote_info.get("animated", False)

    # Size mappings for different sources
    size_map = {
        "small": {"twitch": "1.0", "bttv": "1x", "ffz": "1", "7tv": "1x"},
        "medium": {"twitch": "2.0", "bttv": "2x", "ffz": "2", "7tv": "2x"},
        "large": {"twitch": "3.0", "bttv": "3x", "ffz": "4", "7tv": "3x"}
    }

    size_key = size_map.get(size, size_map["medium"])

    # Generate URL based on source
    if source == "twitch":
        return f"https://static-cdn.jtvnw.net/emoticons/v2/{emote_id}/default/dark/{size_key}"
    elif source == "bttv":
        ext = "gif" if animated else "png"
        return f"https://cdn.betterttv.net/emote/{emote_id}/{size_key}.{ext}"
    elif source == "ffz":
        return f"https://cdn.frankerfacez.com/emoticon/{emote_id}/{size_key}"
    elif source == "7tv":
        return f"https://cdn.7tv.app/emote/{emote_id}/{size_key}"

    return None


def find_emotes_in_text(text: str) -> List[str]:
    """
    Find all emote codes present in a text message

    Args:
        text: Text message to scan for emotes

    Returns:
        List of emote codes found in the text
    """
    all_emotes = get_emote_categories().get("all", set())
    found_emotes = []

    # Split by spaces to identify possible emote codes
    words = text.split()

    for word in words:
        # Remove any trailing punctuation
        clean_word = word.rstrip(',.!?:;\'\"')

        if clean_word in all_emotes:
            found_emotes.append(clean_word)

    return found_emotes


def refresh_emotes() -> None:
    """
    Force refresh all emote data from sources
    """
    get_emotes(force_reload=True)