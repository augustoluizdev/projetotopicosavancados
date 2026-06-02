from django.db import connection


class EventReadModel:
    """Read Model desnormalizado para Eventos (CQRS - Query Side)
    Otimizado para leitura rapida no GET /api/events/
    """

    TABLE_NAME = 'readmodel_event'

    @staticmethod
    def create_table():
        """Cria a tabela de read model se nao existir"""
        if connection.vendor == 'sqlite':
            create_table_sql = f"""
                CREATE TABLE IF NOT EXISTS {EventReadModel.TABLE_NAME} (
                    id INTEGER PRIMARY KEY,
                    title VARCHAR(255) NOT NULL,
                    description TEXT,
                    date DATETIME NOT NULL,
                    location VARCHAR(255) NOT NULL,
                    address VARCHAR(255),
                    max_participants INTEGER NOT NULL,
                    sold_tickets INTEGER DEFAULT 0,
                    available_tickets INTEGER,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """
        else:
            create_table_sql = f"""
                CREATE TABLE IF NOT EXISTS {EventReadModel.TABLE_NAME} (
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
            """

        with connection.cursor() as cursor:
            cursor.execute(create_table_sql)

    @staticmethod
    def insert_or_update(event_data):
        """Insere ou atualiza um evento no read model (Idempotente)
        Usa SQL puro para performance
        """
        timestamp_sql = 'CURRENT_TIMESTAMP' if connection.vendor == 'sqlite' else 'NOW()'

        with connection.cursor() as cursor:
            cursor.execute(f"""
                INSERT INTO {EventReadModel.TABLE_NAME}
                (id, title, description, date, location, address, max_participants, sold_tickets, available_tickets, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, {timestamp_sql}, {timestamp_sql})
                ON CONFLICT (id) DO UPDATE SET
                    title = EXCLUDED.title,
                    description = EXCLUDED.description,
                    date = EXCLUDED.date,
                    location = EXCLUDED.location,
                    address = EXCLUDED.address,
                    max_participants = EXCLUDED.max_participants,
                    sold_tickets = EXCLUDED.sold_tickets,
                    available_tickets = EXCLUDED.available_tickets,
                    updated_at = {timestamp_sql}
            """, [
                event_data['id'],
                event_data['title'],
                event_data.get('description', ''),
                event_data['date'],
                event_data['location'],
                event_data.get('address', ''),
                event_data['max_participants'],
                event_data.get('sold_tickets', 0),
                event_data.get('available_tickets')
            ])

    @staticmethod
    def delete(event_id):
        """Remove um evento do read model"""
        with connection.cursor() as cursor:
            cursor.execute(f"DELETE FROM {EventReadModel.TABLE_NAME} WHERE id = %s", [event_id])

    @staticmethod
    def get_all():
        """Retorna todos os eventos do read model (otimizado para listagem)"""
        with connection.cursor() as cursor:
            cursor.execute(f"""
                SELECT id, title, description, date, location, address, max_participants, sold_tickets, available_tickets
                FROM {EventReadModel.TABLE_NAME}
                ORDER BY date ASC
            """)
            columns = [col[0] for col in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]

    @staticmethod
    def get_by_id(event_id):
        """Retorna um evento especifico do read model"""
        with connection.cursor() as cursor:
            cursor.execute(f"""
                SELECT id, title, description, date, location, address, max_participants, sold_tickets, available_tickets
                FROM {EventReadModel.TABLE_NAME}
                WHERE id = %s
            """, [event_id])
            row = cursor.fetchone()
            if row:
                columns = [col[0] for col in cursor.description]
                return dict(zip(columns, row))
            return None
