"""add promotion codes

Revision ID: 008
Revises: 007
Create Date: 2024-01-15

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '008'
down_revision = '007'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 프로모션 코드 테이블 생성
    op.create_table(
        'promotion_codes',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('code', sa.String(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('discount_type', sa.String(), nullable=False),
        sa.Column('discount_value', sa.Float(), nullable=False),
        sa.Column('max_uses', sa.Integer(), nullable=True),
        sa.Column('max_uses_per_user', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('min_purchase_amount', sa.Float(), nullable=True),
        sa.Column('applicable_plans', sa.Text(), nullable=True),
        sa.Column('valid_from', sa.DateTime(timezone=True), nullable=False),
        sa.Column('valid_until', sa.DateTime(timezone=True), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('uses_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('created_by', sa.Integer(), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )

    # 인덱스 생성
    op.create_index('ix_promotion_codes_id', 'promotion_codes', ['id'])
    op.create_index('ix_promotion_codes_code', 'promotion_codes', ['code'], unique=True)

    # 프로모션 코드 사용 기록 테이블 생성
    op.create_table(
        'promotion_code_usages',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('promotion_code_id', sa.Integer(), nullable=False),
        sa.Column('code', sa.String(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('subscription_id', sa.Integer(), nullable=True),
        sa.Column('discount_applied', sa.Float(), nullable=False),
        sa.Column('used_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('ip_address', sa.String(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )

    # 인덱스 생성
    op.create_index('ix_promotion_code_usages_id', 'promotion_code_usages', ['id'])
    op.create_index('ix_promotion_code_usages_promotion_code_id', 'promotion_code_usages', ['promotion_code_id'])
    op.create_index('ix_promotion_code_usages_user_id', 'promotion_code_usages', ['user_id'])

    # 샘플 프로모션 코드 (선택사항)
    op.execute("""
        INSERT INTO promotion_codes (code, description, discount_type, discount_value, max_uses, valid_from, is_active)
        VALUES
        ('WELCOME2024', '신규 가입 환영 20% 할인', 'percentage', 20, NULL, NOW(), true),
        ('EARLY50', '얼리버드 $50 할인', 'fixed', 50, 100, NOW(), true);
    """)


def downgrade() -> None:
    op.drop_index('ix_promotion_code_usages_user_id', table_name='promotion_code_usages')
    op.drop_index('ix_promotion_code_usages_promotion_code_id', table_name='promotion_code_usages')
    op.drop_index('ix_promotion_code_usages_id', table_name='promotion_code_usages')
    op.drop_table('promotion_code_usages')

    op.drop_index('ix_promotion_codes_code', table_name='promotion_codes')
    op.drop_index('ix_promotion_codes_id', table_name='promotion_codes')
    op.drop_table('promotion_codes')
