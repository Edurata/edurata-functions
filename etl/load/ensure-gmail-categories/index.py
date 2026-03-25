import json
import os
import urllib.error
import urllib.request


def handler(inputs):
    custom_categories = inputs.get("customCategories") or []
    gmail_token = (os.getenv("GMAIL_API_KEY") or "").strip()
    if not custom_categories or not gmail_token:
        return {"created": [], "existing": []}

    lang = (inputs.get("lang") or "en").strip().lower()
    if lang not in ("de", "en"):
        lang = "en"

    color_presets = {"preset%d" % i for i in range(25)}
    color_name_to_preset = {
        "red": "preset0", "orange": "preset1", "brown": "preset2", "yellow": "preset3", "green": "preset4",
        "teal": "preset5", "olive": "preset6", "blue": "preset7", "purple": "preset8", "cranberry": "preset9",
        "steel": "preset10", "darksteel": "preset11", "gray": "preset12", "grey": "preset12", "darkgray": "preset13", "darkgrey": "preset13",
        "black": "preset14", "darkred": "preset15", "darkorange": "preset16", "darkbrown": "preset17", "darkyellow": "preset18",
        "darkgreen": "preset19", "darkteal": "preset20", "darkolive": "preset21", "darkblue": "preset22", "darkpurple": "preset23", "darkcranberry": "preset24",
    }

    def normalize_color(c):
        if not c:
            return "preset0"
        c = str(c).strip().lower()
        if c in color_presets:
            return c
        return color_name_to_preset.get(c, "preset0")

    def hex_to_int(x):
        try:
            return int(x, 16)
        except Exception:
            return 0

    def hex_luminance(rgb_hex):
        rgb_hex = (rgb_hex or "").strip().lstrip("#")
        if len(rgb_hex) != 6:
            return 1.0
        r = hex_to_int(rgb_hex[0:2]) / 255.0
        g = hex_to_int(rgb_hex[2:4]) / 255.0
        b = hex_to_int(rgb_hex[4:6]) / 255.0
        return 0.2126 * r + 0.7152 * g + 0.0722 * b

    gmail_bg_presets = [
        "#d93025", "#f29900", "#a16207", "#fbbc05", "#188038", "#00897b", "#6d4c41", "#1a73e8",
        "#7b1fa2", "#c2185b", "#37474f", "#2f3a3d", "#5f6368", "#3c4043", "#000000", "#8e0000",
        "#c75c0b", "#9c3f00", "#b76d00", "#0b8043", "#00796b", "#4e342e", "#0d47a1", "#6a1b9a",
        "#ad1457",
    ]

    def preset_to_gmail_colors(preset):
        preset = (preset or "").strip().lower()
        if preset.startswith("preset"):
            try:
                idx = int(preset.replace("preset", ""))
            except Exception:
                idx = 0
        else:
            idx = 0
        bg = gmail_bg_presets[idx] if 0 <= idx < len(gmail_bg_presets) else gmail_bg_presets[0]
        text = "#ffffff" if hex_luminance(bg) < 0.6 else "#000000"
        return {"backgroundColor": bg, "textColor": text}

    type_defaults = {
        "en": {
            "DISCRETE_THREE": [("high", "preset0"), ("medium", "preset3"), ("low", "preset4")],
            "SENTIMENT": [("positive", "preset4"), ("neutral", "preset3"), ("negative", "preset0")],
        },
        "de": {
            "DISCRETE_THREE": [("hoch", "preset0"), ("mittel", "preset3"), ("niedrig", "preset4")],
            "SENTIMENT": [("positiv", "preset4"), ("neutral", "preset3"), ("negativ", "preset0")],
        },
    }
    defaults_by_lang = type_defaults.get(lang, type_defaults["en"])

    def value_entries(cat):
        vals = cat.get("possibleValues") or cat.get("values") or []
        if vals:
            return vals
        t = (cat.get("type") or "").strip()
        if t in defaults_by_lang:
            return [{"name": n, "color": col} for n, col in defaults_by_lang[t]]
        return []

    desired = []
    for cat in custom_categories:
        cat_name = (cat.get("name") or "").strip()
        if not cat_name:
            continue
        for pv in value_entries(cat):
            val_name = (pv.get("name") or "").strip() if isinstance(pv, dict) else str(pv).strip()
            if not val_name:
                continue
            display_name = cat_name + ":" + val_name
            raw_color = (pv.get("color") or "preset0").strip() if isinstance(pv, dict) else "preset0"
            desired.append((display_name, normalize_color(raw_color)))

    base = "https://gmail.googleapis.com/gmail/v1/users/me/labels"
    headers = {"Authorization": "Bearer " + gmail_token, "Content-Type": "application/json"}
    existing = set()
    try:
        req = urllib.request.Request(base, headers=headers)
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode())
        for c in data.get("labels", []) or []:
            existing.add((c.get("name") or "").strip())
    except Exception:
        pass

    created = []
    for display_name, color in desired:
        if display_name in existing:
            continue
        try:
            payload = {
                "name": display_name,
                "labelListVisibility": "labelShowHide",
                "messageListVisibility": "showLabel",
                "color": preset_to_gmail_colors(color),
            }
            body = json.dumps(payload).encode()
            req = urllib.request.Request(base, data=body, headers=headers, method="POST")
            with urllib.request.urlopen(req):
                created.append(display_name)
                existing.add(display_name)
        except urllib.error.HTTPError as e:
            err_body = e.read().decode() if e.fp else ""
            if e.code in (409, 400) and "already" in (err_body or "").lower():
                continue
            raise

    return {"created": created, "existing": list(existing)}
