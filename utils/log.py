import json


def log(message, end="\n", flush=False):
    # print with white color
    print("\033[0m" + str(message) + "\033[0m", end=end, flush=flush)


def save_debug(data, response):
    """Save the debug to a file."""
    with open("debug_data.json", "w") as f:
        json.dump(data, f)
    with open("debug_response.json", "w") as f:
        json.dump(response, f)
