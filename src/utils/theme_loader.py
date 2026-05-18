import json
import os

def load_stylesheet(theme_name):
    # Paths to your files
    base_path = os.path.dirname(os.path.abspath(__file__))
    json_path = os.path.join(base_path, "..", "themes", f"{theme_name}.json")
    qss_path = os.path.join(base_path, "..", "themes", "style.qss")

    with open(json_path, 'r') as f:
        colors = json.load(f)

    with open(qss_path, 'r') as f:
        style = f.read()

    # Replace placeholders with actual hex codes
    for key, value in colors.items():
        style = style.replace(f"{{{{{key}}}}}", value)

    return style