"""
Simple Tracking Number Generator for Shipments

Generates easy-to-read tracking numbers with carrier prefix and sequential numbering.

Format: {CARRIER}-{YYYYMMDD}-{SEQUENCE}
Examples:
  - DHL-20240512-00001
  - FEDEX-20240512-00002
  - UPS-20240512-00003
  - ARAMEX-20240512-00001
"""

import asyncpg
import logging
from datetime import datetime
from typing import Optional

logger = logging.getLogger(__name__)


async def generate_tracking_number(
    conn: asyncpg.Connection,
    carrier: Optional[str] = None,
    shipment_date: Optional[datetime] = None
) -> str:
    """
    Generate a simple, unique tracking number.
    
    Format: {CARRIER}-{YYYYMMDD}-{SEQUENCE}
    
    Args:
        conn: Database connection
        carrier: Carrier name (DHL, FedEx, UPS, Aramex)
        shipment_date: Date of shipment (defaults to today)
        
    Returns:
        Tracking number like "DHL-20240512-00001"
        
    How it works:
        1. Takes carrier name (or uses "SHIP" if no carrier)
        2. Adds today's date in YYYYMMDD format
        3. Counts existing shipments today and adds 1
        4. Combines them with dashes
    """

    if shipment_date is None:
        shipment_date = datetime.now()
    date_str = shipment_date.strftime("%Y%m%d")
    carrier_prefix = (carrier or "SHIP").upper().replace(" ", "")
    
    # Count how many shipments exist for this carrier today
    try:
        count = await conn.fetchval(
            """
            SELECT COUNT(*) 
            FROM shipments 
            WHERE carrier_name = $1 
              AND DATE(shipment_date) = $2
              AND deleted = FALSE
            """,
            carrier,
            shipment_date.date()
        )
        sequence = (count or 0) + 1
    except Exception as e:
        logger.error(f"Error counting shipments: {e}")
        # Fallback: use current time as sequence
        sequence = int(datetime.now().strftime("%H%M%S"))
    
    # Build tracking number: CARRIER-YYYYMMDD-XXXXX
    tracking_number = f"{carrier_prefix}-{date_str}-{sequence:05d}"
    
    logger.info(f"Generated tracking number: {tracking_number}")
    
    return tracking_number
