import json
import os
import sys

def get_bundle_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    return os.path.join(base_path, relative_path)

def load_stylesheet(theme_name):
    json_path = get_bundle_path(os.path.join("themes", f"{theme_name}.json"))
    qss_path = get_bundle_path(os.path.join("themes", "style.qss"))

    with open(json_path, 'r') as f:
        colors = json.load(f)

    with open(qss_path, 'r') as f:
        style = f.read()

    for key, value in colors.items():
        style = style.replace(f"{{{{{key}}}}}", value)

    return style