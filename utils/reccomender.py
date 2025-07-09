import csv
import ast
import json
import re

# Helper functions
def match_tile(tile1, tile2, tolerance=5.0, rotation_tol=40.0):
    return (
        tile1["type"] == tile2["type"]
        and abs(tile1["x"] - tile2["x"]) <= tolerance
        and abs(tile1["y"] - tile2["y"]) <= tolerance
        and abs(tile1["rotation"] - tile2["rotation"]) <= rotation_tol
    )

def tile_match_score(user_shapes:list, meta_shapes:list) -> tuple:
    matched = 0
    used = [False] * len(meta_shapes)

    for u_tile in user_shapes:
        for i, m_tile in enumerate(meta_shapes):
            if not used[i] and match_tile(u_tile, m_tile):
                matched += 1
                used[i] = True
                break

    total = len(user_shapes)
    relevance = matched / total
    return matched, relevance

def safe_parse(data_str: str) -> dict:
    try:
        return json.loads(data_str)
    except Exception as e:
        print(f"TOP! Skipping line due to error: {e}")
        return None

def convert_to_embed_url(youtube_url):
    if not youtube_url:
        return ""
    
    if "youtube.com/embed/" in youtube_url:
        return youtube_url  # Already formatted

    video_id = None

    # Match short URLs like youtu.be/VIDEO_ID
    short_match = re.search(r'youtu\.be/([^?\s]+)', youtube_url)
    if short_match:
        video_id = short_match.group(1)

    # Match long URLs like youtube.com/watch?v=VIDEO_ID
    if not video_id:
        long_match = re.search(r'v=([^&\s]+)', youtube_url)
        if long_match:
            video_id = long_match.group(1)

    if video_id:
        return f"https://www.youtube.com/embed/{video_id}"
    else:
        return ""



# Actual build finding function
def find_top_matches(user_generation_data):
    user_data = safe_parse(user_generation_data)
    if not user_data or "shapes" not in user_data:
        print("Invalid or missing 'shapes' in user data.")
        return [], [] # Returns empty lists if data is invalid - could maybe just display a message instead?

    user_shapes = user_data["shapes"]
    matches = []

    with open("utils/meta_builds.json", "r") as f:
        builds = json.load(f)

    for row in builds:
        build_data = row.get("generation_data")
        if not build_data or "shapes" not in build_data:
            continue

        build_shapes = build_data["shapes"]
        matched, relevance = tile_match_score(user_shapes, build_shapes)
        matches.append((relevance, row))

    # Sort by relevance
    matches.sort(reverse=True, key=lambda x: x[0])

    # Select top matches and relevant ones (>60% overlap)
    top_matches = [row for score, row in matches[:5]]
    relevant_builds = [row for score, row in matches if score >= 0.6]

    return top_matches, relevant_builds