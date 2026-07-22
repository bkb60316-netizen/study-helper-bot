from supabase import Client, create_client

from services.config import config


class Database:

    def __init__(self):
        self.client: Client | None = None

    def connect(self):

        if not config.supabase_url or not config.supabase_key:
            raise ValueError(
                "Supabase credentials not found."
            )

        self.client = create_client(
            config.supabase_url,
            config.supabase_key,
        )

        return self.client

    def get_client(self):

        if self.client is None:
            return self.connect()

        return self.client


database = Database()
