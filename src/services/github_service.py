import requests

from src.modules import Followers, User, Viewer
from src.utils import get_current_month_interval, get_query


class GithubService:
    GH_GRAPHQL_ENDPOINT = "https://api.github.com/graphql"

    def __init__(self, token: str):
        self.headers = {"Authorization": f"Bearer {token}"}

    def get_viewer(self) -> Viewer:
        query = get_query("viewer.graphql")

        if not query:
            raise ValueError("No query found for " + self.get_viewer.__name__)

        response = requests.post(
            self.GH_GRAPHQL_ENDPOINT,
            headers=self.headers,
            json={"query": query},
        )

        if response.status_code != 200:
            raise ValueError("Failed to get viewer")

        data: dict = response.json()

        return Viewer(**data["data"]["viewer"])

    def get_montly_followers_contributions(self) -> list[User]:
        query = get_query("followers.graphql")

        if not query:
            raise ValueError(
                "No query found for "
                + self.get_montly_followers_contributions.__name__
            )

        from_date, to_date = get_current_month_interval()

        followers_nodes: list[User] = []

        variables: dict[str, str | None] = {
            "cursor": None,
            "fromDate": from_date,
            "toDate": to_date,
        }

        while True:
            response = requests.post(
                self.GH_GRAPHQL_ENDPOINT,
                headers=self.headers,
                json={
                    "query": query,
                    "variables": variables,
                },
            )

            if response.status_code != 200:
                break

            data: dict = response.json()

            try:
                data["data"]["viewer"]["followers"]
            except KeyError:
                break

            followers = Followers(**data["data"]["viewer"]["followers"])

            variables.update({"cursor": followers.pageInfo.endCursor})
            followers_nodes.extend(followers.nodes)

            if not followers.pageInfo.hasNextPage:
                break

        return followers_nodes
