import logging
from abc import ABC, abstractmethod

import requests

from src.modules import Followers, User, Viewer
from src.utils import get_current_month_interval, get_graphql_query


class GithubService(ABC):
    """
    Abstract class for Github services.

    Methods
    -------
    get_viewer() -> Viewer
        Get the viewer's information.
    get_montly_followers_contributions() -> list[User]
        Get the followers' contributions in the current month.
    """

    @abstractmethod
    def get_viewer(self) -> Viewer:
        """
        Get the viewer's information.

        Returns
        -------
        Viewer
            The viewer's information.
        """

        pass

    @abstractmethod
    def get_montly_followers_contributions(self) -> list[User]:
        """
        Get the followers contributions in the current month.

        Returns
        -------
        list[User]
            The followers contributions in the current month.
        """

        pass


class Github:
    """
    Class for Github services.

    Attributes
    ----------
    github_service : GithubService
        The Github service.

    Methods
    -------
    change_service(github_service: GithubService) -> None
        Change the Github service.
    get_viewer() -> Viewer
        Get the viewer's information.
    get_montly_followers_contributions() -> list[User]
        Get the followers contributions in the current month
    """

    def __init__(self, github_service: GithubService) -> None:
        self.github_service = github_service

    def change_service(self, github_service: GithubService) -> None:
        """
        Change the Github service.

        Parameters
        ----------
        github_service : GithubService
            The Github service.
        """

        logging.info(
            "Changing Github service to " + github_service.__class__.__name__
        )
        self.github_service = github_service

    def get_viewer(self) -> Viewer:
        """
        Get the viewer's information.

        Returns
        -------
        Viewer
            The viewer's information.
        """

        logging.info(
            "Getting viewer with " + self.github_service.__class__.__name__
        )
        return self.github_service.get_viewer()

    def get_montly_followers_contributions(self) -> list[User]:
        """
        Get the followers contributions in the current month.

        Returns
        -------
        list[User]
            The followers contributions in the current month.
        """

        logging.info(
            "Getting followers contributions with "
            + self.github_service.__class__.__name__
        )
        return self.github_service.get_montly_followers_contributions()


class GithubGraphqlService(GithubService):
    """
    Class for Github GraphQL services.

    Attributes
    ----------
    token : str
        The Github token.

    Methods
    -------
    get_viewer() -> Viewer
        Get the viewer's information.
    get_montly_followers_contributions() -> list[User]
        Get the followers contributions in the current month
    """

    GH_GRAPHQL_ENDPOINT = "https://api.github.com/graphql"

    def __init__(self, token: str):
        self.headers = {"Authorization": f"Bearer {token}"}

    def get_viewer(self) -> Viewer:
        """
        Get the viewer's information.

        Returns
        -------
        Viewer
            The viewer's information.
        """

        logging.info("Getting viewer with Github GraphQL")

        query = get_graphql_query("viewer")

        response = requests.post(
            self.GH_GRAPHQL_ENDPOINT,
            headers=self.headers,
            json={"query": query},
        )

        if response.status_code != 200:
            logging.error("Failed to get viewer")
            raise ValueError("Failed to get viewer")

        data: dict = response.json()

        return Viewer(**data["data"]["viewer"])

    def get_montly_followers_contributions(self) -> list[User]:
        """
        Get the followers contributions in the current month.

        Returns
        -------
        list[User]
            The followers contributions in the current month.
        """

        logging.info("Getting followers contributions with Github GraphQL")

        query = get_graphql_query("followers_contributions_date_range")

        logging.info("Getting current month interval")
        from_date, to_date = get_current_month_interval()

        nodes: list[User] = []

        graphql_variables: dict[str, str | None] = {
            "cursor": None,
            "fromDate": from_date,
            "toDate": to_date,
        }

        logging.info("Getting followers...")
        while True:
            logging.info(f"cursor: {graphql_variables['cursor']}")

            response = requests.post(
                self.GH_GRAPHQL_ENDPOINT,
                headers=self.headers,
                json={
                    "query": query,
                    "variables": graphql_variables,
                },
            )

            if response.status_code != 200:
                logging.error(
                    "Failed to get followers"
                    + str(response.status_code)
                    + "status code"
                )
                break

            data: dict = response.json()

            followers = Followers(**data["data"]["viewer"]["followers"])

            logging.info("Getting next page...")
            graphql_variables.update({"cursor": followers.pageInfo.endCursor})
            nodes.extend(followers.nodes)

            if not followers.pageInfo.hasNextPage:
                logging.info("No more pages")
                break

        return nodes
