import os.path
import pathlib

import requests

BERLIN_MODEL_HELPERS_SPREADSHEET_ID = "1fbFNh-vpqlIljIg2OMlXmLCbqeV9ISL4eRaepW0jmjo"
SHEETS = {
    "conditions": 0,
    "clinical_findings-attributes": 1243051470,
    "attributes-value_sets": 1283340500,
}


def export_google_docs_sheet_to_csv(spreadsheet_id: str, sheet_id: int):
    return f"https://docs.google.com/spreadsheets/u/0/d/{spreadsheet_id}" \
           f"/export?format=csv&id={spreadsheet_id}&gid={sheet_id}"


for sheet_name, sheet_id in SHEETS.items():
    print(f"Download {sheet_name}...")

    print(export_google_docs_sheet_to_csv(BERLIN_MODEL_HELPERS_SPREADSHEET_ID, sheet_id))
    request = requests.get(
        export_google_docs_sheet_to_csv(BERLIN_MODEL_HELPERS_SPREADSHEET_ID, sheet_id)
    )

    if request.status_code != 200:
        print(f"Download failed, response code: {request.status_code}")
        continue

    csv_file_name = os.path.join(pathlib.Path(__file__).parent, f"{sheet_name}.csv")
    with open(csv_file_name, "wb") as sheet_file:
        sheet_file.write(request.content)
        print(f"Saved as {csv_file_name}")

    print("")
