import requests


def identify_plant(file_names):
    # PlantNet API endpoint
    url = "https://my-api.plantnet.org/v2/identify/all"

    # Replace with your API key from dashboard
    api_key = "2b10Bz5aV3mdnKlqL7ioP8Vie"

    files = []
    for img in file_names:
        files.append(('images', open(img, 'rb')))

    params = {
    "api-key": api_key,
    "lang": "en"
    }

    try:
        response = requests.post(url, files=files, params=params)

        print("Status Code:", response.status_code)
        print("Response Text:", response.text)

        return response.json()

    except Exception as e:
        return {
            "error": "PlantNet API request failed",
            "details": str(e)
        }


def recursive_items(dictionary):
    for key, value in dictionary.items():
        if type(value) is dict:
            yield from recursive_items(value)
        else:
            yield (key, value)


'''
Testing block (not used in Django)

if __name__ == '__main__':
    x = identify_plant(["../img/photo1.jpg"])

    for key, value in recursive_items(x):
        print(key, value)
'''