from alembic import op
import sqlalchemy as sa

revision = '0001_create_train_records'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    op.create_table(
        'train_records',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('train_number', sa.String(50), index=True),
        sa.Column('departure_station', sa.String(100), index=True),
        sa.Column('arrival_station', sa.String(100), index=True),
        sa.Column('scheduled_time', sa.DateTime()),
        sa.Column('actual_time', sa.DateTime()),
        sa.Column('delay', sa.Float()),
        sa.Column('status', sa.String(20)),
        sa.Column('source', sa.String(20), server_default='irail'),
        sa.Column('created_at', sa.DateTime()),
    )

def downgrade():
    op.drop_table('train_records')
