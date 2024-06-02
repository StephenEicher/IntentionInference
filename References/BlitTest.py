from immutables import Map
import immutables as im

Test_map =  Map({"key1": "value1", "key2": "value2"})
test_dict = {}

if (None, Test_map) not in test_dict:
    print('hello')