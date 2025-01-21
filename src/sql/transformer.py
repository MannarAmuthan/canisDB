import random

import sqlglot


def transform_sql_query(sql_string: str):
    sql_string = replace_non_deterministic_function_calls(sql_string)
    return sql_string


def replace_non_deterministic_function_calls(sql_query):
    parsed = sqlglot.parse_one(sql_query)

    functions_map = {
        'rand': lambda: random.randint(-9223372036854775808, 9223372036854775807)
    }

    for expression in parsed.find_all(sqlglot.exp.Func):
        if expression.key in functions_map:
            value = functions_map[expression.key]()
            expression.replace(sqlglot.parse_one(str(value)))

    return parsed.sql()
