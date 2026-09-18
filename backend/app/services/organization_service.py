from sqlalchemy.orm import Session

from app.models.organization import Organization
from app.models.organization_membership import OrganizationMembership


def create_organization(
    db: Session,
    name: str,
    slug: str,
    user_id,
) -> Organization:
    """
    Create a new organization and automatically make
    the creating user its owner.
    """

    existing_organization = (
        db.query(Organization)
        .filter(Organization.slug == slug)
        .first()
    )

    if existing_organization:
        raise ValueError("Organization slug already exists")

    try:
        organization = Organization(
            name=name,
            slug=slug,
        )

        db.add(organization)

        # Generate organization.id before creating membership
        db.flush()

        membership = OrganizationMembership(
            organization_id=organization.id,
            user_id=user_id,
            role="owner",
        )

        db.add(membership)

        # Commit organization + membership together
        db.commit()

        db.refresh(organization)

        return organization

    except Exception:
        # Roll back the entire transaction if anything fails
        db.rollback()
        raise


def get_user_organizations(
    db: Session,
    user_id,
) -> list[Organization]:
    """
    Return all organizations where the user has membership.
    """

    organizations = (
        db.query(Organization)
        .join(
            OrganizationMembership,
            OrganizationMembership.organization_id == Organization.id,
        )
        .filter(
            OrganizationMembership.user_id == user_id,
        )
        .order_by(Organization.id)
        .all()
    )

    return organizations