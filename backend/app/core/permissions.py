from fastapi import HTTPException, status

ROLE_PERMISSIONS = {
    "owner": {
        "organization_manage",
        "dataset_create",
        "dataset_manage",
        "analysis_run",
        "analysis_view",
    },
    "admin": {
        "organization_manage",
        "dataset_create",
        "dataset_manage",
        "analysis_run",
        "analysis_view",
    },
    "analyst": {
        "dataset_create",
        "analysis_run",
        "analysis_view",
    },
    "viewer": {
        "analysis_view",
    },
}


def require_permission(role: str, permission: str) -> None:
    allowed_permissions = ROLE_PERMISSIONS.get(role, set())

    if permission not in allowed_permissions:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to perform this action.",
        )
def require_role(membership, allowed_roles: set[str]) -> None:
    if membership.role not in allowed_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to perform this action.",
        )