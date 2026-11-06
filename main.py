from flask import Flask, request, jsonify
from flask_cors import CORS
import base64
import xml.etree.ElementTree as ET
import io
import zipfile

app = Flask(__name__)
CORS(app)

PROP_ALLOW = {
    "Part": ["Name", "Position", "Size", "Color3uint8", "Material", "Anchored", "CanCollide", "Transparency", "Reflectance"],
    "Model": ["Name"],
    "Script": ["Name", "Source", "Disabled"],
    "LocalScript": ["Name", "Source", "Disabled"],
    "ModuleScript": ["Name", "Source"],
    "ScreenGui": ["Name", "IgnoreGuiInset", "ResetOnSpawn"],
    "TextLabel": ["Name", "Text", "TextSize", "BackgroundColor3uint8", "Position", "Size"],
    "TextButton": ["Name", "Text", "TextSize", "BackgroundColor3uint8", "Position", "Size"],
    "Frame": ["Name", "BackgroundColor3uint8", "Position", "Size"],
    "Folder": ["Name"],
    "RemoteEvent": ["Name"],
    "RemoteFunction": ["Name"],
    "Sky": ["Name", "CelestialBodiesShown"],
    "Camera": ["Name"],
    "Decal": ["Name", "Texture"],
    "MeshPart": ["Name", "Position", "Size", "MeshId", "Material"],
    "SpawnLocation": ["Name", "Position", "Size"],
    "Workspace": ["Name"],
    "Lighting": ["Name"],
}

def parse_value(elem):
    if elem is None:
        return None
    tag = elem.tag
    text = (elem.text or "").strip()
    if tag in ("Vector3", "CFrame", "Color3uint8"):
        return text
    if tag == "bool":
        return text.lower() == "true"
    if tag in ("int", "float", "double"):
        try:
            return float(text) if "." in text else int(text)
        except:
            return text
    return text

def parse_instance(elem):
    class_name = elem.get("class", "Unknown")
    name = ""
    props = {}
    allowed = PROP_ALLOW.get(class_name, ["Name"])
    for prop in elem.findall("Properties/*"):
        prop_name = prop.get("name")
        if prop_name in allowed:
            val_elem = prop.find("./*")
            if￼Enter
