import pandas as pd
from pandasql import sqldf, load_births


if __name__ == '__main__':
    births = load_births()
    print(sqldf("Select * FROM births where births > 250000 limit 5;", locals()))
    print()
    q = """
        select
            date(date) as DOB, 
            sum(births) as "Total Births"
        from
            births
        group by
            date
            limit 10;
    """
    print(sqldf(q, locals()))


