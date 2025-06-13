from datetime import date as dt_date

def get_search_restaurant_description():
    tool_description = f"Search for available restaurants based on city, locality, cuisine, date, and time: Note: Today's date is {dt_date.today().isoformat()})"
