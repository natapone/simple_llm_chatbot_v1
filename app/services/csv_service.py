#!/usr/bin/env python3
"""
CSV Service for storing lead data in a local CSV file.
This replaces the Google Sheets integration with a simpler local storage solution.
"""

import csv
import os
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any

from app.core.logger import get_logger
from app.models.chat import Lead
from app.core.config import get_settings

# Set up logger
logger = get_logger(__name__)

class CSVService:
    """Service for storing lead data in a local CSV file."""

    def __init__(self):
        """Initialize the CSV service."""
        # Get settings
        settings = get_settings()
        
        # Ensure the data directory exists
        self.data_dir = Path(settings.csv.data_directory)
        self.data_dir.mkdir(exist_ok=True)
        
        # Path to the leads CSV file
        self.leads_file = self.data_dir / settings.csv.leads_file
        
        # Create the CSV file with headers if it doesn't exist
        if not self.leads_file.exists():
            self._create_csv_file()
            
        logger.info(f"CSV Service initialized. Leads file: {self.leads_file}")

    def _create_csv_file(self):
        """Create the CSV file with headers."""
        headers = [
            "id", 
            "client_name", 
            "contact_info", 
            "project_type", 
            "requirements_summary", 
            "use_case",
            "timeline", 
            "budget_range", 
            "follow_up_status", 
            "created_at",
            "summary"
        ]
        
        with open(self.leads_file, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(headers)
            
        logger.info(f"Created new leads CSV file at {self.leads_file}")

    async def store_lead(self, lead: Lead, conversation_summary: str) -> str:
        """Store a lead in the CSV file.
        
        Args:
            lead: The lead to store
            conversation_summary: A summary of the conversation
            
        Returns:
            The ID of the stored lead
        """
        try:
            # Prepare the row data
            row_data = [
                lead.id,
                lead.client_name or "",
                lead.contact_info or "",
                lead.project_type or "",
                lead.requirements_summary or "",
                getattr(lead, "use_case", "") or "",
                lead.timeline or "",
                lead.budget_range or "",
                lead.follow_up_status,
                lead.created_at.isoformat(),
                conversation_summary
            ]
            
            # Append the row to the CSV file
            with open(self.leads_file, 'a', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(row_data)
                
            # Print the lead information to the console
            print("\n=== New Lead Collected ===")
            print(f"ID: {lead.id}")
            print(f"Client Name: {lead.client_name}")
            print(f"Contact Info: {lead.contact_info}")
            print(f"Project Type: {lead.project_type}")
            print(f"Requirements: {lead.requirements_summary}")
            print(f"Use Case: {getattr(lead, 'use_case', '')}")
            print(f"Timeline: {lead.timeline}")
            print(f"Budget Range: {lead.budget_range}")
            print(f"Created At: {lead.created_at}")
            print(f"Summary: {conversation_summary}")
            print("==========================\n")
            
            logger.info(f"Stored lead {lead.id} in CSV file")
            return lead.id
            
        except Exception as e:
            logger.error(f"Error storing lead in CSV file: {str(e)}")
            raise

    async def get_leads(self, limit: int = 10, offset: int = 0) -> Dict[str, Any]:
        """Get a list of leads from the CSV file.
        
        Args:
            limit: Maximum number of leads to return
            offset: Number of leads to skip
            
        Returns:
            Dictionary containing leads and pagination info
        """
        try:
            leads = []
            
            # Read all leads from the CSV file
            with open(self.leads_file, 'r', newline='') as csvfile:
                reader = csv.DictReader(csvfile)
                all_leads = list(reader)
                
            # Apply pagination
            paginated_leads = all_leads[offset:offset+limit]
            
            # Convert to Lead objects
            for row in paginated_leads:
                lead = Lead(
                    id=row["id"],
                    client_name=row["client_name"],
                    contact_info=row["contact_info"],
                    project_type=row["project_type"],
                    requirements_summary=row["requirements_summary"],
                    timeline=row["timeline"],
                    budget_range=row["budget_range"],
                    follow_up_status=row["follow_up_status"],
                    created_at=datetime.fromisoformat(row["created_at"])
                )
                leads.append(lead)
                
            return {
                "total": len(all_leads),
                "limit": limit,
                "offset": offset,
                "leads": leads
            }
            
        except FileNotFoundError:
            logger.warning(f"Leads file not found at {self.leads_file}")
            return {
                "total": 0,
                "limit": limit,
                "offset": offset,
                "leads": []
            }
        except Exception as e:
            logger.error(f"Error getting leads from CSV file: {str(e)}")
            raise

    async def get_lead_by_id(self, lead_id: str) -> Optional[Lead]:
        """Get a lead by ID from the CSV file.
        
        Args:
            lead_id: The ID of the lead to get
            
        Returns:
            The lead if found, None otherwise
        """
        try:
            # Read all leads from the CSV file
            with open(self.leads_file, 'r', newline='') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    if row["id"] == lead_id:
                        return Lead(
                            id=row["id"],
                            client_name=row["client_name"],
                            contact_info=row["contact_info"],
                            project_type=row["project_type"],
                            requirements_summary=row["requirements_summary"],
                            timeline=row["timeline"],
                            budget_range=row["budget_range"],
                            follow_up_status=row["follow_up_status"],
                            created_at=datetime.fromisoformat(row["created_at"])
                        )
                        
            return None
            
        except FileNotFoundError:
            logger.warning(f"Leads file not found at {self.leads_file}")
            return None
        except Exception as e:
            logger.error(f"Error getting lead from CSV file: {str(e)}")
            raise

    async def update_lead_status(self, lead_id: str, status: str) -> bool:
        """Update the status of a lead in the CSV file.
        
        Args:
            lead_id: The ID of the lead to update
            status: The new status
            
        Returns:
            True if the lead was updated, False otherwise
        """
        try:
            # Read all leads from the CSV file
            with open(self.leads_file, 'r', newline='') as csvfile:
                reader = csv.DictReader(csvfile)
                headers = reader.fieldnames
                rows = list(reader)
                
            # Find and update the lead
            lead_updated = False
            for row in rows:
                if row["id"] == lead_id:
                    row["follow_up_status"] = status
                    lead_updated = True
                    break
                    
            if not lead_updated:
                return False
                
            # Write the updated leads back to the CSV file
            with open(self.leads_file, 'w', newline='') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=headers)
                writer.writeheader()
                writer.writerows(rows)
                
            logger.info(f"Updated lead {lead_id} status to {status}")
            return True
            
        except FileNotFoundError:
            logger.warning(f"Leads file not found at {self.leads_file}")
            return False
        except Exception as e:
            logger.error(f"Error updating lead status in CSV file: {str(e)}")
            raise

# Create an instance of the CSVService class
csv_service = CSVService() 