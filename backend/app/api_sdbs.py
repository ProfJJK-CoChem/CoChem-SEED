import requests

def fetch_sdbs(inchi_key: str):
    # Mocking SDBS fetch
    return {
        "x": [1705.0, 2960.0],
        "y": [1.2, 0.6],
        "source": "SDBS Mock"
    }

def fetch_nist(inchi_key: str):
    # Mocking NIST fetch
    return {
        "fragments": [15, 29, 43],
        "source": "NIST Mock"
    }
