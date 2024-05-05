from pytest import mark


@mark.parametrize('tv_brand', [
    ('Samsung'),
    ('Sony'),
    ('Vizio'),
])
def test_television_turns_on(tv_brand):
    print(f'{tv_brand} turns on as expected')