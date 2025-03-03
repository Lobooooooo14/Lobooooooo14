import json
import logging
import xml.etree.ElementTree as ET
from abc import ABC, abstractmethod
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from textwrap import shorten

from jinja2 import Environment

from src.modules.user import User
from src.modules.viewer import Viewer
from src.services.ai_service import AI
from src.utils import (
    encode_image_from_url_to_data_image,
    format_number,
    get_template_path,
)


class GeneratorService(ABC):
    """
    Abstract class for generator services.

    Methods
    -------
    create(self) -> None:
        Abstract method that creates the generator service.
    save(self, output: Path | str) -> None:
        Abstract method that saves the generated output to a file.
    """

    @abstractmethod
    def create(self) -> None:
        """
        Abstract method that creates the generator service.
        """
        pass

    @abstractmethod
    def save(self, output: Path | str) -> None:
        """
        Abstract method that saves the generated output to a file.

        Parameters
        ----------
        output : Path | str
            The path or name of the file to save the generated output to.
        """
        pass


class Generator:
    """
    Class that uses a GeneratorService to generate content.

    Attributes
    ----------
    generator_service : GeneratorService
        A GeneratorService object used to generate content.

    Methods
    -------
    change_service(self, generator_service: GeneratorService) -> None:
        Change the generator service used to generate content.
    generate(self, output: Path | str) -> None:
        Generate content and save it to a file.
    """

    def __init__(self, generator_service: GeneratorService) -> None:
        self.generator_service = generator_service

    def change_service(self, generator_service: GeneratorService) -> None:
        """
        Change the generator service used to generate content.

        Parameters
        ----------
        generator_service : GeneratorService
            A GeneratorService object used to generate content.
        """

        logging.info(
            "Changing generator service to"
            + generator_service.__class__.__name__
        )
        self.generator_service = generator_service

    def generate(self, output: Path | str) -> None:
        """
        Generate content and save it to a file.

        Parameters
        ----------
        output : Path | str
            The path or name of the file to save the generated content to.
        """

        logging.info(
            "Generating content with"
            + self.generator_service.__class__.__name__
        )
        self.generator_service.create()
        self.generator_service.save(output)


class Top3ContributorsService(GeneratorService):
    """
    Class that implements a GeneratorService that generates a SVG file
    with the top 3 contributors.

    Attributes
    ----------
    followers : list[User] | None
        A list of User objects representing the top 3 contributors.

    Methods
    -------
    create(self) -> None:
        Create the SVG file with the top 3 contributors.
    save(self, output: Path | str) -> None:
        Save the SVG file with the top 3 contributors to a file.
    """

    SVG_NS = {"svg": "http://www.w3.org/2000/svg"}

    def __init__(self, followers: list[User] | None = None) -> None:
        self.tree: ET.ElementTree | None = None
        self.followers = followers
        self.template_path = get_template_path("top3", "svg")
        self.need_followers_template = get_template_path(
            "need-followers-contributions", "svg"
        )

    def create(self) -> None:
        """
        Create the SVG file with the top 3 contributors.
        """

        if self.template_path is None:
            raise ValueError(
                "No template found for top3 contributors generator"
            )

        if self.followers is None:
            raise ValueError(
                "No followers provided for top3 contributors generator"
            )

        if (
            len(self.followers) < 3
            or sum([user.get_total_contributions() for user in self.followers])
            < 1
        ):
            self.tree = ET.parse(self.need_followers_template)
            root = self.tree.getroot()

            element = root.find(".//*[@id='message']", self.SVG_NS)

            if element is not None:
                logging.info("No contributions from followers found")
                element.text = (
                    f"waiting for contributions from followers "
                    f"({len(self.followers)}/3)"
                )

            return

        logging.info("Sorting followers by contributions and username")
        self.followers.sort(
            key=lambda user: (
                -user.get_total_contributions(),
                user.get_username(),
            )
        )

        top3_followers = self.followers[:3]

        self.tree = ET.parse(self.template_path)
        root = self.tree.getroot()

        followers_contents: dict = {
            "texts": {},
            "images": {},
        }

        for index, user in enumerate(top3_followers):
            user_contributions = user.get_total_contributions()

            logging.info(
                f"User {user.get_username()}: {user_contributions} ctr."
            )

            followers_contents["texts"].update(
                {
                    f"user_{index}_username": shorten(
                        user.get_username(), width=19, placeholder="..."
                    ),
                    f"user_{index}_contributions": (
                        f"{format_number(user_contributions)} Ctr."
                    ),
                }
            )

            followers_contents["images"].update(
                {
                    f"user_{index}_avatar": (
                        encode_image_from_url_to_data_image(
                            f"{user.avatarUrl}&size=128"
                        )
                    ),
                }
            )

        logging.info("Updating SVG file with top 3 contributors...")
        for content_type in followers_contents:
            for key, value in followers_contents[content_type].items():
                element = root.find(f".//*[@id='{key}']", self.SVG_NS)

                if element is not None:
                    if content_type == "texts":
                        element.text = ""
                        element.text = str(value)

                    if content_type == "images":
                        element.attrib["href"] = ""
                        element.attrib["href"] = str(value)

    def save(self, output: Path | str) -> None:
        """
        Save the SVG file with the top 3 contributors to a file.
        """

        if self.template_path is None or self.tree is None:
            logging.error("No template or tree found")
            raise ValueError("No template or tree found")

        if isinstance(output, str):
            output = Path(output)

        if output.is_dir():
            output = output / "output.svg"

        output = output.absolute()

        output.parent.mkdir(parents=True, exist_ok=True)
        output.touch(exist_ok=True)

        ET.register_namespace("", "http://www.w3.org/2000/svg")

        logging.info("Saving SVG file with top 3 contributors...")
        self.tree.write(output, encoding="utf-8", xml_declaration=True)

    def __repr__(self) -> str:
        return (
            f"Top3ContributorsGenerator(followers={self.followers!r},"
            f"template={self.template_path!r})"
        )


