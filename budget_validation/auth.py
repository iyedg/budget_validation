import pygsheets


def get_client():
    gc = pygsheets.authorize(
        client_secret="credentials/credentials.json",
        credentials_directory="credentials",
    )
    return gc
