import os

from dotenv import load_dotenv

from src import GeminiService, GithubService
from src.modules import User, Viewer
from src.services.generators import CustomReadme, Top3ContributorsGenerator

load_dotenv()


def get_blacklisted_users() -> list[str]:
    blacklist = []

    with open("assets/blacklist.txt") as f:
        for line in f:
            blacklist.append(line.strip())

    return blacklist


def create_top3(followers: list[User]) -> None:
    top3 = Top3ContributorsGenerator(followers)
    top3.create()
    top3.save("output/cards/top3.svg")


def update_custom_readme(
    viewer: Viewer, followers: list[User], gemini_service: GeminiService
) -> None:
    custom_readme = CustomReadme(
        "assets/readme_template.md", viewer, followers, gemini_service
    )
    custom_readme.create()
    custom_readme.save("README.md")


def main():
    token = os.getenv("TOKEN")
    gemini_api_key = os.getenv("GEMINI_API_KEY")

    blacklist = get_blacklisted_users()

    gh_service = GithubService(token)
    viewer = gh_service.get_viewer()

    gemini_service = GeminiService(gemini_api_key, viewer)

    followers_data = gh_service.get_montly_followers_contributions()

    followers = [
        follower
        for follower in followers_data
        if follower.login not in blacklist
    ]

    create_top3(followers)
    update_custom_readme(viewer, followers, gemini_service)


if __name__ == "__main__":
    main()
