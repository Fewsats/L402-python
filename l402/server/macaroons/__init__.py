from .macaroon_service import MacaroonService
from .sqlite_macaroon_service import SqliteMacaroonService

# import like this to avoid adding the psycopg2 dependency to the package
def PostgreSQLMacaroonService(*args, **kwargs):
    from .postgresql_macaroon_service import PostgreSQLMacaroonService as PSQLService
    return PSQLService(*args, **kwargs)