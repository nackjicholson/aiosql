def assign_record_class(result, columns, record_class, one=False):
    if columns is None:  # means it comes from asyncpg
        try:
            import pandas as pd
            if record_class == pd.DataFrame:
                if len(result) == 0:
                    return record_class()
                columns = list(result[0].keys())
                return record_class([rec.values() for rec in result], columns=columns)
        except ImportError as _:
            pass
        if not one:
            return [record_class(**dict(rec)) for rec in result]
        else:
            return record_class(**dict(result))
    
    # else -> psycopg2, sqlite3, aiosqlite
    try:
        import pandas as pd
        if record_class == pd.DataFrame:
            return record_class(result, columns=columns)
    except ImportError as _:
        pass
    if not one:
        return [record_class(**dict(zip(columns, row))) for row in result]
    else:
        return record_class(**dict(zip(columns, result)))
