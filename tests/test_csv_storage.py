#!/usr/bin/env python3
"""
Test script for CSV storage.
This script tests the ability to store a lead in a local CSV file.
"""

import asyncio
import uuid
from datetime import datetime

from app.core.config import get_settings
from app.core.logger import setup_logging
from app.models.chat import Lead
from app.services.csv_service import CSVService

# Set up logging
setup_logging()

async def test_store_lead():
    """Test storing a lead in a CSV file."""
    print("\n=== CSV Storage Test ===")
    
    # Create a test lead
    lead_id = str(uuid.uuid4())
    lead = Lead(
        id=lead_id,
        client_name="Test Client",
        contact_info="test@example.com",
        project_type="Website",
        requirements_summary="Responsive design, contact form, about page",
        timeline="2 months",
        budget_range="$5,000 - $10,000",
        follow_up_status="pending",
        created_at=datetime.utcnow()
    )
    
    # Create a test summary
    summary = "Client needs a responsive website with a contact form and about page. Budget is $5,000 - $10,000 and timeline is 2 months."
    
    # Initialize the CSV service
    csv_service = CSVService()
    
    # Store the lead
    print("Storing lead in CSV file...")
    stored_id = await csv_service.store_lead(lead, summary)
    
    # Verify the lead was stored
    print(f"Lead stored with ID: {stored_id}")
    
    # Retrieve the lead
    print("Retrieving lead from CSV file...")
    retrieved_lead = await csv_service.get_lead_by_id(lead_id)
    
    if retrieved_lead:
        print("Lead retrieved successfully!")
        print(f"Client Name: {retrieved_lead.client_name}")
        print(f"Contact Info: {retrieved_lead.contact_info}")
        print(f"Project Type: {retrieved_lead.project_type}")
        print(f"Requirements: {retrieved_lead.requirements_summary}")
        print(f"Timeline: {retrieved_lead.timeline}")
        print(f"Budget Range: {retrieved_lead.budget_range}")
        return True
    else:
        print("Failed to retrieve lead!")
        return False

async def main():
    """Main function."""
    # Test storing a lead
    success = await test_store_lead()
    
    if success:
        print("\n✅ CSV storage test passed!")
    else:
        print("\n❌ CSV storage test failed!")

if __name__ == "__main__":
    asyncio.run(main()) 