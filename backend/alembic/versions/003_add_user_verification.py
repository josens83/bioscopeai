"""add user verification and reset fields

Revision ID: 003
Revises: 002
Create Date: 2024-01-16

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '003'
down_revision = '002'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Users 테이블에 새 컬럼 추가
    op.add_column('users', sa.Column('is_verified', sa.Boolean(), nullable=True, server_default='false'))
    op.add_column('users', sa.Column('reset_token', sa.String(), nullable=True))
    op.add_column('users', sa.Column('reset_token_expires_at', sa.DateTime(timezone=True), nullable=True))
    op.add_column('users', sa.Column('verification_token', sa.String(), nullable=True))
    op.add_column('users', sa.Column('verified_at', sa.DateTime(timezone=True), nullable=True))

    # 인덱스 추가
    op.create_index('ix_users_is_verified', 'users', ['is_verified'])
    op.create_index('ix_users_is_superuser', 'users', ['is_superuser'])
    op.create_index('ix_users_reset_token', 'users', ['reset_token'])
    op.create_index('ix_users_verification_token', 'users', ['verification_token'])


def downgrade() -> None:
    # 인덱스 삭제
    op.drop_index('ix_users_verification_token', table_name='users')
    op.drop_index('ix_users_reset_token', table_name='users')
    op.drop_index('ix_users_is_superuser', table_name='users')
    op.drop_index('ix_users_is_verified', table_name='users')

    # 컬럼 삭제
    op.drop_column('users', 'verified_at')
    op.drop_column('users', 'verification_token')
    op.drop_column('users', 'reset_token_expires_at')
    op.drop_column('users', 'reset_token')
    op.drop_column('users', 'is_verified')
