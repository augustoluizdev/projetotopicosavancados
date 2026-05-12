from django.db import migrations, connection


def create_read_model_table(apps, schema_editor):
    """Cria a tabela de Read Model para Eventos (CQRS - Query Side)"""
    with connection.cursor() as cursor:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS readmodel_event (
                id INTEGER PRIMARY KEY,
                title VARCHAR(255) NOT NULL,
                description TEXT,
                date TIMESTAMP WITH TIME ZONE NOT NULL,
                location VARCHAR(255) NOT NULL,
                address VARCHAR(255),
                max_participants INTEGER NOT NULL,
                sold_tickets INTEGER DEFAULT 0,
                available_tickets INTEGER,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            )
        """)


def reverse_migration(apps, schema_editor):
    """Remove a tabela de Read Model (rollback)"""
    with connection.cursor() as cursor:
        cursor.execute("DROP TABLE IF EXISTS readmodel_event")


class Migration(migrations.Migration):

    dependencies = [
        ('api_rest', '0005_alter_event_max_participants_and_more'),
    ]

    operations = [
        migrations.RunPython(create_read_model_table, reverse_migration),
    ]
