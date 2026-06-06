import time

# In-memory activity feed store
ACTIVITY_FEED = []


def publish_admin_event(event_type: str, user: str, details: dict | str):
    """
    Append an admin event to the activity feed.
    """
    ACTIVITY_FEED.append({
        "timestamp": time.time(),
        "event": event_type,
        "user": user,
        "details": details,
    })

    # Keep only last 500 events
    if len(ACTIVITY_FEED) > 500:
        ACTIVITY_FEED.pop(0)
