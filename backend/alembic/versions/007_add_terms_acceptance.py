"""add terms acceptance tables

Revision ID: 007
Revises: 006
Create Date: 2024-01-15

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '007'
down_revision = '006'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 약관 동의 기록 테이블 생성
    op.create_table(
        'terms_acceptances',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('terms_type', sa.String(), nullable=False),
        sa.Column('version', sa.String(), nullable=False),
        sa.Column('accepted', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('accepted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('ip_address', sa.String(), nullable=True),
        sa.Column('user_agent', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    )

    # 인덱스 생성
    op.create_index('ix_terms_acceptances_id', 'terms_acceptances', ['id'])
    op.create_index('ix_terms_acceptances_user_id', 'terms_acceptances', ['user_id'])
    op.create_index('ix_terms_acceptances_terms_type', 'terms_acceptances', ['terms_type'])

    # 약관 버전 테이블 생성
    op.create_table(
        'terms_versions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('terms_type', sa.String(), nullable=False),
        sa.Column('version', sa.String(), nullable=False),
        sa.Column('language', sa.String(), nullable=False, server_default='ko'),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('is_required', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('effective_date', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_by', sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['updated_by'], ['users.id']),
    )

    # 인덱스 생성
    op.create_index('ix_terms_versions_id', 'terms_versions', ['id'])
    op.create_index('ix_terms_versions_terms_type', 'terms_versions', ['terms_type'])

    # 기본 약관 버전 삽입 (예시)
    op.execute("""
        INSERT INTO terms_versions (terms_type, version, language, title, content, is_active, is_required, effective_date)
        VALUES
        ('terms_of_service', '1.0.0', 'ko', 'BioscopeAI 이용약관', '# BioscopeAI 이용약관\\n\\n제1조 (목적)...', true, true, NOW()),
        ('privacy_policy', '1.0.0', 'ko', 'BioscopeAI 개인정보 처리방침', '# 개인정보 처리방침\\n\\n제1조 (개인정보의 처리목적)...', true, true, NOW()),
        ('marketing', '1.0.0', 'ko', '마케팅 정보 수신 동의', '# 마케팅 정보 수신 동의\\n\\n선택사항입니다.', true, false, NOW());
    """)


def downgrade() -> None:
    op.drop_index('ix_terms_versions_terms_type', table_name='terms_versions')
    op.drop_index('ix_terms_versions_id', table_name='terms_versions')
    op.drop_table('terms_versions')

    op.drop_index('ix_terms_acceptances_terms_type', table_name='terms_acceptances')
    op.drop_index('ix_terms_acceptances_user_id', table_name='terms_acceptances')
    op.drop_index('ix_terms_acceptances_id', table_name='terms_acceptances')
    op.drop_table('terms_acceptances')
