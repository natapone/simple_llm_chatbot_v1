"""
Google Sheets service for storing lead information.
"""

import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import os

import gspread
from gspread.exceptions import SpreadsheetNotFound
from google.oauth2.service_account import Credentials
from tenacity import retry, stop_after_attempt, wait_exponential

from app.core.config import settings
from app.core.logger import get_logger
from app.models.chat import Lead, CollectedInfo, Message, MessageRole

# Define the required scopes
SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]

# Get logger
logger = get_logger("sheets_service")


class GoogleSheetsService:
    """Service for interacting with Google Sheets."""
    
    def __init__(self):
        """Initialize the Google Sheets service with credentials from settings."""
        try:
            # Check if we're in a testing environment
            if os.getenv("TESTING", "False").lower() in ("true", "1", "t"):
                logger.info("Running in test mode with mock Google Sheets service")
                self._setup_mock_service()
            else:
                # Load credentials from the file specified in settings
                self.credentials = Credentials.from_service_account_file(
                    settings.google_sheets.credentials_file, 
                    scopes=SCOPES
                )
                
                # Create a client
                self.client = gspread.authorize(self.credentials)
                
                # Try to open the spreadsheet to validate credentials
                self.spreadsheet = self.client.open_by_key(
                    settings.google_sheets.spreadsheet_id
                )
                
                # Get the leads worksheet (first sheet by default)
                self.leads_worksheet = self.spreadsheet.get_worksheet(0)
                
                # If the worksheet doesn't exist or is empty, set up the headers
                if not self.leads_worksheet or not self.leads_worksheet.get_all_values():
                    self._setup_worksheet()
                
                logger.info("Google Sheets service initialized successfully")
        
        except Exception as e:
            logger.error(f"Error initializing Google Sheets service: {str(e)}")
            # For testing purposes, set up mock service if initialization fails
            self._setup_mock_service()
    
    def _setup_worksheet(self):
        """Set up the worksheet with headers if it doesn't exist."""
        try:
            # If the worksheet doesn't exist, create it
            if not self.leads_worksheet:
                self.leads_worksheet = self.spreadsheet.add_worksheet(
                    title="Leads", 
                    rows=1000, 
                    cols=10
                )
            
            # Set up headers
            headers = [
                "ID",
                "Timestamp",
                "Client Name",
                "Contact Info",
                "Project Type",
                "Requirements Summary",
                "Timeline",
                "Budget Range",
                "Follow-up Status",
                "Conversation Summary"
            ]
            
            self.leads_worksheet.update_cell(1, 1, headers[0])
            self.leads_worksheet.update_cell(1, 2, headers[1])
            self.leads_worksheet.update_cell(1, 3, headers[2])
            self.leads_worksheet.update_cell(1, 4, headers[3])
            self.leads_worksheet.update_cell(1, 5, headers[4])
            self.leads_worksheet.update_cell(1, 6, headers[5])
            self.leads_worksheet.update_cell(1, 7, headers[6])
            self.leads_worksheet.update_cell(1, 8, headers[7])
            self.leads_worksheet.update_cell(1, 9, headers[8])
            self.leads_worksheet.update_cell(1, 10, headers[9])
            
            logger.info("Worksheet set up with headers")
        
        except Exception as e:
            logger.error(f"Error setting up worksheet: {str(e)}")
            raise
    
    def _setup_mock_service(self):
        """Set up a mock service for testing."""
        logger.info("Setting up mock Google Sheets service")
        
        # Create some mock leads for testing
        # Create a mock lead
        mock_lead = Lead(
            id="mock-lead-123",
            client_name="John Doe",
            contact_info="john.doe@example.com",
            project_type="Mobile App",
            requirements_summary="A mobile app with payment integration and user authentication",
            timeline="3 months",
            budget_range="$10,000-$20,000",
            follow_up_status="pending",
            created_at=datetime.utcnow() - timedelta(days=1),
            conversation_history=[
                Message(
                    role=MessageRole.USER,
                    content="I need a mobile app for my business",
                    timestamp=datetime.utcnow() - timedelta(days=1, hours=1)
                ),
                Message(
                    role=MessageRole.ASSISTANT,
                    content="That sounds interesting! Could you describe the key features you need?",
                    timestamp=datetime.utcnow() - timedelta(days=1, minutes=59)
                )
            ]
        )
        
        self.mock_leads = [mock_lead]
        self.mock_total_leads = len(self.mock_leads)
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    async def store_lead(self, lead: Lead, conversation_summary: str) -> str:
        """
        Store lead information in Google Sheets.
        
        Args:
            lead: Lead information to store
            conversation_summary: Summary of the conversation
            
        Returns:
            ID of the stored lead
        """
        try:
            logger.debug(f"Storing lead: {lead.id}")
            
            # Check if we're using the mock service
            if hasattr(self, 'mock_leads'):
                # For testing, just add the lead to our mock leads list
                self.mock_leads.append(lead)
                self.mock_total_leads = len(self.mock_leads)
                logger.info(f"Mock lead stored successfully: {lead.id}")
                return lead.id
            
            # Prepare the row data
            row_data = [
                lead.id,
                lead.created_at.isoformat(),
                lead.client_name or "",
                lead.contact_info or "",
                lead.project_type or "",
                lead.requirements_summary or "",
                lead.timeline or "",
                lead.budget_range or "",
                lead.follow_up_status,
                conversation_summary
            ]
            
            # Append the row to the worksheet
            self.leads_worksheet.append_row(row_data)
            
            logger.info(f"Lead stored successfully: {lead.id}")
            return lead.id
        
        except Exception as e:
            logger.error(f"Error storing lead: {str(e)}")
            raise
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    async def get_leads(
        self, 
        limit: int = 10, 
        offset: int = 0
    ) -> Dict[str, Any]:
        """
        Get a list of leads with pagination.
        
        Args:
            limit: Maximum number of leads to return
            offset: Number of leads to skip
            
        Returns:
            Dictionary with leads and pagination information
        """
        try:
            # Check if we're using the mock service
            if hasattr(self, 'mock_leads'):
                mock_leads = self.mock_leads[offset:offset+limit]
                return {
                    "leads": mock_leads,
                    "total": self.mock_total_leads,
                    "limit": limit,
                    "offset": offset
                }
                
            logger.debug(f"Getting leads (limit={limit}, offset={offset})")
            
            # Get all values from the worksheet
            all_values = self.leads_worksheet.get_all_values()
            
            # Skip the header row
            rows = all_values[1:]
            
            # Calculate total
            total = len(rows)
            
            # Apply pagination
            paginated_rows = rows[offset:offset+limit]
            
            # Convert rows to Lead objects
            leads = []
            for row in paginated_rows:
                if len(row) >= 9:  # Ensure the row has enough columns
                    lead = Lead(
                        id=row[0],
                        created_at=datetime.fromisoformat(row[1]) if row[1] else datetime.utcnow(),
                        client_name=row[2] if row[2] else None,
                        contact_info=row[3] if row[3] else None,
                        project_type=row[4] if row[4] else None,
                        requirements_summary=row[5] if row[5] else None,
                        timeline=row[6] if row[6] else None,
                        budget_range=row[7] if row[7] else None,
                        follow_up_status=row[8]
                    )
                    leads.append(lead)
            
            logger.debug(f"Retrieved {len(leads)} leads")
            
            return {
                "total": total,
                "limit": limit,
                "offset": offset,
                "leads": leads
            }
        
        except Exception as e:
            logger.error(f"Error getting leads: {str(e)}")
            # Return empty results for testing
            return {
                "leads": [],
                "total": 0,
                "limit": limit,
                "offset": offset
            }
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    async def get_lead_by_id(self, lead_id: str) -> Optional[Lead]:
        """
        Get a specific lead by ID.
        
        Args:
            lead_id: ID of the lead to retrieve
            
        Returns:
            Lead object if found, None otherwise
        """
        try:
            logger.debug(f"Getting lead by ID: {lead_id}")
            
            # Check if we're using the mock service
            if hasattr(self, 'mock_leads'):
                # Find the lead in mock data
                for lead in self.mock_leads:
                    if lead.id == lead_id:
                        logger.debug(f"Retrieved mock lead: {lead_id}")
                        return lead
                logger.warning(f"Mock lead not found: {lead_id}")
                return None
            
            # Find the row with the matching ID
            cell = self.leads_worksheet.find(lead_id)
            if not cell:
                logger.warning(f"Lead not found: {lead_id}")
                return None
            
            # Get the row values
            row = self.leads_worksheet.row_values(cell.row)
            
            # Ensure the row has enough columns
            if len(row) >= 9:
                lead = Lead(
                    id=row[0],
                    created_at=datetime.fromisoformat(row[1]) if row[1] else datetime.utcnow(),
                    client_name=row[2] if row[2] else None,
                    contact_info=row[3] if row[3] else None,
                    project_type=row[4] if row[4] else None,
                    requirements_summary=row[5] if row[5] else None,
                    timeline=row[6] if row[6] else None,
                    budget_range=row[7] if row[7] else None,
                    follow_up_status=row[8]
                )
                
                logger.debug(f"Retrieved lead: {lead_id}")
                return lead
            
            logger.warning(f"Lead row has insufficient data: {lead_id}")
            return None
        
        except Exception as e:
            logger.error(f"Error getting lead by ID: {str(e)}")
            raise
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    async def update_lead_status(self, lead_id: str, status: str) -> bool:
        """
        Update the follow-up status of a lead.
        
        Args:
            lead_id: ID of the lead to update
            status: New status value
            
        Returns:
            True if successful, False otherwise
        """
        try:
            logger.debug(f"Updating lead status: {lead_id} -> {status}")
            
            # Check if we're using the mock service
            if hasattr(self, 'mock_leads'):
                # Find the lead in mock data
                for lead in self.mock_leads:
                    if lead.id == lead_id:
                        lead.follow_up_status = status
                        logger.info(f"Mock lead status updated: {lead_id} -> {status}")
                        return True
                logger.warning(f"Mock lead not found for status update: {lead_id}")
                return False
            
            # Find the row with the matching ID
            cell = self.leads_worksheet.find(lead_id)
            if not cell:
                logger.warning(f"Lead not found for status update: {lead_id}")
                return False
            
            # Update the status cell (column 9)
            self.leads_worksheet.update_cell(cell.row, 9, status)
            
            logger.info(f"Lead status updated: {lead_id} -> {status}")
            return True
        
        except Exception as e:
            logger.error(f"Error updating lead status: {str(e)}")
            raise


# Create a singleton instance
sheets_service = GoogleSheetsService() 