class CustomReadmeService(GeneratorService):
    """
    Class that implements a GeneratorService that generates a custom readme.

    Attributes
    ----------
    readme_path : Path | str
        The path to the readme file.
    viewer : Viewer
        The viewer object.
    followers : list[User]
        The followers of the viewer.
    ai : AI
        The AI service.

    Methods
    -------
    create(self) -> None:
        Create the custom readme.
    save(self, output: Path | str) -> None:
        Save the custom readme to a file.
    """

    def __init__(
        self,
        readme_path: Path | str,
        viewer: Viewer,
        followers: list[User],
        ai: AI,
    ) -> None:
        self.readme_path = readme_path
        self.env = Environment(
            trim_blocks=True,
            lstrip_blocks=True,
        )
        self.rendered_readme: str = ""
        self.viewer = viewer
        self.followers = followers
        self.ai = ai

    def create(self) -> None:
        """
        Create the custom readme.

        Raises
        ------
        ValueError
            If the readme path, viewer, or followers is not provided
            or if the readme path is not found or is not a file.
        """
        if self.readme_path is None:
            logging.error("No readme path provided for custom readme")
            raise ValueError("No readme path provided for custom readme")

        if isinstance(self.readme_path, str):
            self.readme_path = Path(self.readme_path)

        if not self.readme_path.exists():
            logging.error("Readme not found")
            raise ValueError("Readme not found")

        if not self.readme_path.is_file():
            logging.error("Readme is not a file")
            raise ValueError("Readme is not a file")

        self.env.filters["age"] = self._age_filter

        logging.info("Creating custom readme...")

        template = self.env.from_string(
            self.readme_path.read_text(encoding="utf-8")
        )

        logging.info("Sorting followers by contributions and username...")
        self.followers.sort(
            key=lambda user: (
                -user.get_total_contributions(),
                user.get_username(),
            )
        )

        logging.info("Generating leaderboard array...")
        followers_contributions = [
            (
                position + 1,
                user.get_username(),
                user.url,
                user.get_total_contributions(),
            )
            for position, user in enumerate(self.followers)
            if position + 1 < 11
        ]

        logging.info("Generating AI prompt...")
        json_prompt = json.dumps(
            {
                "followers": [
                    {
                        "position": position + 1,
                        "username": user.get_username(),
                        "bio": user.bio,
                        "contributions": user.get_total_contributions(),
                        "recent_activity_repos": [
                            asdict(repo)
                            for repo in user.repositoriesContributedTo.nodes
                        ],
                    }
                    for position, user in enumerate(self.followers)
                    if user.get_total_contributions() > 0 and position < 11
                ],
            }
        )

        logging.info("Generating AI review...")
        ai_response = self.ai.generate_review(json_prompt, self.viewer)

        logging.info("Rendering custom readme...")
        self.rendered_readme = template.render(
            gh_name=self.viewer.get_username(),
            last_update=datetime.now(timezone.utc).strftime(
                "%Y-%m-%d at %H:%M:%S UTC %z"
            ),
            total_contributions=sum(
                [user.get_total_contributions() for user in self.followers]
            ),
            followers=followers_contributions,
            ai_review=ai_response,
        )

    def save(self, output: Path | str) -> None:
        """
        Save the custom readme to a file.

        Parameters
        ----------
        output : Path | str
            The path or name of the file to save the generated output to.
        """
        if isinstance(output, str):
            output = Path(output)

        if output.is_dir():
            output = output / "output.md"

        output = output.absolute()

        output.parent.mkdir(parents=True, exist_ok=True)
        output.touch(exist_ok=True)

        logging.info("Saving custom readme...")

        with output.open("w", encoding="utf-8") as f:
            f.write(self.rendered_readme)

    def _age_filter(self, value):
        past_date = datetime.strptime(value, "%Y-%m-%d")
        now = datetime.now()

        age = (
            now.year
            - past_date.year
            - ((now.month, now.day) < (past_date.month, past_date.day))
        )

        return age

    def __repr__(self) -> str:
        return (
            f"CustomReadme(readme_path={self.readme_path!r},"
            f"rendered_readme={self.rendered_readme!r}, "
            f"env={self.env!r}"
            f"viewer={self.viewer!r}, "
            f"followers={self.followers!r})"
        )
