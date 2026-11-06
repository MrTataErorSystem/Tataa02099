herefrom flask import Flask, request, jsonify
from flask_cors import CORS
import base64
import xml.etree.ElementTree as ET
import io
import zipfile

app = Flask(__name__)
CORS(app)

# Mapping properti yang penting aja, biar JSON ga jebol
# Kalau lu mau full 100%, tambahin sendiri di sini
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
    "Tool": ["Name"],
}

def parse_vector3(text):
    # Format XML: "0, 10, 0"
    try:
        parts = text.replace(" ", "").split(",")
        return [float(x) for x in parts]
    except:
        return [0,0,0]

def parse_item(elem):
    # elem = <Item class="Part" referent="...">
    class_name = elem.get("class")
    props = {}
    children = []
    
    prop_elem = elem.find("Properties")
    if prop_elem is not None:
        for p in prop_elem:
            pname = p.get("name")
            # Ambil yang ada di allow list, atau Name selalu ambil
            if pname == "Name" or pname in PROP_ALLOW.get(class_name, []):
                if p.tag == "string":
                    props[pname] = p.text or ""
                elif p.tag in ["Vector3", "CoordinateFrame"]:
                    # CoordinateFrame ambil Position aja biar simpel
                    if p.tag == "CoordinateFrame":
                        pos = p.find("X")
                        # Simplified: ambil <Position>
                        pos_elem = p.find("Position")
                        if pos_elem is not None:
                            props["Position"] = parse_vector3(pos_elem.text)
                    else:
                        props[pname] = parse_vector3(p.text or "0,0,0")
                elif p.tag == "Color3uint8":
                    props[pname] = p.text or "255,255,255"
                elif p.tag == "bool":
                    props[pname] = p.text == "true"
                elif p.tag in ["float", "double", "int", "int64"]:
                    try: props[pname] = float(p.text)
                    except: props[pname] = 0
                elif p.tag == "ProtectedString":
                    props[pname] = p.text or ""
                elif p.tag == "Enum":
                    props[pname] = p.text or ""
                else:
                    if p.text:
                        props[pname] = p.text

    # Children
    for child in elem.findall("Item"):
        children.append(parse_item(child))
    
    return {
        "Class": class_name,
        "Props": props,
        "Children": children
    }

@app.route("/")
def home():
    return jsonify({"status": "CAA Worker Full Service - ONLINE"})

@app.route("/convert", methods=["POST"])
def convert():
    try:
        data = request.get_json()
        b64 = data.get("file")
        if not b64:
            return jsonify({"error": "no file"}), 400
        
        raw = base64.b64decode(b64)
        
        # Cek apakah ini rbxlx (XML) atau rbxl (Binary)
        # Kalau binary, di Render lu harus convert dulu via rojo, tapi 90% file dari Studio Lite itu XML
        if raw[:5] == b"<roblox":
            root = ET.fromstring(raw)
        else:
            # Binary RBXL - kasih pesan suruh convert ke RBXLX dulu di Studio
            return jsonify({
                "error": "BINARY_RBXL",
                "message": "File masih binary .rbxl. Buka di Studio > Save As > pilih .rbxlx (XML). Atau kirim file .rbxlx"
            }), 400

        result = {}
        # Root is <roblox><Item class="DataModel">...
        for item in root.findall("Item"):
            if item.get("class") == "DataModel":
                for service in item.findall("Item"):
                    service_name = service.get("class")
                    # Ambil Name asli dari Properties
                    name_prop = service.find("Properties/Name")
                    if name_prop is not None and name_prop.text:
                        service_name = name_prop.text
                    
                    service_children = []
                    for child in service.findall("Item"):
                        service_children.append(parse_item(child))
                    
                    result[service_name] = service_children
        
        return jsonify({"success": True, "services": result})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
￼Enter
