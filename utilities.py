def find_dict(nested_dict, target_key, target_value):
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

def get_key_from_value(dictionary, value):
    for key, val in dictionary.items():
        if val == value:
            return key
    return None