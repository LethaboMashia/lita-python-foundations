"""policy.py - the single place that decides who may do what.

Deny by default: an action is allowed only if a rule below says so explicitly.
Unknown user, unknown role, unknown action, missing resource -> False.
"""
from typing import Any

# role -> the actions that role may perform at all
ROLE_PERMISSIONS: dict[str, set[str]] = {
    "patient": {"record:read", "profile:update"},
    "doctor": {"record:read", "record:write", "profile:update"},
    "admin": {"user:list", "user:set_role", "profile:update"},
}

# actions that ALSO need a relationship to the specific resource
OWNERSHIP_ACTIONS = {"record:read", "record:write"}


def _is_related(user: dict[str, Any], resource: dict[str, Any] | None) -> bool:
    """Is this user the patient, or the treating doctor, on this record?"""
    if not resource:
        return False
    if user.get("role") == "patient":
        return resource.get("patient_id") == user.get("id")
    if user.get("role") == "doctor":
        return resource.get("doctor_id") == user.get("id")
    return False


def can(user: dict[str, Any] | None, action: str,
        resource: dict[str, Any] | None = None) -> bool:
    """May `user` perform `action` (on `resource`)? False unless a rule says yes."""
    if not user:
        return False
    if action not in ROLE_PERMISSIONS.get(user.get("role", ""), set()):
        return False
    if action in OWNERSHIP_ACTIONS:
        return _is_related(user, resource)
    return True