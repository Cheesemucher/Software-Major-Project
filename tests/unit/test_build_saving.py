import pytest
import json
from app import app as flask_app, db, User
from utils.builds import create_new_build, get_selected_build_data

# App + DB fixture
@pytest.fixture(scope="function")
def app_context():
    flask_app.config.update({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "SQLALCHEMY_TRACK_MODIFICATIONS": False,
    })
    with flask_app.app_context():
        db.create_all()
        yield
        db.drop_all()


@pytest.fixture
def test_users(app_context):
    user1 = User(email="user1@example.com",
                password_hash="123",
                visual_settings=json.dumps({ # Default tile settings
                    "squareColour": "#e26a4a",
                    "triangleColour": "#e26a4a",
                    "deleteButtonColour": "#ff8400",
                    "plusSize": "30",
                    "deleteSize": "22"
                 }),
                blackjack_balance=1000
                )
    user2 = User(email="user2@example.com",
                password_hash="123",
                visual_settings=json.dumps({ # Default tile settings
                    "squareColour": "#e26a4a",
                    "triangleColour": "#e26a4a",
                    "deleteButtonColour": "#ff8400",
                    "plusSize": "30",
                    "deleteSize": "22"
                 }),
                blackjack_balance=1000
                )
    db.session.add_all([user1, user2])
    db.session.commit()
    return user1, user2


def test_create_build_stores_unique_id(test_users):
    user1, _ = test_users
    data = {"tiles": ["test"]}
    build = create_new_build(user1.id, "TestBuild", data)

    assert build.id is not None
    assert build.build_name == "TestBuild"
    assert build.linked_user_id == user1.id
    assert json.loads(build.get_generation_data()) == data


def test_access_control_on_builds(test_users):
    user1, user2 = test_users
    build = create_new_build(user1.id, "PrivateBuild", {"a": 1})

    with pytest.raises(ValueError, match="Build not found"):
        get_selected_build_data(user2.id, build.id)


def test_load_and_verify_build_data(test_users):
    user1, _ = test_users
    prefs = {"grid": "on"}
    build_data = {"shapes": ["triangle"], "rotation": 30}

    user1.visual_settings = json.dumps(prefs)
    db.session.commit()

    build = create_new_build(user1.id, "LoadableBuild", build_data)
    result = get_selected_build_data(user1.id, build.id)

    assert result["generation_data"] == build_data
    assert result["user_preferences"] == prefs
