from datetime import datetime
from babel.dates import format_date

def handler(inputs):
    format_option = inputs.get("format", "iso")
    locale = inputs.get("locale", "en_US")
    now = datetime.now()

    if format_option == "iso":
        formatted_date = now.isoformat()
    elif format_option == "locale":
        formatted_date = now.strftime("%c")
    elif format_option == "localized":
        try:
            formatted_date = format_date(now.date(), format='long', locale=locale)
        except Exception as e:
            return {"error": f"Invalid locale for Babel: {e}"}
    else:
        try:
            formatted_date = now.strftime(format_option)
        except Exception as e:
            return {"error": f"Invalid format string: {e}"}

    return {"date": formatted_date}

# Example usage:
# print(handler({"format": "localized", "locale": "de_DE"}))
# print(handler({"format": "%d.%m.%Y"}))
