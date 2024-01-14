def my_function(param, param1):
    return param + param1
    


def test_my_function():
    assert my_function(1, 2) == 3
    assert my_function(0, 0) == 0
    assert my_function(-1, 1) == 0
