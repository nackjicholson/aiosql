# Advanced Topics

## Leveraging Driver Specific Features

## Access the `cursor` object

## Accessing prepared SQL as a string

When you need to do something not directly supported by aiosql, this is your escape hatch. You can still define your sql in a file and load it with aiosql, but then you may choose to use it without calling your aiosql method. The prepared SQL string of a method is available as an attribute of each method `queries.<method_name>.sql`. Here's an example of how you might use it with a unique feature of `psycopg2` like `execute_values`.

TODO: Link to execute_values docs and write an example usage.
