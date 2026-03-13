"""Google Docs integration for creating tailored resumes."""

import logging
import os
import io
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

from config import settings


# Need these scopes to duplicate and edit files
SCOPES = ['https://www.googleapis.com/auth/documents', 'https://www.googleapis.com/auth/drive']


logger = logging.getLogger(__name__)

class GoogleDocsService:
    """Service to interact with Google Docs and Drive APIs."""

    def __init__(self):
        self.creds = None
        self.docs_service = None
        self.drive_service = None
        
        # In a real app, this path comes from env
        service_account_file = os.getenv("GOOGLE_SERVICE_ACCOUNT_FILE")
        if service_account_file and os.path.exists(service_account_file):
            self.creds = Credentials.from_service_account_file(
                service_account_file, scopes=SCOPES
            )
            self.docs_service = build('docs', 'v1', credentials=self.creds)
            self.drive_service = build('drive', 'v3', credentials=self.creds)
        else:
            print("[Google Docs] Warning: GOOGLE_SERVICE_ACCOUNT_FILE not found. Mock mode active.")
            self._mock_mode = True

    @property
    def is_configured(self):
        return self.creds is not None

    async def create_tailored_doc(self, template_id: str, replacements: dict, new_title: str, folder_id: str = None) -> tuple[str, str]:
        """
        Duplicate a template doc and replace placeholders with tailored text.
        
        Args:
            template_id: Google Doc ID of the template
            replacements: Dict mapping "{{PLACEHOLDER}}" -> "Replacement text"
            new_title: Title for the newly created document
            folder_id: Optional ID of Drive folder to place it in
            
        Returns:
            Tuple of (Document ID, Document URL)
        """
        if getattr(self, '_mock_mode', False) or not self.is_configured:
            print(f"[Google Docs] Mocking creation of doc: {new_title}")
            return ("mock_doc_id", f"https://docs.google.com/document/d/mock_doc_id/edit")

        try:
            # 1. Duplicate the template via Drive API
            copy_body = {'name': new_title}
            if folder_id:
                copy_body['parents'] = [folder_id]
                
            drive_response = self.drive_service.files().copy(
                fileId=template_id, 
                body=copy_body,
                supportsAllDrives=True
            ).execute()
            
            new_doc_id = drive_response.get('id')
            print(f"[Google Docs] Duplicated template to new doc: {new_doc_id}")

            # 2. Setup batchUpdate requests to replace text
            requests = []
            for placeholder, text in replacements.items():
                requests.append({
                    'replaceAllText': {
                        'containsText': {
                            'text': placeholder,
                            'matchCase': True
                        },
                        'replaceText': text
                    }
                })

            # 3. Execute replacements via Docs API
            if requests:
                self.docs_service.documents().batchUpdate(
                    documentId=new_doc_id,
                    body={'requests': requests}
                ).execute()
                print(f"[Google Docs] Successfully updated {len(requests)} placeholders.")

            doc_url = f"https://docs.google.com/document/d/{new_doc_id}/edit"
            return new_doc_id, doc_url

        except Exception as e:
            print(f"[Google Docs] API Error: {e}")
            raise

    async def export_doc_as_pdf(self, doc_id: str, filepath: str) -> str:
        """
        Export a Google Doc as a PDF file to the local filesystem.
        """
        if getattr(self, '_mock_mode', False) or not self.is_configured:
            print(f"[Google Docs] Mocking PDF export to: {filepath}")
            # Touch a mock file
            with open(filepath, 'w') as f:
                f.write("Mock PDF content")
            return filepath

        try:
            request = self.drive_service.files().export_media(
                fileId=doc_id,
                mimeType='application/pdf'
            )
            
            with open(filepath, 'wb') as fh:
                downloader = MediaIoBaseDownload(fh, request)
                done = False
                while done is False:
                    status, done = downloader.next_chunk()
                    
            print(f"[Google Docs] Successfully exported PDF to {filepath}")
            return filepath

        except Exception as e:
            print(f"[Google Docs] PDF Export Error: {e}")
            raise


# Singleton
google_docs_service = GoogleDocsService()
