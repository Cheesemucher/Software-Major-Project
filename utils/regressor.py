import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.multioutput import MultiOutputRegressor
from sklearn.model_selection import train_test_split
import json

# Constants
MAX_TILES = 10
TILE_VECTOR_SIZE = 4  # [type, x, y, rotation]

# Saved learning data reading
def load_build_dataset_from_csv(filepath: str) -> list:
    """
    Reads builds from a CSV file and returns a cleaned list of builds.
    Filters out any rows that don't contain valid 'shapes' lists.
    """
    build_dataset = []

    with open(filepath, 'r', encoding='utf-8') as f:
        for line_number, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue

            try:
                data = json.loads(line)
                if 'shapes' in data and isinstance(data['shapes'], list):
                    valid_shapes = [
                        s for s in data['shapes']
                        if isinstance(s, dict)
                        and 'type' in s and s['type'] in ('square', 'triangle')
                        and all(k in s for k in ('x', 'y', 'rotation'))
                    ]
                    if valid_shapes:
                        build_dataset.append({'shapes': valid_shapes})
            except json.JSONDecodeError:
                print(f"Skipping line {line_number}: Invalid JSON.")

    return build_dataset

# Tile conversion helpers 
def tile_to_vector(tile: dict) -> list:
    """Convert a tile dictionary to a numeric vector."""
    type_val = 0 if tile['type'] == 'square' else 1  # 0 = square, 1 = triangle
    return [type_val, tile['x'], tile['y'], tile['rotation']]

def vector_to_tile(vec: list) -> dict:
    """Convert a numeric vector back to a tile dictionary."""
    return {
        "type": "square" if round(vec[0]) == 0 else "triangle",
        "x": vec[1],
        "y": vec[2],
        "rotation": vec[3]
    }

# --- Training function ---

def train_model(build_dataset: list):
    """
    Trains a model to predict the next tile given a partial build.
    build_dataset: list of build dicts, each with a "shapes" key
    Returns: trained model
    """

    max_tiles = MAX_TILES
    X, y = [], []

    for build in build_dataset:
        tiles = build["shapes"]
        for i in range(1, len(tiles)):
            partial = tiles[:i]
            target = tiles[i]

            # Convert partial build to flat padded vector
            vec = [tile_to_vector(t) for t in partial[:max_tiles]]
            pad = [[0, 0, 0, 0]] * (max_tiles - len(vec))
            flat_vector = [v for t in (vec + pad) for v in t]

            X.append(flat_vector)
            y.append(tile_to_vector(target))

    X = np.array(X)
    y = np.array(y)

    # Optional: split to evaluate performance
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    model = MultiOutputRegressor(RandomForestRegressor(n_estimators=100, random_state=42))
    model.fit(X_train, y_train)

    return model

# --- Prediction function ---

def predict_next_tile(model, current_build: list, max_tiles=MAX_TILES):
    """
    Predicts the next tile given the current build.
    current_build: list of tile dicts (shapes)
    Returns: predicted tile dict
    """
    vec = [tile_to_vector(t) for t in current_build[-max_tiles:]]
    pad = [[0, 0, 0, 0]] * (max_tiles - len(vec))
    flat_vector = [v for t in (vec + pad) for v in t]

    prediction = model.predict([flat_vector])[0]
    return vector_to_tile(prediction)
