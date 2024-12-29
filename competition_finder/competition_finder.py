import requests
from bs4 import BeautifulSoup
import random
import time

# Function to generate refined search prompts based on user inputs
def generate_search_prompts(interests, education_status, age, location):
    base_prompts = []
    interests_list = [interest.strip() for interest in interests.split(",")]

    # Create search prompts for each interest
    for interest in interests_list:
        base_prompts.append(
            f"{interest} competitions for {education_status} aged {age}"
        )
        base_prompts.append(
            f"{interest} contests for students in {location} or online"
        )
        base_prompts.append(
            f"opportunities for {education_status} interested in {interest}"
        )
        base_prompts.append(
            f"lesser-known {interest} contests 2024"
        )

    additional_keywords = ["international/worldwide", "local", "online"]

    refined_prompts = []
    for prompt in base_prompts:
        for keyword in additional_keywords:
            refined_prompts.append(f"{prompt} {keyword}")

    return refined_prompts

# Function to fetch competitions from Google
def fetch_google_competitions(search_query):
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

# Main function to find competitions
def find_competitions(city, state_province, country, age, interests, education_status):
    location = f"{city}, {state_province}, {country}"
    all_competitions = []

    # Generate multiple search prompts
    prompts = generate_search_prompts(interests, education_status, age, location)

    # Perform searches for each prompt
    for prompt in prompts:  
        results = fetch_google_competitions(prompt)
        all_competitions.extend(results)
        time.sleep(random.uniform(1, 3))  # Sleep to mimic natural browsing behavior

    # Deduplicate competitions by title
    unique_competitions = {comp["title"]: comp for comp in all_competitions if "title" in comp}.values()

    return list(unique_competitions)

# Example use case
if __name__ == "__main__":
    city = "Ottawa"
    state_province = "Ontario"
    country = "Canada"
    age = "16"
    interests = "coding, robotics, entrepreneurship"
    education_status = "High School"

    competitions = find_competitions(city, state_province, country, age, interests, education_status)
    for comp in competitions:
        print(f"Title: {comp['title']}\nLink: {comp['link']}\nSnippet: {comp['snippet']}\nEligibility: {comp['eligibility']}\n")
