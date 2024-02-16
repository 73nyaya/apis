def find_dict(nested_dict: dict, target_key: str, target_value: str) -> dict:
    found = False
    for key, val in nested_dict.items():
        if isinstance(val, dict):
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
        print('value found!')
    else:
        print('not found')

def get_key_from_value(dictionary: dict, value: str) -> str:
    for key, val in dictionary.items():
        if val == value:
            return key
    return None

def find_dict_in_list(my_list: tuple[dict, ...], target_key : str, target_val: str):
    found = False
    for dicts in my_list:
        key_pair = find_dict(dict, target_key=target_key, target_value=target_val)
        if isinstance(key_pair, dict):
            found = True
            return find_dict(dict, target_key=target_key, target_value=target_val)
            break
    if found:
        print('value found!')
    else:
        print('not found')