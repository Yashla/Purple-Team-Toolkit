"""Sync after manual version fix

Revision ID: 37b4662d9e31
Revises: 10b0e490b160
Create Date: 2024-04-22 16:20:43.844577

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '37b4662d9e31'
down_revision = '10b0e490b160'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('cves',
    sa.Column('cve_id', sa.String(length=64), nullable=False),
    sa.Column('summary', sa.Text(), nullable=True),
    sa.Column('cvss_v3_score', sa.Text(), nullable=True),
    sa.Column('cvss_v3_label', sa.Text(), nullable=True),
    sa.PrimaryKeyConstraint('cve_id')
    )
    op.create_table('devices',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('ip_address', sa.String(length=15), nullable=False),
    sa.Column('device_type', sa.String(length=255), nullable=False),
    sa.Column('username', sa.String(length=255), nullable=False),
    sa.Column('password', sa.String(length=255), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('snmp_outputs',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('filename', sa.String(length=255), nullable=False),
    sa.Column('data', sa.LargeBinary(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('ssdp_outputs',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('file_name', sa.String(length=255), nullable=False),
    sa.Column('output_blob', sa.LargeBinary(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('device_cves',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('device_id', sa.Integer(), nullable=True),
    sa.Column('cve_id', sa.String(length=64), nullable=True),
    sa.ForeignKeyConstraint(['cve_id'], ['cves.cve_id'], ),
    sa.ForeignKeyConstraint(['device_id'], ['devices.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('devices_information',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('device_id', sa.Integer(), nullable=True),
    sa.Column('ip_address', sa.String(length=255), nullable=False),
    sa.Column('device_type', sa.Text(), nullable=False),
    sa.Column('Vendor', sa.String(length=255), nullable=False),
    sa.Column('Product', sa.String(length=255), nullable=False),
    sa.Column('Version', sa.String(length=255), nullable=False),
    sa.ForeignKeyConstraint(['device_id'], ['devices.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('device_id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('devices_information')
    op.drop_table('device_cves')
    op.drop_table('ssdp_outputs')
    op.drop_table('snmp_outputs')
    op.drop_table('devices')
    op.drop_table('cves')
    # ### end Alembic commands ###
