import yaml


def get_access_token(platform_str):
    with open('./Components/Credentials/accessTokens.yaml', 'r') as file:
        data = yaml.safe_load(file)
    return data[platform_str]


def get_platform_names():
    with open('./Components/Credentials/accessTokens.yaml', 'r') as file:
        data = yaml.safe_load(file)
    return data.keys()


def update_token(platform_str, token_str):
    with open('./Components/Credentials/accessTokens.yaml', 'r') as file:
        data = yaml.safe_load(file)
        data[platform_str] = token_str

    with open('./Components/Credentials/accessTokens.yaml', 'w') as file:
        yaml.dump(data, file, default_flow_style=False)
