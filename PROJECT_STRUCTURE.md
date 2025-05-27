# Project Structure

## Root Directory Files

### Core Application Files
- `app.py` - Main Flask application with routes and shape placement logic
- `requirements.txt` - Python package dependencies

### Documentation
- `README.md` - Comprehensive project documentation
- `PROJECT_STRUCTURE.md` - This file, describing the project organization
- `.gitignore` - Git ignore patterns for Python/Flask projects

## Directory Structure

### `/templates/`
HTML templates for the web application:
- `Login.html` - Login page
- `Build.html` - Main floor planning interface
- `Save.html` - Save functionality page
- `Recs.html` - Recommendations page
- `Blackjack.html` - Blackjack mini-game page

### `/static/`
Static assets served by Flask:

#### `/static/css/`
- `style.css` - Global styles and theme variables
- `build.css` - Styles for the build/floor planning page
- `login.css` - Login page specific styles
- `saves.css` - Save page styles
- `recs.css` - Recommendations page styles
- `blackjack.css` - Blackjack game styles

#### `/static/js/`
- `build.js` - JavaScript for shape placement, floor management, and interactive features

### `/utils/`
Utility modules:
- `shapes.py` - Shape calculation functions (centre positions, edge detection, collision detection)
- `__init__.py` - Package initializer

### `/tests/`
Test suite organized by type:
- `run_tests.py` - Test runner script with options for unit/integration tests

#### `/tests/unit/`
- `test_shapes.py` - Unit tests for shape calculations and collision detection
- `__init__.py` - Package initializer

#### `/tests/integration/`
- `test_app.py` - Integration tests for Flask routes and shape placement API
- `__init__.py` - Package initializer

## Key Features of Organization

1. **Separation of Concerns**: Backend (Python), frontend (JS), and styling (CSS) are clearly separated
2. **Modular Design**: Shape calculations extracted to utilities for reusability
3. **Test Organization**: Tests separated by type (unit vs integration)
4. **Clean Root**: Only essential files in root directory
5. **Standard Flask Structure**: Follows Flask conventions for templates and static files