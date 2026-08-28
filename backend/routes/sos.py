from fastapi import APIRouter, HTTPException

from ..database.mongodb import db_manager
from ..models.schemas import CitizenRegisterRequest, SOSBroadcastRequest
from ..services.notification_service import dispatch_phone_sos

router = APIRouter()


@router.post("/sos/register")
async def register_citizen(citizen: CitizenRegisterRequest):
    try:
        doc = citizen.model_dump()
        db_manager.citizens.update_one(
            {"phone": citizen.phone, "location": citizen.location},
            {"$set": doc},
            upsert=True,
        )
        return {
            "status": "SUCCESS",
            "message": f"Registered {citizen.name} for {citizen.location} alerts.",
        }
    except Exception as exc:
        raise HTTPException(status_code=503, detail="Could not save citizen registration.") from exc


@router.post("/sos/dispatch")
async def dispatch_sos_alert(req: SOSBroadcastRequest):
    all_citizens = list(db_manager.citizens.find())
    matching_citizens = [
        c for c in all_citizens
        if req.location.lower() in c.get("location", "").lower()
    ]

    # Prototype behavior: no fake citizen and no fake phone number.
    result = dispatch_phone_sos(
        req.location, matching_citizens, req.custom_message
    )
    return result
