import os
import sys
import json
import random
import logging
import requests
from typing import Tuple
from github import Github, NamedUser
from rich.logging import RichHandler
from datetime import datetime, timedelta


logging.basicConfig(
    level=logging.INFO,
    format="%(name)s - %(message)s",
    handlers=[
        RichHandler()
    ]
)

DEV = False
GH_GRAPHQL_API = "https://api.github.com/graphql"

if len(sys.argv) == 2 and sys.argv[1] == "--dev":
    logging.warning("dev mode enabled")

    DEV = True

    from dotenv import load_dotenv
    from rich import print

    load_dotenv()


class Inputs:
    GH_TOKEN: str | None = os.getenv("github_token")
    COMMIT_MESSAGE: str | None = os.getenv("commit_message")
    GH_USER: str | None = os.getenv("github_user")
    USER_REPO: str | None = os.getenv("user_repository")
    TEMPLATE_PATH: str | None = os.getenv("template_path")
    README_PATH: str | None = os.getenv("readme_path")
    BRANCH: str | None = os.getenv("branch")
    CODES_PATH: str | None = os.getenv("codes_path")
    CODES_USE_DAY: str | None = os.getenv("codes_use_day")
    AUTOREADME_TAG_NAME: str | None = os.getenv("autoreadme_tag_name")


def check_inputs():
    if not Inputs.GH_TOKEN:
        raise Exception("please inform your GitHub TOKEN.")

    if len(Inputs.COMMIT_MESSAGE) < 1:
        raise Exception("Commit message length must be greater than 1 character long.")

    if not Inputs.GH_USER:
        raise Exception("please inform a GitHub user.")
    
    if not Inputs.USER_REPO:
        raise Exception("please inform a GitHub user repository.")
    
    if not Inputs.TEMPLATE_PATH:
        raise Exception("please inform a path with a README template.")
    
    if Inputs.README_PATH:
        Inputs.README_PATH = "./README.md"

    if not Inputs.AUTOREADME_TAG_NAME:
        Inputs.AUTOREADME_TAG_NAME = "AUTOREADME"


def daily_code(codes: list[str]) -> dict:
    logging.info("Choosing daily code")

    if not Inputs.CODES_USE_DAY:
        code = random.choice(codes)
    else:
        date = datetime.now()
        day = date.day
        try:
            code = codes[day - 1]
        except IndexError:
            logging.info("No code found for today. Choosing random code.")
            code = random.choice(codes)
    
    return code


def create_codeblock(code_dict: dict) -> Tuple[str, str]:
    logging.info("Creating codeblock")

    name = code_dict.get("name", "")
    ext = code_dict.get("ext", "text")
    code = code_dict.get("code", "")

    codeblock = f"```{ext}\n{code}\n```"

    return codeblock, name


def replace_tags(content: str, tags: dict) -> str:
    logging.info("Replacing tags")

    for tag, tag_value in tags.items():
        tag = f"<!-- {Inputs.AUTOREADME_TAG_NAME}:{tag} -->"
        content = content.replace(tag, str(tag_value))
    
    return content


def create_medal_table(medal: str) -> str:
    logging.info("Creating medal table")

    table = f"<td width=\"100px\" align=\"center\"><p>{medal}</p></td>"

    return table


def create_follower_table(user: dict) -> str:
    logging.info("Creating follower table")

    username = user.get('username', '')
    avatar = user.get('avatar', '')
    url = user.get('url', '')
    contributions = user.get('contributions', '')

    table = f"<td width=\"100px\" align=\"center\"><img src=\"{avatar}\" width=\"100%\"/><br><a href=\"{url}\" target=\"_blank\">{username}</a><p>{contributions} {'contributions' if contributions > 1 else 'contribution'}</p></td>"
    
    return table


def create_followers_table_top_3(top_users: list) -> str:
    logging.info("Creating followers table top 3")

    if sum([x.get("contributions", 0) for x in top_users]) < 1:
        return "<p>There are no contributors yet!</p>"
        

    medal_tables = []
    user_tables = []
    for index, user in enumerate(top_users):
        medal = ""
        match index:
            case 0:
                medal = ":1st_place_medal:"
            case 1:
                medal = ":2nd_place_medal:"
            case 2:
                medal = ":3rd_place_medal:"
        
        medal_table = create_medal_table(medal)
        medal_tables.append(medal_table)

        user_table = create_follower_table(user)
        user_tables.append(user_table)

        if index == 2:
            break

    table = f"<table><tr>{''.join(medal_tables)}</tr><tr>{''.join(user_tables)}</tr></table>"

    return table


