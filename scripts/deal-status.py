import requests
import pandas as pd
import json

# Base URL for API requests
# BASE_URL = "http://192.168.1.40:9090/api"
# BASE_URL = "http://192.168.1.125:9090/api"
BASE_URL = "http://192.168.1.5:9090/api"

# Enter filename to save the output
OUTPUT_FILENAME = "gedi_tutorial_payload"

# Enter the preparation ID you want to process. If 0, all preparations will be processed.
PREP_ID = 2

# Export a list of all the directories and files in the preparation
# Set the source id that is linked to the preparation
EXPORT_FILES = False
SOURCE_ID = 2


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


def get_preparations():
    preparations_response = make_get_request("/preparation")
    if preparations_response:
        return preparations_response
    return []


def get_pieces_for_preparation(prep_id, prep_name):
    pieces_response = make_get_request(f"/preparation/{prep_id}/piece")
    if pieces_response:
        just_the_pieces = [item["pieces"] for item in pieces_response]
        just_the_pieces = [item for sublist in just_the_pieces for item in sublist]
        just_the_pieces = [{**d, "name": prep_name} for d in just_the_pieces]
        return just_the_pieces
    return []


def get_deal_status_for_preparation(prep_id):
    data = {"preparations": [f"{prep_id}"]}
    deal_status_response = make_post_request("/deal", data)
    if deal_status_response:
        deal_status_response = [
            {**d, "preparationId": prep_id} for d in deal_status_response
        ]
        return deal_status_response
    return []


def process_preparations(prep_id: int = 0) -> tuple[pd.DataFrame, pd.DataFrame]:
    preparations = get_preparations()
    all_pieces_data = []
    all_deals_data = []

    if prep_id > 0:
        preparations = [prep for prep in preparations if prep["id"] == prep_id]

    for prep in preparations:
        prep_id = prep["id"]
        prep_name = prep["name"]

        pieces = get_pieces_for_preparation(prep_id, prep_name)
        all_pieces_data.extend(pieces)

        deals = get_deal_status_for_preparation(prep_id)
        all_deals_data.extend(deals)

    all_pieces_df = pd.DataFrame(all_pieces_data)
    all_deals_df = pd.DataFrame(all_deals_data)

    return all_pieces_df, all_deals_df


def get_pieces_count_by_prep(all_pieces_df):
    return (
        all_pieces_df.groupby("preparationId")
        .size()
        .reset_index()
        .rename(columns={0: "TotalPieces"})
    )


def get_pieces_count_by_prep_status(all_deals_df):
    return (
        all_deals_df.groupby(["preparationId", "state"])
        .size()
        .reset_index()
        .rename(columns={0: "pieceCount"})
    )


def get_deals_count(all_deals_df):
    return (
        all_deals_df.groupby("scheduleId")
        .size()
        .reset_index()
        .rename(columns={0: "pieceCount"})
    )


def get_pieces_count_by_deal_status(all_deals_df):
    return (
        all_deals_df.groupby("state")
        .size()
        .reset_index()
        .rename(columns={0: "pieceCount"})
    )


def get_pieces_count_by_deal_piece(all_deals_df):
    return (
        all_deals_df.groupby("pieceCid")
        .size()
        .reset_index()
        .rename(columns={0: "dealCount"})
    )


def print_summary_statistics(all_pieces_df, all_deals_df) -> None:

    pieces_count_by_prep = get_pieces_count_by_prep(all_pieces_df)
    pieces_count_by_prep_status = get_pieces_count_by_prep_status(all_deals_df)
    deals_count = get_deals_count(all_deals_df)
    pieces_count_by_deal_status = get_pieces_count_by_deal_status(all_deals_df)
    pieces_count_by_deal_piece = get_pieces_count_by_deal_piece(all_deals_df)

    print("Summary statistics:")
    print("Total number of pieces by preparation ID:")
    print(pieces_count_by_prep)
    print("\nTotal number of pieces by preparation ID and status:")
    print(pieces_count_by_prep_status)
    print("\nTotal number of deals by status:")
    print(deals_count)
    print("\nTotal number of pieces by deal:")
    print(pieces_count_by_deal_status)
    print("\nTotal number of pieces by deal piece:")
    print(pieces_count_by_deal_piece)


def get_file_details_from_piece(all_pieces_df):
    # loop through each piece and get all the file details from the api request `/piece/<piece id>/metadata'`
    file_details = []

    for index, row in all_pieces_df.iterrows():
        pieceCid = row["pieceCid"]
        rootCid = row["rootCid"]

        metadata_response = make_get_request(f"/piece/{pieceCid}/metadata")
        if metadata_response:

            # grab the files dict from the response and loop the list of dicts
            file_metadata = metadata_response["files"]

            # loop through each list of dicts in file_metadata:
            # - create empty dict holder to store the file details
            # - split the `path` key into two components, file_path and file_name based on the character `/`
            # - append the missing '/' to the file_path which takes care of the case where the path is empty
            # - add the rootCid and pieceCid key/value that comes from the dict `car` in metadata response
            # extend the in loop dict to the file_details list

            for file in file_metadata:
                file_details_dict = {}
                file_details_dict.update(file)
                # Split the path check if it has a path or not
                file_parts = file["path"].rsplit("/", 1)
                if len(file_parts) == 2:
                    file_path, file_name = file_parts
                else:
                    file_path, file_name = "", file_parts[0]
                file_details_dict["path"] = file_path
                file_details_dict["fileName"] = file_name
                file_details_dict["rootCid"] = rootCid
                file_details_dict["pieceCid"] = pieceCid
                file_details.append(file_details_dict)

    return pd.DataFrame(file_details)


def fetch_sub_entries(prep_id, source_id, path="/"):
    """
    Fetches sub-entries from the API endpoint and returns a list of lists containing 'cid' and 'path'.
    Recursively explores directories if 'isDir' is True.

    Args:
        prep_id (str): Preparation ID.
        source_id (str): Source ID.
        path (str): Path to explore (default is root).

    Returns:
        list: A list of lists containing 'cid' and 'path'.
    """
    url = f"/preparation/{prep_id}/source/{source_id}/explore/{path}"
    data = make_get_request(url)

    if not data:
        return []

    result = []

    for entry in data.get("subEntries", []):
        result.append([entry["cid"], entry["path"]])
        if entry.get("isDir"):
            # Recursively fetch sub-entries for directories
            result.extend(fetch_sub_entries(prep_id, source_id, entry["path"]))

    return result


if __name__ == "__main__":

    # Create a list of all the directories and files in the preparation
    if EXPORT_FILES:
        files_from_prep = fetch_sub_entries(PREP_ID, SOURCE_ID)
        # convert list of lists to a dataframe and modify the path column to only contain the file/directory name
        files_from_prep_df = pd.DataFrame(files_from_prep, columns=["cid", "path"])
        files_from_prep_df["path"] = files_from_prep_df["path"].apply(
            lambda x: x.split("/")[-1]
        )
        files_from_prep_df.to_json(
            f"{OUTPUT_FILENAME}.json", orient="records", lines=False
        )

    pieces_df, deals_df = process_preparations(PREP_ID)
    file_deets = get_file_details_from_piece(pieces_df)
    file_deets.to_csv(f"{OUTPUT_FILENAME}.csv", index=False)
