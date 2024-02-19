def find_dict(nested_dict: dict, target_key: str, target_value: str) -> dict:
    found = False
    for key, val in nested_dict.items():
        if isinstance(val, dict):
            print('iterating over val ', val)
            result = find_dict(val, target_key, target_value)
            if result is not None:
                found = True
                return result
                break
        elif key == target_key and val == target_value:
            return nested_dict  # return the entire dictionary if the key-value pair is found
            found = True
            break
    if found:
        print('value found in nested dict!')
    else:
        print('not found in nested dict')

def get_key_from_value(dictionary: dict, value: str) -> str:
    for key, val in dictionary.items():
        if val == value:
            return key
    return None

def find_dict_in_list(my_list: tuple[dict, ...], target_key : str, target_val: str):
    found_list = False
    for dicts in my_list:
        print('iterating over ', dicts)
        key_pair = find_dict(dicts, target_key=target_key, target_value=target_val)
        if isinstance(key_pair, dict):
            found_list = True
            return key_pair
            break
    if found_list:
        print('value found in list!')
    else:
        print('not found in list')