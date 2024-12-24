import requests
from bs4 import BeautifulSoup
import json

def fetch_devpost_competitions(interests):
    """
    Fetches hackathons from Devpost related to the user's interests.

    Args:
        interests (str): User's interests (e.g., coding, AI).

    Returns:
        list: List of competitions with details from Devpost.
    """
    url = f"https://devpost.com/hackathons?search={interests.replace(' ', '+')}"
    competitions = []

    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        # Extract hackathon details
        for item in soup.find_all("div", class_="hackathon-tile"):
            title = item.find("h3").text.strip() if item.find("h3") else "No Title"
            link = "https://devpost.com" + item.find("a")["href"] if item.find("a") else "No Link"
            snippet = item.find("p", class_="description").text.strip() if item.find("p", class_="description") else "No Description"

            competitions.append({
                "title": title,
                "link": link,
                "snippet": snippet,
                "eligibility": "Check the hackathon page for detailed eligibility criteria."
            })

        return competitions
    except Exception as e:
        return [{"error": f"Failed to fetch competitions from Devpost: {str(e)}"}]

def fetch_google_competitions(location, age, interests, education_status):
    """
    Searches for competitions via Google.

    Args:
        location (str): User's location.
        age (str): User's age.
        interests (str): User's interests.
        education_status (str): User's education status.

    Returns:
        list: List of competitions as dictionaries with details.
    """
    search_query = f"{interests} competitions OR contests for {education_status} aged {age} in {location} OR online eligibility"
    url = f"https://www.google.com/search?q={search_query.replace(' ', '+')}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        results = []
        for g in soup.find_all("div", class_="tF2Cxc"):
            title = g.find("h3").text if g.find("h3") else "No Title"
            link = g.find("a")["href"] if g.find("a") else "No Link"
            snippet = g.find("span", class_="aCOpRe").text if g.find("span", class_="aCOpRe") else "No Description"

            if "competition" in title.lower() or "contest" in title.lower():
                results.append({
                    "title": title,
                    "link": link,
                    "snippet": snippet,
                    "eligibility": "Check the competition link for detailed eligibility."
                })

        return results
    except Exception as e:
        return [{"error": f"Failed to fetch competitions from Google: {str(e)}"}]

def find_competitions(city, state_province, country, age, interests, education_status):
    """
    Aggregates competitions from various sources based on user input.

    Args:
        city (str): User's city.
        state_province (str): User's state or province.
        country (str): User's country.
        age (str): User's age.
        interests (str): User's interests.
        education_status (str): User's education status.

    Returns:
        list: List of competitions with details.
    """
    location = f"{city}, {state_province}, {country}"
    all_competitions = []

    # Fetch competitions from Devpost (for coding and tech-related interests)
    if "coding" in interests.lower() or "hackathon" in interests.lower():
        all_competitions.extend(fetch_devpost_competitions(interests))

    # Fetch competitions from Google
    all_competitions.extend(fetch_google_competitions(location, age, interests, education_status))

    # Filter duplicates by title
    unique_competitions = {comp["title"]: comp for comp in all_competitions}.values()

    return list(unique_competitions)

# Example use case
if __name__ == "__main__":
    city = "Ottawa"
    state_province = "Ontario"
    country = "Canada"
    age = "16"
    interests = "coding"
    education_status = "High School"

    competitions = find_competitions(city, state_province, country, age, interests, education_status)
    for comp in competitions:
        print(f"Title: {comp['title']}\nLink: {comp['link']}\nSnippet: {comp['snippet']}\nEligibility: {comp['eligibility']}\n")
