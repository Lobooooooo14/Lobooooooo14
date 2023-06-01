import os
import sys
import json
import random
from typing import Tuple
from github import Github
from datetime import datetime


DEV = False

if len(sys.argv) == 2 and sys.argv[1] == "--dev":
    from dotenv import load_dotenv

    load_dotenv()

    DEV = True


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
    if not Inputs.CODES_USE_DAY:
        code = random.choice(codes)
    else:
        date = datetime.now()
        day = date.day
        try:
            code = codes[day - 1]
        except IndexError:
            code = random.choice(codes)
    
    return code


def create_codeblock(code_dict: dict) -> Tuple[str, str]:
    name = code_dict.get("name", "")
    ext = code_dict.get("ext", "text")
    code = code_dict.get("code", "")

    codeblock = f"```{ext}\n{code}\n```"

    return codeblock, name


def replace_tags(content: str, tags: dict) -> str:
    for tag, tag_value in tags.items():
        tag = f"<!-- {Inputs.AUTOREADME_TAG_NAME}:{tag} -->"
        content = content.replace(tag, str(tag_value))
    
    return content


def create_medal_table(medal: str) -> str:
    table = f"<td width=\"100px\" align=\"center\"><p>{medal}</p></td>"

    return table


def create_follower_table(user: dict) -> str:
    username = user.get('username', '')
    avatar = user.get('avatar', '')
    url = user.get('url', '')
    contributions = user.get('contributions', '')

    table = f"<td width=\"100px\" align=\"center\"><img src=\"{avatar}\" width=\"100%\"/><br><a href=\"{url}\" target=\"_blank\">{username}</a><p>{contributions} contribuições</p></td>"
    
    return table


def create_followers_table_top_3(top_users: list) -> str:
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
    positions = []
    for index, user in enumerate(top_users):
        username = user.get('username', '')
        url = user.get('url', '')
        contributions = int(user.get('contributions', 0))

        if contributions > 0:
            positions.append(f"<li><a href=\"{url}\">{username}</a><span> - {contributions} {'contribuicões' if contributions > 1 else 'contribuição'}</span></li>")
        
        if index == 5:
            break
    
    return f"<ol>{''.join(positions)}</ol>"


def monthly_contributions(user):
        total_contributions = 0
        events = user.get_events()
        for event in events:
            if event.type == 'PushEvent':
                total_contributions += 1

        return total_contributions


def main():
    check_inputs()

    LAST_UPDATED = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

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

    followers = sorted(followers, key=lambda x: monthly_contributions(x), reverse=True)

    tops = []
    for follower in followers:
        login = follower.login
        contributions = monthly_contributions(follower)

        follower_user = github.get_user(login=login)
        tops.append(
            {
                "username":login, 
                "url": follower_user.url, 
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
        "LAST_UPDATED":LAST_UPDATED,
        "DAILY_CODE_NAME":language if Inputs.CODES_PATH else "",
        "DAILY_CODE":codeblock if Inputs.CODES_PATH else "",
        "FOLLOWERS_ACTIVE_TOP_3":top3_table,
        "FOLLOWERS_ACTIVE_LEADERBOARD":leaderboard
    }


    replaced_readme_content = replace_tags(template_readme_content, tags)

    repo.update_file(
        path=repo_readme.path,
        message=Inputs.COMMIT_MESSAGE,
        content=replaced_readme_content,
        sha=repo_readme.sha,
        branch=Inputs.BRANCH
    )


if __name__ == "__main__":
    main()