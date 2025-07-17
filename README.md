# Floor Planning Application

A web-based floor planning application that allows users to design floor layouts using tessellating shapes (squares and triangles). Built with Flask and vanilla JavaScript.

## Features

- **Interactive Shape Placement**: Place squares and triangles on a grid
- **Smart Tessellation**: Shapes automatically align edge-to-edge
- **Collision Detection**: Prevents overlapping shapes
- **Multi-Floor Support**: Create and manage multiple floor plans
- **Clean UI**: Intuitive interface with visual feedback

## Project Structure

```
Software-Major-Project/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── templates/            # HTML templates
│   ├── Login.html
│   ├── Build.html
│   ├── Save.html
│   ├── Recs.html
│   └── Blackjack.html
├── static/               # Static assets
│   ├── css/             # Stylesheets
│   │   ├── style.css
│   │   ├── build.css
│   │   ├── login.css
│   │   ├── recs.css
│   │   └── saves.css
│   └── js/              # JavaScript files
│       └── build.js
├── utils/               # Utility modules
│   └── shapes.py       # Shape calculation utilities
└── tests/              # Test suite
    ├── run_tests.py    # Test runner script
    ├── unit/           # Unit tests
    └── integration/    # Integration tests
```

## Installation

1. Clone the repository:
```bash
git clone https://github.com/Cheesemucher/Software-Major-Project.git
cd Software-Major-Project
```

2. Create a virtual environment (recommended):
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Running the Application

1. Start the Flask server:
```bash
python3 app.py
```

2. Open your browser and navigate to:
```
http://localhost:5001
```

3. Click the login button to access the build page

## Usage

### Building Floor Plans

1. Click the red "+" button to start placing shapes
2. Select either "Square" or "Triangle" from the menu
3. The shape will be placed and new "+" buttons appear on available edges
4. Continue placing shapes to create your floor plan
5. Shapes automatically align and prevent overlapping

### Managing Floors

- Click the "+" button in the right panel to add new floors
- Click the pencil icon to rename floors
- Each floor maintains its own layout

## Running Tests

Run all tests:
```bash
python3 tests/run_tests.py
```

Run only unit tests:
```bash
python3 tests/run_tests.py --unit
```

Run only integration tests:
```bash
python3 tests/run_tests.py --integration
```

## Technical Details

### Shape Calculations

- **Squares**: 80x80 pixels, placed edge-to-edge
- **Triangles**: Equilateral with 80px sides
- **Collision Detection**: Prevents shapes from overlapping with configurable tolerances
- **Edge Detection**: Automatically calculates valid placement positions

### Architecture

- **Backend**: Flask with session-based shape tracking
- **Frontend**: Vanilla JavaScript with dynamic DOM manipulation
- **Styling**: CSS Grid and Flexbox for responsive layout
