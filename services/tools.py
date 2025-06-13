import os
from typing import Dict

from dotenv import load_dotenv
import requests
from langchain.tools import tool
from datetime import date as dt_date
from models.tool_model import RestaurantSearchArgs, TableReserveArgs

load_dotenv()


RESTAURANT_SEARCH_URL = os.getenv('RESTAURANT_SEARCH_URL')
TABLE_RESERVE_URL = os.getenv('TABLE_RESERVE_URL')


@tool("search_restaurant",
      args_schema=RestaurantSearchArgs,
      description=f"Search for available restaurants based on city, locality, cuisine, date, and time: Note: Today's date is {dt_date.today().isoformat()})")
def search_restaurant_tool(city: str, locality: str, cuisine: str, date: str, time: str) -> Dict:
    """
        This tool searches for available restaurants based on the user's preferences.

        args:
            - city: Name of the city where the user wants to book a restaurant
            - locality: Specific area within the city
            - cuisine: Preferred cuisine type (e.g., Italian, Indian)
            - date: Reservation date in YYYY-MM-DD format (must be a valid future date)
            - time: Reservation time in 24-hour HH:MM format

        Returns:
            dict: JSON response from the restaurant search API or an error message.

        Raises:
            Exception: If the external API call fails or response parsing fails
        """
    try:
        params = {
            "city": city,
            "locality": locality,
            "cuisine": cuisine,
            "date": date,
            "time": time
        }

        headers = {
            "accept": "application/json",
            "Content-Type": "application/json"
        }

        response = requests.post(RESTAURANT_SEARCH_URL, json=params, headers=headers)
        tool_motive = {
                        "top_choice": response.json(),
                        "next_action": "Please use the reserve_table tool using this restaurant_id and user details from the query. "
                                        "as your final goal is to reserve a table."
                      }
        return tool_motive

    except Exception as e:
        return {"error": "Exception", "details": str(e)}


@tool(
    "reserve_table",
    return_direct=False,
    args_schema=TableReserveArgs,
    description="Reserve a table at a specific restaurant using restaurant ID, date, time, guest count, and user details."
                "NOTE: Before booking a table use 'search_restaurant' tool get the restaurant ID and to check the slot availability"
)
def reserve_table_tool(
    restaurant_id: str,
    date: str,
    time: str,
    guests: int,
    user_name: str,
    user_phone: str
):
    """
    Reserves a table at a restaurant.

    Args:
        - restaurant_id: Unique ID of the restaurant
        - date: Reservation date in YYYY-MM-DD format (must be a valid future date)
        - time: Reservation time in HH:MM format (24-hour)
        - guests: Number of guests to reserve the table for
        - user_name: Name of the person making the reservation
        - user_phone: User's phone number (e.g., +91XXXXXXXXXX)

    Returns:
        dict: JSON response from the restaurant reservation API with confirmation or error details.

    Raises:
        Exception: If the external API call fails or the response is invalid.
    """
    try:
        payload = {
            "restaurant_id": restaurant_id,
            "date": date,
            "time": time,
            "guests": guests,
            "user_name": user_name,
            "user_phone": user_phone
        }

        headers = {
            "accept": "application/json",
            "Content-Type": "application/json"
        }

        response = requests.post(TABLE_RESERVE_URL, json=payload, headers=headers)
        if response.ok:
            tool_motive = {
                "status": "success",
                "reservation_response": response.json()
            }
            return f"{tool_motive}"
        else:
            tool_motive = {
                "status": "error",
                "reservation_response": response.json()
            }
            return f"{tool_motive}"


    except Exception as e:
        return {"error": "Exception", "details": str(e)}





