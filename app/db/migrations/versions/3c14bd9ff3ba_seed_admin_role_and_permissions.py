"""seed admin role and permissions

Revision ID: 3c14bd9ff3ba
Revises: 20d638d5b826
Create Date: 2026-03-12 16:08:46.764392

"""
from alembic import op
import sqlalchemy as sa
from ....utils import PermissionName



# revision identifiers, used by Alembic.
revision = '3c14bd9ff3ba'
down_revision = '20d638d5b826'
branch_labels = None
depends_on = None


# Add new permissions here as the app grows.
PERMISSIONS = [
    {'name': PermissionName.REMOVE_USER,  'description': 'Allows removing a user from the system'},
    {'name': PermissionName.GET_USERS,    'description': 'Allows listing all users'},
    {'name': PermissionName.ASSIGN_ROLES, 'description': 'Allows assigning roles to users'},
    {'name': PermissionName.CREATE_ROLES, 'description': 'Allows creating new roles'},
    {'name': PermissionName.REMOVE_USER_ROLE, 'description': 'Allows removing a role from a user'},
    {'name': PermissionName.GET_ROLES, 'description': 'Allows viewing all roles'},
]

ADMIN_ROLE = {'name': 'ADMIN', 'description': 'Full access — owns all permissions'}


def upgrade() -> None:
    conn = op.get_bind()

    # Insert all permissions
    for p in PERMISSIONS:
        conn.execute(
            sa.text("INSERT INTO permission (name, description, disabled) VALUES (:name, :description, false)"),
            p,
        )

    # Insert the Admin role
    conn.execute(
        sa.text("INSERT INTO role (name, description, disabled) VALUES (:name, :description, false)"),
        ADMIN_ROLE,
    )

    # Retrieve the Admin role id and all permission ids to build the relations
    admin_role = conn.execute(
        sa.text("SELECT id FROM role WHERE name = :name"),
        {'name': ADMIN_ROLE['name']},
    ).fetchone()

    permission_ids = conn.execute(
        sa.text("SELECT id FROM permission WHERE name = ANY(:names)"),
        {'names': [p['name'] for p in PERMISSIONS]},
    ).fetchall()

    # Link every permission to the Admin role
    for row in permission_ids:
        conn.execute(
            sa.text("INSERT INTO permission_roles (role_id, permission_id) VALUES (:role_id, :permission_id)"),
            {'role_id': admin_role.id, 'permission_id': row.id},
        )


def downgrade() -> None:
    conn = op.get_bind()

    # Remove permission_role entries for Admin
    admin_role = conn.execute(
        sa.text("SELECT id FROM role WHERE name = :name"),
        {'name': ADMIN_ROLE['name']},
    ).fetchone()

    if admin_role:
        conn.execute(
            sa.text("DELETE FROM permission_roles WHERE role_id = :role_id"),
            {'role_id': admin_role.id},
        )

    # Remove the Admin role
    conn.execute(
        sa.text("DELETE FROM role WHERE name = :name"),
        {'name': ADMIN_ROLE['name']},
    )

    # Remove the seeded permissions
    conn.execute(
        sa.text("DELETE FROM permission WHERE name = ANY(:names)"),
        {'names': [p['name'] for p in PERMISSIONS]},
    )

