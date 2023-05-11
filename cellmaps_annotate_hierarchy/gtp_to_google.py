import google.auth
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.oauth2 import service_account

def create_or_overwrite_doc(doc_name, folder_id, creds_path):
    try:
        # Create a service object for Google Drive API
        credentials = service_account.Credentials.from_service_account_file(creds_path, scopes=["https://www.googleapis.com/auth/drive", "https://www.googleapis.com/auth/documents"])
        drive_service = build('drive', 'v3', credentials=credentials)
        docs_service = build('docs', 'v1', credentials=credentials)

        # Check if a doc with the same name already exists in the folder
        query = f"mimeType='application/vnd.google-apps.document' and trashed = false and parents in '{folder_id}' and name='{doc_name}'"
        results = drive_service.files().list(q=query, fields="nextPageToken, files(id, name)").execute()
        items = results.get("files", [])

        if items:
            # Overwrite the existing doc
            doc_id = items[0]["id"]
            requests = [{"deleteContentRange": {"range": {"startIndex": 1, "endIndex": "\ufffd"}}}]
            docs_service.documents().batchUpdate(documentId=doc_id, body={"requests": requests}).execute()

            print(f"Overwritten Google Doc with ID: {doc_id}")
            return doc_id
        else:
            # Create a new doc in the folder
            doc_metadata = {
                "name": doc_name,
                "mimeType": "application/vnd.google-apps.document",
                "parents": [folder_id],
            }
            doc = drive_service.files().create(body=doc_metadata).execute()
            doc_id = doc["id"]

            print(f"Created Google Doc with ID: {doc_id}")
            return doc_id

    except HttpError as error:
        print(f"An error occurred: {error}")
        return None

# Example usage
if __name__ == "__main__":
    doc_name = "My New Google Doc"
    folder_id = "FOLDER_ID_GOES_HERE"  # Replace with your folder ID
    creds_path = "path/to/credentials.json"  # Replace with your credentials file path
    create_or_overwrite_doc(doc_name, folder_id, creds_path)
