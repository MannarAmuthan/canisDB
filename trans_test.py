import random

import sqlglot


def replace_function_calls(sql_query):
    parsed = sqlglot.parse_one(sql_query)

    functions_map = {
        'rand': lambda: random.randint(-9223372036854775808, 9223372036854775807)
    }

    for expression in parsed.find_all(sqlglot.exp.Func):
        if expression.key in functions_map:
            value = functions_map[expression.key]()
            expression.replace(sqlglot.parse_one(str(value)))

    return parsed.sql()


# Example usage
original_query = "select random();"
modified_query = replace_function_calls(original_query)

print("Original Query:")
print(original_query)
print("\nModified Query:")
print(modified_query)
