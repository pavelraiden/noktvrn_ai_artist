import json
from datetime import datetime, timedelta


def generate_calendar(start_date, days, profile_data, strategy_data):
    calendar = []
    date = datetime.strptime(start_date, "%Y-%m-%d")
    cta = strategy_data.get(
        "cta_templates", ["Listen now", "Available on all platforms"]
    )
    platforms = strategy_data.get(
        "platforms", ["TikTok", "Threads", "YouTube Shorts"]
    )
    tones = strategy_data.get("tone", "mysterious")

    for i in range(days):
        platform = platforms[i % len(platforms)]
        calendar.append(
            {
                "date": (date + timedelta(days=i)).strftime("%Y-%m-%d"),
                "platform": platform,
                "post_type": "teaser",
                "prompt": f"{profile_data['name']} in {tones} mood. Don't miss it.",
                "cta": cta[i % len(cta)],
            }
        )
    return calendar


if __name__ == "__main__":
    with open("artists/noktvrn/profile/phonk_artist_profile_v2.json") as f:
        profile = json.load(f)
    with open("artists/noktvrn/profile/strategy_profile.json") as f:
        strategy = json.load(f)

    plan = generate_calendar("2025-05-01", 30, profile, strategy)
    with open("artists/noktvrn/calendar/2025-05_calendar.json", "w") as f:
        json.dump(plan, f, indent=2)