def create_followers_leaderboard(top_users: list) -> str:
    logging.info("Creating followers leaderboard")

    if sum([x.get("contributions", 0) for x in top_users]) < 1:
        return "<p align=\"center\">...</p>"

    positions = []
    for index, user in enumerate(top_users):
        username = user.get('username', '')
        url = user.get('url', '')
        contributions = int(user.get('contributions', 0))

        if contributions > 0:
            positions.append(f"<li><a href=\"{url}\">{username}</a><span> - {contributions} {'contributions' if contributions > 1 else 'contribution'}</span></li>")
        
        if index == 5:
            break
    
    return f"<ol>{''.join(positions)}</ol>"


def monthly_contributions(user: NamedUser.NamedUser) -> str:
    logging.info(f"Getting monthly contributions for {user.login}")

    current_date = datetime.now()

    first_day = current_date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    
    next_month = first_day.replace(month=(first_day.month % 12) + 1, year=first_day.year + (first_day.month // 12), day=1)
    last_day = next_month - timedelta(days=1)
    last_day = last_day.replace(hour=23, minute=59, second=59)

    first_day_str = first_day.strftime('%Y-%m-%dT%H:%M:%SZ')
    last_day_str = last_day.strftime('%Y-%m-%dT%H:%M:%SZ')

    query = '''
        query {
            user(login: "%s") {
                contributionsCollection(from: "%s", to: "%s") {
                    totalCommitContributions
                    totalRepositoryContributions
                    totalPullRequestContributions
                }
            }
        }
    ''' % (user.login, first_day_str, last_day_str)

    headers = {"Authorization": f"bearer {Inputs.GH_TOKEN}"}
    data = {'query': query}

    response = requests.post(GH_GRAPHQL_API, json=data, headers=headers)
    result: dict = response.json()

    contributions_collection = result.get("data", {}).get("user", {}).get("contributionsCollection", {})
    
    return sum(
        [
            contributions_collection.get("totalCommitContributions", 0),
            contributions_collection.get("totalRepositoryContributions", 0),
            contributions_collection.get("totalPullRequestContributions", 0)
        ]
    )


def main():
    blacklist = ["isyuricunha"] # uses automations, e.g.

    logging.info("Checking inputs")
    check_inputs()

    github = Github(
        login_or_token=Inputs.GH_TOKEN
    )

    user = github.get_user(
        login=Inputs.GH_USER
    )

    repo = user.get_repo(
        name=Inputs.USER_REPO
    )
    
    if Inputs.CODES_PATH:
        with open(Inputs.CODES_PATH, "r", encoding="utf8") as f:
            codes_list: list = json.loads(f.read())

            codeblock, language = create_codeblock(daily_code(codes_list))
    
    repo_readme = repo.get_readme()

    if DEV:
        with open(Inputs.TEMPLATE_PATH, "r", encoding="utf8") as f:
            template_readme_content: str = f.read()
    else:
        template_readme = repo.get_contents(Inputs.TEMPLATE_PATH)
        template_readme_content = template_readme.decoded_content.decode("utf-8")

    followers = user.get_followers()

    followers_contributions = sorted(
        [(follower.login, monthly_contributions(follower)) for follower in followers if follower.login not in blacklist],
        key=lambda x: x[1],
        reverse=True)

    tops = []
    for follower, contributions in followers_contributions:

        follower_user = github.get_user(login=follower)
        tops.append(
            {
                "username":follower, 
                "url":follower_user.html_url, 
                "avatar":follower_user.avatar_url, 
                "contributions": contributions
            }
        )

    top3_table = create_followers_table_top_3(tops)
    leaderboard = create_followers_leaderboard(tops)

    tags = {
        "FOLLOWERS":user.followers,
        "FOLLOWING":user.following,
        "REPOS_AMMOUNT":user.public_repos,
        "NAME":user.name,
        "DAILY_CODE_NAME":language if Inputs.CODES_PATH else "",
        "DAILY_CODE":codeblock if Inputs.CODES_PATH else "",
        "FOLLOWERS_ACTIVE_TOP_3":top3_table,
        "FOLLOWERS_ACTIVE_LEADERBOARD":leaderboard
    }

    replaced_readme_content = replace_tags(template_readme_content, tags)

    if not DEV:
        logging.info("Updating readme")
        repo.update_file(
            path=repo_readme.path,
            message=Inputs.COMMIT_MESSAGE,
            content=replaced_readme_content,
            sha=repo_readme.sha,
            branch=Inputs.BRANCH
        )
    else:
        print(replaced_readme_content)


if __name__ == "__main__":
    main()