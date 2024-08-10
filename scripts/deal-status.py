import requests
import pandas as pd
import json

# Base URL for API requests
BASE_URL = "https://singularity.easierdata.info/api"


def make_post_request(endpoint, data=None):
    """Make a POST request to a specified endpoint."""
    headers = {
        "accept": "application/json",
        "Content-Type": "application/json; charset=UTF-8",
    }

    try:
        response = requests.post(
            f"{BASE_URL}{endpoint}", headers=headers, data=json.dumps(data)
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return None


def make_get_request(endpoint):
    """Make a POST request to a specified endpoint."""
    headers = {
        "accept": "application/json",
        "Content-Type": "application/json; charset=UTF-8",
    }
    try:
        response = requests.get(f"{BASE_URL}{endpoint}", headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return None


def process_preparations():
    preparations_response = make_get_request("/preparation")
    if preparations_response:
        preparations = preparations_response  # Assuming this is a list of dicts
        all_pieces_data = []
        all_deals_data = []

        for prep in preparations:

            # Get the pieces for each preparation
            prep_id = prep["id"]  # Assuming each preparation has an 'id'
            pieces_response = make_get_request(f"/preparation/{prep_id}/piece")
            if pieces_response:
                # Extract the pieces from each item in the list and then loop through each pieces in the list and extend into a dictionary of lists
                just_the_pieces = [item["pieces"] for item in pieces_response]
                just_the_pieces = [
                    item for sublist in just_the_pieces for item in sublist
                ]

                # Add the piece_name to the pieces data
                just_the_pieces = [{**d, "name": prep["name"]} for d in just_the_pieces]
                all_pieces_data.extend(just_the_pieces)

            # Get the pieces in deals for each preparation
            # Create data payload to send into post request
            data = {"preparations": [f"{prep_id}"]}

            deal_status_response = make_post_request("/deal", data)
            if deal_status_response:
                # Add preparation id to each deal status record
                deal_status_response = [
                    {**d, "preparationId": prep_id} for d in deal_status_response
                ]

                # Add deal status data
                all_deals_data.extend(deal_status_response)
            else:
                print(
                    f"No deals have been made for prepartion id {prep_id} - {prep['name']}"
                )

        # Assuming all_pieces_data is a list of dicts
        all_pieces_df = pd.DataFrame(all_pieces_data)
        all_deals_df = pd.DataFrame(all_deals_data)

        # Get a count of pieces by preperation ID and rename the column to reflect the count
        pieces_count_by_prep = (
            all_pieces_df.groupby("preparationId")
            .size()
            .reset_index()
            .rename(columns={0: "TotalPieces"})
        )

        # Get a count of pieces by preparation ID for scheduled deals. Note, that there may be duplicate pieceIds in the deals data so we need to drop duplicates
        pieces_count_by_prep_deal = (
            all_deals_df.drop_duplicates(subset=["pieceCid"])
            .groupby("preparationId")
            .size()
            .reset_index()
            .rename(columns={0: "ScheduledPieces"})
        )

        pieces_count_by_prep = pd.merge(
            pieces_count_by_prep,
            pieces_count_by_prep_deal,
            on="preparationId",
            how="left",
        )
        # Fill NaN values with 0 and convert to integer
        pieces_count_by_prep["ScheduledPieces"] = (
            pieces_count_by_prep["ScheduledPieces"].fillna(0).astype(int)
        )

        # Get a count of pieces by preparation ID and status
        pieces_count_by_prep_status = (
            all_deals_df.groupby(["preparationId", "state"])
            .size()
            .reset_index()
            .rename(columns={0: "pieceCount"})
        )

        # Get a count of deals and the number of pieces in each deal, regardless of status or preparation ID
        deals_count = (
            all_deals_df.groupby("scheduleId")
            .size()
            .reset_index()
            .rename(columns={0: "pieceCount"})
        )
        # Get a count of pieces in a deal grouped by status
        pieces_count_by_deal_status = (
            all_deals_df.groupby("state")
            .size()
            .reset_index()
            .rename(columns={0: "pieceCount"})
        )
        # Get a count of pieces that are in a deal, grouped by pieceCid
        pieces_count_by_deal_piece = (
            all_deals_df.groupby("pieceCid")
            .size()
            .reset_index()
            .rename(columns={0: "dealCount"})
        )

        # Further processing to identify preparations and pieces as per the flowchart
        # This would involve more detailed logic based on the structure of your data

        # Print summary statistics
        print("Summary statistics:")
        print("Total number of pieces by preparation ID:")
        print(pieces_count_by_prep)
        print("\nTotal number of pieces by preparation ID and status:")
        print(pieces_count_by_prep_status)
        print("\nTotal number of deals by status:")
        print(pieces_count_by_deal_status)
        print("\nTotal number of pieces by deal:")


if __name__ == "__main__":
    process_preparations()
