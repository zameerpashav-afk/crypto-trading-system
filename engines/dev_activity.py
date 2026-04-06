import requests

COINGECKO_API = "https://api.coingecko.com/api/v3"


def get_dev_data(coin_id):
    try:
        url = f"{COINGECKO_API}/coins/{coin_id}"
        data = requests.get(url).json()

        dev = data.get("developer_data", {})

        return {
            "commits": dev.get("commit_count_4_weeks", 0),
            "stars": dev.get("stars", 0),
            "forks": dev.get("forks", 0)
        }
    except:
        return {"commits": 0, "stars": 0, "forks": 0}


def compute_dev_score(coin_id):
    data = get_dev_data(coin_id)

    score = (
        min(data["commits"] / 100, 1) * 0.5 +
        min(data["stars"] / 5000, 1) * 0.3 +
        min(data["forks"] / 2000, 1) * 0.2
    )

    return {
        "score": score,
        "confidence": 0.8,
        "signals": data
    }
if __name__ == "__main__":
    result = compute_dev_score("bitcoin")
    print(result)