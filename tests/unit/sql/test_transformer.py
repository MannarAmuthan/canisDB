import re

from sql.transformer import replace_non_deterministic_function_calls


def test_should_transform_query_with_random_function():
    transformed_string = replace_non_deterministic_function_calls("select random() as col1")

    assert re.match('SELECT\s+(-?\d+)\s+AS\s+col1', transformed_string), \
        f"SQL string '{transformed_string}' does not match expected pattern"
