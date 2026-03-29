"""
Gmail Integration for CRM Digital FTE
Receives and sends emails via Gmail API
"""

import os
import base64
import logging
from typing import List, Dict, Optional, Any
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import pickle

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from kafka.producer import KafkaProducerService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Gmail API Scopes
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly',
          'https://www.googleapis.com/auth/gmail.send',
          'https://www.googleapis.com/auth/gmail.modify']


class GmailIntegration:
    """Gmail Integration for receiving and sending support emails"""
    
    def __init__(
        self,
        credentials_file: str = "credentials.json",
        token_file: str = "token.pickle",
        support_email: str = "support@techcorp.com"
    ):
        self.credentials_file = credentials_file
        self.token_file = token_file
        self.support_email = support_email
        self.service = None
        self.producer = KafkaProducerService()
        self._authenticate()
    
    def _authenticate(self):
        """Authenticate with Gmail API"""
        try:
            creds = None
            
            # Load existing token
            if os.path.exists(self.token_file):
                with open(self.token_file, 'rb') as token:
                    creds = pickle.load(token)
            
            # Refresh or get new credentials
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    flow = InstalledAppFlow.from_client_secrets_file(
                        self.credentials_file, SCOPES
                    )
                    creds = flow.run_local_server(port=0)
                
                # Save credentials
                with open(self.token_file, 'wb') as token:
                    pickle.dump(creds, token)
            
            # Build service
            self.service = build('gmail', 'v1', credentials=creds)
            logger.info(f"✅ Authenticated as {self.support_email}")
            
        except Exception as e:
            logger.error(f"❌ Gmail authentication failed: {e}")
            raise
    
    def receive_emails(self, max_results: int = 10) -> List[Dict]:
        """
        Receive support emails from Gmail
        
        Args:
            max_results: Maximum number of emails to fetch
            
        Returns:
            List of email dictionaries
        """
        emails = []
        
        try:
            # Fetch unread emails
            results = self.service.users().messages().list(
                userId='me',
                q='is:unread from:-me',
                maxResults=max_results
            ).execute()
            
            messages = results.get('messages', [])
            
            for msg in messages:
                email_data = self._parse_email(msg['id'])
                if email_data:
                    emails.append(email_data)
                    
                    # Mark as read
                    self.service.users().messages().modify(
                        userId='me',
                        id=msg['id'],
                        body={'removeLabelIds': ['UNREAD']}
                    ).execute()
                    
                    # Send to Kafka for processing
                    self.producer.send_incoming_message({
                        'type': 'email',
                        'channel': 'email',
                        'customer': email_data['from']['email'],
                        'subject': email_data['subject'],
                        'content': email_data['body'],
                        'priority': 'medium',
                        'message_id': email_data['id']
                    })
            
            logger.info(f"📬 Received {len(emails)} new emails")
            
        except HttpError as error:
            logger.error(f"❌ Gmail API error: {error}")
        
        return emails
    
    def _parse_email(self, message_id: str) -> Optional[Dict]:
        """Parse email message"""
        try:
            message = self.service.users().messages().get(
                userId='me',
                id=message_id,
                format='full'
            ).execute()
            
            headers = message['payload']['headers']
            
            email_data = {
                'id': message_id,
                'from': self._extract_header(headers, 'From'),
                'to': self._extract_header(headers, 'To'),
                'subject': self._extract_header(headers, 'Subject'),
                'date': self._extract_header(headers, 'Date'),
                'body': '',
                'attachments': []
            }
            
            # Parse email body
            email_data['body'] = self._get_email_body(message['payload'])
            
            # Parse email addresses
            from_email = email_data['from']
            if '<' in from_email:
                name_part, email_part = from_email.split('<')
                email_data['from'] = {
                    'name': name_part.strip().strip('"'),
                    'email': email_part.strip('>')
                }
            else:
                email_data['from'] = {'name': '', 'email': from_email}
            
            return email_data
            
        except Exception as e:
            logger.error(f"Error parsing email: {e}")
            return None
    
    def _extract_header(self, headers: List, name: str) -> str:
        """Extract header value by name"""
        for header in headers:
            if header['name'].lower() == name.lower():
                return header['value']
        return ''
    
    def _get_email_body(self, payload: Dict) -> str:
        """Get email body from payload"""
        body = ''
        
        if 'parts' in payload:
            # Multipart email
            for part in payload['parts']:
                if part['mimeType'] == 'text/plain':
                    if 'data' in part['body']:
                        body = base64.urlsafe_b64decode(
                            part['body']['data'].encode('ASCII')
                        ).decode('utf-8')
                        break
        elif 'body' in payload['body']:
            # Simple email
            body = base64.urlsafe_b64decode(
                payload['body']['data'].encode('ASCII')
            ).decode('utf-8')
        
        return body
    
    def send_email(
        self,
        to: str,
        subject: str,
        body: str,
        html: bool = False,
        in_reply_to: Optional[str] = None
    ) -> bool:
        """
        Send email via Gmail
        
        Args:
            to: Recipient email
            subject: Email subject
            body: Email body
            html: Whether body is HTML
            in_reply_to: Message ID to reply to
            
        Returns:
            True if sent successfully
        """
        try:
            # Create message
            message = MIMEMultipart('alternative')
            message['to'] = to
            message['from'] = self.support_email
            message['subject'] = subject
            
            if in_reply_to:
                message['In-Reply-To'] = in_reply_to
                message['References'] = in_reply_to
            
            # Add body
            if html:
                message.attach(MIMEText(body, 'html'))
            else:
                message.attach(MIMEText(body, 'plain'))
            
            # Encode and send
            raw_message = base64.urlsafe_b64encode(
                message.as_bytes()
            ).decode('utf-8')
            
            sent_message = self.service.users().messages().send(
                userId='me',
                body={'raw': raw_message}
            ).execute()
            
            logger.info(f"📤 Email sent to {to}: {sent_message['id']}")
            
            # Send to Kafka for tracking
            self.producer.send_outgoing_message({
                'type': 'email',
                'channel': 'email',
                'customer': to,
                'subject': subject,
                'message_id': sent_message['id'],
                'timestamp': datetime.now().isoformat()
            })
            
            return True
            
        except HttpError as error:
            logger.error(f"❌ Failed to send email: {error}")
            return False
        except Exception as e:
            logger.error(f"❌ Unexpected error: {e}")
            return False
    
    def send_reply(
        self,
        to: str,
        subject: str,
        body: str,
        original_message_id: str
    ) -> bool:
        """Send reply to an email"""
        return self.send_email(
            to=to,
            subject=f"Re: {subject}",
            body=body,
            in_reply_to=original_message_id
        )
    
    def poll_emails(self, interval_seconds: int = 30):
        """
        Continuously poll for new emails
        
        Args:
            interval_seconds: Polling interval
        """
        logger.info(f"📬 Starting email polling (interval: {interval_seconds}s)")
        
        import time
        
        try:
            while True:
                self.receive_emails()
                time.sleep(interval_seconds)
        except KeyboardInterrupt:
            logger.info("⏹️  Email polling stopped")


# ==================== USAGE EXAMPLE ====================

if __name__ == "__main__":
    print("=" * 60)
    print("📧 Gmail Integration - CRM Digital FTE")
    print("=" * 60)
    
    # Initialize Gmail integration
    gmail = GmailIntegration()
    
    # Receive emails
    emails = gmail.receive_emails(max_results=5)
    
    for email in emails:
        print(f"\n📨 New Email:")
        print(f"   From: {email['from']['email']}")
        print(f"   Subject: {email['subject']}")
        print(f"   Body: {email['body'][:100]}...")
    
    # Send test email
    # gmail.send_email(
    #     to="customer@example.com",
    #     subject="Re: Your Support Request",
    #     body="Thank you for contacting support..."
    # )
    
    # Start polling
    # gmail.poll_emails(interval_seconds=30)
