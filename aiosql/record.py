def assign_record_class(result, columns, record_class, one=False):
    if columns is None:  # means it comes from asyncpg
        try:
            import pandas as pd
            if isinstance(record_class, pd.DataFrame):
                return pd.concat([record_class(dict(rec)) for rec in results])
        except ImportError as _:
            pass
        if not one:
            return [record_class(**dict(rec)) for rec in results]
        else:
            return record_class(**dict(result))
    
    # else -> psycopg2, sqlite3, aiosqlite
    try:
        import pandas as pd
        if isinstance(record_class, pd.DataFrame):
            return record_class(results, columns=columns)
    except ImportError as _:
        pass
    if not one:
        return [record_class(**dict(zip(column_names, row))) for row in results]
    else:
        return record_class(**dict(zip(column_names, result)))
