from datetime import datetime, timezone

def get_current_time():
    return datetime.now(timezone.utc)

def get_current_timestamp():
    return int(get_current_time().timestamp())