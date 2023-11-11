import yaml


def get_access_token(platform_str):
    with open('./Components/Credentials/accessTokens.yaml', 'r') as file:
        data = yaml.safe_load(file)
    return data[platform_str]

def get_platform_names():
    with open('./Components/Credentials/accessTokens.yaml', 'r') as file:
        data = yaml.safe_load(file)
    return data.keys()
