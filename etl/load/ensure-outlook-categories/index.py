import json
import os
import urllib.error
import urllib.request


def handler(inputs):
    custom_categories = inputs.get("customCategories") or []
    outlook_token = (os.getenv("OUTLOOK_API_KEY") or "").strip()
    if not custom_categories or not outlook_token:
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

    base = "https://graph.microsoft.com/v1.0/me/outlook/masterCategories"
    headers = {"Authorization": "Bearer " + outlook_token, "Content-Type": "application/json"}
    existing = set()
    try:
        req = urllib.request.Request(base, headers=headers)
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode())
        for c in data.get("value", []):
            existing.add((c.get("displayName") or "").strip())
    except Exception:
        pass

    created = []
    for display_name, color in desired:
        if display_name in existing:
            continue
        try:
            body = json.dumps({"displayName": display_name, "color": color}).encode()
            req = urllib.request.Request(base, data=body, headers=headers, method="POST")
            with urllib.request.urlopen(req):
                created.append(display_name)
                existing.add(display_name)
        except urllib.error.HTTPError as e:
            if e.code != 409:
                raise

    return {"created": created, "existing": list(existing)}
