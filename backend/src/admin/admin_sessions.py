import time
import uuid

# In-memory admin session store
ADMIN_SESSIONS = {}

def create_session(user: str):
    """
    Create a new admin session and return its session_id.
    """
    session_id = str(uuid.uuid4())
    ADMIN_SESSIONS[session_id] = {
        "session_id": session_id,
        "user": user,
        "start_time": time.time(),
        "last_activity": time.time(),
    }
    return session_id


def touch_session(session_id: str):
    """
    Update last_activity timestamp for a session.
    """
    if session_id in ADMIN_SESSIONS:
        ADMIN_SESSIONS[session_id]["last_activity"] = time.time()


def delete_session(session_id: str):
    """
    Delete a specific admin session.
    """
    if session_id in ADMIN_SESSIONS:
        del ADMIN_SESSIONS[session_id]


def session_exists(session_id: str) -> bool:
    """
    Check if a session exists.
    """
    return session_id in ADMIN_SESSIONS
