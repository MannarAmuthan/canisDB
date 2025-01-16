def is_write_operation(sql_string: str):
    tokens = [_t.lower() for _t in sql_string.split(" ")]

    write_operation_tokens = ['insert', 'update', 'delete', 'drop', 'create', 'alter', 'truncate', 'replace', 'merge',
                              'upsert', 'grant', 'revoke', 'vacuum', 'reindex']

    for _t in tokens:
        if _t in write_operation_tokens:
            return True

    return False


