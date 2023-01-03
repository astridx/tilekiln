
from tilekiln.config import Config
from psycopg_pool import ConnectionPool

DEFAULT_SCHEMA = "tilekiln"


class Storage:
    def __init__(self, config: Config, dbpool: ConnectionPool):
        self.__config = config
        self.__pool = dbpool

    def create_tables(self):
        with self.__pool.connection() as conn:
            minzoom = self.__config.minzoom
            maxzoom = self.__config.maxzoom
            id = self.__config.id
            schema = DEFAULT_SCHEMA
            with conn.cursor() as cur:
                cur.execute(f'''CREATE SCHEMA IF NOT EXISTS "{schema}"''')
                cur.execute(f'''CREATE TABLE "{schema}"."{id}" (
                    z smallint CHECK (z >= {minzoom} AND z <= {maxzoom}),
                    x int CHECK (x >= 0 AND x < 1 << z),
                    y int CHECK (x >= 0 AND x < 1 << z),
                    tile bytea NOT NULL,
                    primary key (z, x, y)
                    ) PARTITION BY LIST (z)''')
                for z in range(minzoom, maxzoom+1):
                    tablename = f"{id}_z{z}"
                    cur.execute(f'''CREATE TABLE "{schema}"."{tablename}"
                                    PARTITION OF "{schema}"."{id}" FOR VALUES IN ({z})''')
                    # tile is already compressed, so tell postgres to not compress it again
                    cur.execute(f'''ALTER TABLE "{schema}"."{tablename}"
                                    ALTER COLUMN tile SET STORAGE EXTERNAL''')

                conn.commit()

    def remove_tables(self):
        with self.__pool.connection() as conn:
            id = self.__config.id
            schema = DEFAULT_SCHEMA
            with conn.cursor() as cur:
                cur.execute(f'''DROP TABLE "{schema}"."{id}" CASCADE''')
                conn.commit()

    def truncate_tables(self, zooms=None):
        with self.__pool.connection() as conn:
            minzoom = self.__config.minzoom
            maxzoom = self.__config.maxzoom
            with conn.cursor() as cur:
                if zooms is None:
                    for z in range(minzoom, maxzoom+1):
                        self.__truncate_table(z, cur)
                else:
                    for z in zooms:
                        self.__truncate_table(z, cur)

    def __truncate_table(self, zoom, cur):
        tablename = f"{self.__config.id}_z{zoom}"
        schema = DEFAULT_SCHEMA
        cur.execute(f'''TRUNCATE TABLE "{schema}"."{tablename}"''')
