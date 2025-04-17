"""This module provides a class to interact with the Monday.com API to update boards and items.
It includes methods to add items and subitems to a Monday.com board.
Classes:
    MondayBoardUpdater: A class to interact with the Monday.com API to update boards and items.
Example usage:
    MONDAY_API_KEY = "your_api_key_here"
    updater = MondayBoardUpdater(MONDAY_API_KEY)"""
from datetime import datetime
import json
import random
import requests


class MondayBoardUpdater:
    """
    A class to interact with the Monday.com API to update boards and items.
    This class provides methods to add items and subitems to a Monday.com board.
    """

    def __init__(self, api_key):
        """
        Initializes the MondayBoardUpdater with the provided API key.

        Args:
            api_key (str): The API key to authenticate with Monday.com API.
        """
        self.api_key = api_key
        self.url = "https://api.monday.com/v2"
        self.headers = {
            "Authorization": self.api_key,
            "Content-Type": "application/json",
        }

    def add_item(
        self, board_id, item_name, succ_count, status_label, comp_date, owner_id
    ):
        """
        Adds a new item to the specified board and group on Monday.com.

        Args:
            board_id (int): The ID of the board to add the item to.
            group_id (str): The ID of the group within the board.
            item_name (str): The name of the item to be created.
            exec_time (int): The execution time for the item.
            status_label (str): The status label of the item.
            req_date (str): The required date for the item (in YYYY-MM-DD format).
            comp_date (str): The completion date for the item (in YYYY-MM-DD format).
            owner_id (int): The ID of the owner for the item.

        Returns:
            int: The ID of the newly created item.
        """
        group_id = self.get_or_create_group(board_id, comp_date)
        payload = json.dumps(
            {
                "query": f'mutation {{create_item (board_id: {board_id}, group_id: "{group_id}", '
                f'item_name: "{item_name}", column_values: "{{\\"numbers\\": \\"{succ_count}\\", '
                f'\\"status1\\": {{\\"label\\": \\"{status_label}\\"}}, \\"date5\\": {{\\"date\\": \\"{comp_date}\\"}}, \\"people2\\": '
                f'{{\\"personsAndTeams\\":[{{\\"id\\":{owner_id},\\"kind\\":\\"person\\"}}]}}, \\"dropdown98\\": \\"Natera\\"}}") {{id}}}}'
            }
        )

        response = requests.post(
            self.url, headers=self.headers, data=payload, timeout=10
        )
        response_dict = json.loads(response.text)
        return response_dict["data"]["create_item"]["id"]

    def get_or_create_group(self, board_id, comp_date):
        """
        Checks if a group with the current month and year exists on the specified board.
        If the group exists, returns its ID. Otherwise, creates a new group in the format
        'Month Year' and returns the new group's ID.

        Args:
            board_id (int): The ID of the board to check or create the group on.

        Returns:
            str: The ID of the existing or newly created group.
        """
        current_month = datetime.strptime(comp_date, "%Y-%m-%d").strftime("%B")

        # Query to get all groups on the board
        query = json.dumps(
            {"query": f"{{boards (ids: {board_id}) {{groups {{id title}}}}}}"}
        )

        response = requests.post(self.url, headers=self.headers, data=query, timeout=10)
        response_dict = json.loads(response.text)

        # Check if the group already exists
        for group in response_dict["data"]["boards"][0]["groups"]:
            if group["title"] == current_month:
                return group["id"]

        colors = [
            "dark-green",
            "orange",
            "blue",
            "red",
            "green",
            "grey",
            "dark-blue",
            "purple",
            "yellow",
            "lime-green",
            "brown",
            "dark-red",
            "trolley-grey",
            "dark-purple",
            "dark-orange",
            "dark-pink",
            "turquoise",
            "light-pink",
        ]
        group_color = random.choice(colors)
        # If the group does not exist, create it
        mutation = json.dumps(
            {
                "query": f'mutation {{create_group (board_id: {board_id}, group_name: "{current_month}", group_color: "{group_color}") {{id}}}}'
            }
        )

        response = requests.post(
            self.url, headers=self.headers, data=mutation, timeout=10
        )
        response_dict = json.loads(response.text)

        return response_dict["data"]["create_group"]["id"]


# Example usage
MONDAY_API_KEY = (
    """eyJhbGciOiJIUzI1NiJ9.eyJ0aWQiOjQzODU0ODE5OCwiYWFpIjoxMSwid
WlkIjo2ODcyMjg3OSwiaWFkIjoiMjAyNC0xMS0xOVQxNToxODozMS4wMDB
aIiwicGVyIjoibWU6d3JpdGUiLCJhY3RpZCI6OTkyMzIyMCwicmduIjoidX
NlMSJ9.dMl4U9w2IQgX_AWdRyar1cwidd4meFHtGEXn2_ZLa1Q"""
).replace("\n", "")
updater = MondayBoardUpdater(MONDAY_API_KEY)
today_date = datetime.now().strftime("%Y-%m-%d")

itemname = "Meetings"
# itemname = "Posting"
# itemname = "AOR Syncer"
# itemname = "PA Fax Forms"
# itemname = "MMR,LIMS,AOR Backlog and moving to aws secrets"
# itemname = "LOA workflow"
# itemname = "Sasiru Mondayboard KT"
# itemname = "LIMS Refactoring"
# Fetch the JSON data from the provided URL
current_date = datetime.strptime(today_date, "%Y-%m-%d")
date = current_date.strftime("%Y-%m-%d")
if current_date.weekday() >= 5:  # 5 is Saturday, 6 is Sunday
    exit()
url = "https://gist.githubusercontent.com/eXtizi/222ab3e3ef962fffd240954978682b85/raw/table.json"
response = requests.get(url)
hours_and_items = response.json()


for itemname, hours in hours_and_items.items():

    item_id = updater.add_item(8137873748, itemname, hours, "Meetings", date, 68722879)
    print(f"Item ID: {item_id}",itemname, hours, date)
