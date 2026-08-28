import logging
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


def dispatch_phone_sos(location: str, citizens: list, custom_msg: str = None) -> dict:
    """
    SIH prototype notification simulator.

    This does NOT send real SMS/phone calls. It creates a dispatch log that
    can later be replaced with an SMS/voice provider such as Twilio.
    """
    timestamp = datetime.now(timezone.utc).isoformat()
    msg = custom_msg or (
        f"EMERGENCY LANDSLIDE ALERT: Landslide risk detected near {location}. "
        "Stay away from vulnerable slopes and follow local safety advisories."
    )

    recipients_log = [
        {
            "name": citizen.get("name", "Resident"),
            "phone": citizen.get("phone", ""),
            "location": citizen.get("location", location),
            "status": "SIMULATED",
            "message": msg,
            "timestamp": timestamp,
        }
        for citizen in citizens
    ]

    logger.info(
        "Simulated SOS broadcast to %d registered citizens in %s.",
        len(recipients_log),
        location,
    )

    return {
        "status": "SIMULATED",
        "location": location,
        "dispatched_count": len(recipients_log),
        "message": msg,
        "timestamp": timestamp,
        "logs": recipients_log,
        "note": "No real SMS/phone call was sent; this is a prototype simulator.",
    }
