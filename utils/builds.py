from flask import jsonify
import json
from data import db, User, lookup_user_by_email, Build


# Helper functions for build management routes

def get_selected_build_data(user_id: int, build_id: int):
    build = Build.query.filter_by(id=build_id, linked_user_id=user_id).first()
    if not build:
        raise ValueError("Build not found")

    user = User.query.filter_by(id=user_id).first()
    return {
        "generation_data": json.loads(build.get_generation_data()),
        "user_preferences": json.loads(user.visual_settings or "{}")
    }


def create_new_build(user_id: int, build_name: str, generation_data: dict):
    new_build = Build(
        build_name=build_name,
        build_description="Build description goes here",
        generation_data=None,
        linked_user_id=user_id
    )
    new_build.set_generation_data(json.dumps(generation_data))
    db.session.add(new_build)
    db.session.commit()
    return new_build


def update_existing_build(user_id: int, build_id: int, generation_data: dict):
    build = Build.query.filter_by(id=build_id, linked_user_id=user_id).first()
    if not build:
        raise ValueError("Build not found")
    build.set_generation_data(json.dumps(generation_data))
    db.session.commit()


def rename_existing_build(user_id: int, build_id: int, new_name: str):
    build = Build.query.filter_by(id=build_id, linked_user_id=user_id).first()
    if not build:
        raise ValueError("Build not found")
    build.build_name = new_name.replace("\\", "")
    db.session.commit()


def update_build_description(user_id: int, build_id: int, new_desc: str):
    build = Build.query.filter_by(id=build_id, linked_user_id=user_id).first()
    if not build:
        raise ValueError("Build not found")
    build.build_description = new_desc.replace("\\", "")
    db.session.commit()


def delete_user_build(user_id: int, build_id: int):
    build = Build.query.filter_by(id=build_id, linked_user_id=user_id).first()
    if not build:
        raise ValueError("Build not found or not authorized")
    db.session.delete(build)
    db.session.commit()


def copy_user_build(user_id: int, name_str: str, generation_data: dict):
    build_name, build_description = name_str.split(";")
    copied_build = Build(
        build_name=build_name + " (Copy)",
        build_description=build_description[1:],
        generation_data=None,
        linked_user_id=user_id
    )
    copied_build.set_generation_data(json.dumps(generation_data))
    db.session.add(copied_build)
    db.session.commit()

def store_visual_preferences(user_id: int, preferences: dict):
    user = User.query.filter_by(id=user_id).first()
    if not user:
        raise ValueError("User not found")
    user.visual_settings = json.dumps(preferences)
    db.session.commit()