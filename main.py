import os
from dotenv import load_dotenv
from src import GithubService
from src.services.generators import Top3ContributorsGenerator
from src.modules import User


load_dotenv()


def get_blacklisted_users() -> list[str]:
    blacklist = []

    with open("assets/blacklist.txt", "r") as f:
        for line in f:
            blacklist.append(line.strip())

    return blacklist


def create_top3(followers: list[User]) -> None:
    top3 = Top3ContributorsGenerator(followers)
    top3.create()
    top3.save("output/top3.svg")


def main():
    token = os.getenv("TOKEN")
    blacklist = get_blacklisted_users()

    gh_service = GithubService(token)

    followers_data = gh_service.get_montly_followers_contributions()

    followers = [
        follower for follower in followers_data if follower.login not in blacklist
    ]

    create_top3(followers)


if __name__ == "__main__":
    main()
