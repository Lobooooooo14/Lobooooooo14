import logging
import os

from dotenv import load_dotenv

from src.services import (
    AI,
    CustomReadmeService,
    GeminiService,
    Generator,
    Github,
    GithubGraphqlService,
    Top3ContributorsService,
)
from src.utils import get_blacklisted_users

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)


def main():
    logging.info("Starting...")

    logging.info("Getting environment variables...")
    github_token = os.getenv("TOKEN")
    gemini_token = os.getenv("GEMINI_API_KEY")

    github_service = GithubGraphqlService(github_token)
    gemini_service = GeminiService(gemini_token)

    github = Github(github_service)
    ai = AI(gemini_service)

    logging.info("Getting blacklisted users...")
    blacklist = get_blacklisted_users()

    logging.info("Getting followers...")
    followers = [
        follower
        for follower in github.get_montly_followers_contributions()
        if follower.login not in blacklist
    ]

    top3_service = Top3ContributorsService(followers=followers)
    custom_readme_service = CustomReadmeService(
        "assets/readme_template.md", github.get_viewer(), followers, ai
    )

    generator = Generator(top3_service)
    generator.generate("output/cards/top3.svg")

    generator.change_service(custom_readme_service)
    generator.generate("README.md")


if __name__ == "__main__":
    main()
