import json
import xml.etree.ElementTree as ET
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from textwrap import shorten

from jinja2 import Environment

from src.modules.user import User
from src.modules.viewer import Viewer
from src.services.gemini_service import GeminiService
from src.utils import (
    encode_image_from_url_to_data_image,
    format_number,
    get_template_path,
)


class Top3ContributorsGenerator:
    SVG_NS = {"svg": "http://www.w3.org/2000/svg"}

    def __init__(self, followers: list[User] | None = None) -> None:
        self.tree = None
        self.followers = followers
        self.template_path = get_template_path("top3/top3.svg")
        self.need_followers_template = get_template_path(
            "top3/need-followers-contributions.svg"
        )

    def create(self):
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
                element.text = (
                    f"waiting for contributions from followers "
                    f"({len(self.followers)}/3)"
                )
            return

        self.followers.sort(
            key=lambda user: (
                -user.get_total_contributions(),
                user.get_username(),
            )
        )

        top3_followers = self.followers[:3]

        self.tree = ET.parse(self.template_path)
        root = self.tree.getroot()

        followers_contents = {
            "texts": {},
            "images": {},
        }

        for index, user in enumerate(top3_followers):
            user_contributions = user.get_total_contributions()

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

    def save(self, output: Path | str):
        if self.template_path is None or self.tree is None:
            return

        if isinstance(output, str):
            output = Path(output)

        if output.is_dir():
            output = output / "output.svg"

        output = output.absolute()

        output.parent.mkdir(parents=True, exist_ok=True)
        output.touch(exist_ok=True)

        ET.register_namespace("", "http://www.w3.org/2000/svg")

        self.tree.write(output, encoding="utf-8", xml_declaration=True)

    def __repr__(self) -> str:
        return (
            f"Top3ContributorsGenerator(followers={self.followers!r},"
            f"template={self.template_path!r})"
        )


class CustomReadme:
    def __init__(
        self,
        readme_path: Path | str,
        viewer: Viewer,
        followers: list[User],
        gemini_service: GeminiService,
    ) -> None:
        self.readme_path = readme_path
        self.env = Environment(
            trim_blocks=True,
            lstrip_blocks=True,
        )
        self.rendered_readme: str = ""
        self.viewer = viewer
        self.followers = followers
        self.gemini_service = gemini_service

    def create(self) -> None:
        if self.readme_path is None:
            raise ValueError("No readme path provided for custom readme")

        if isinstance(self.readme_path, str):
            self.readme_path = Path(self.readme_path)

        if not self.readme_path.exists():
            raise ValueError("Readme not found")

        if not self.readme_path.is_file():
            raise ValueError("Readme is not a file")

        self.env.filters["age"] = self._age_filter

        template = self.env.from_string(
            self.readme_path.read_text(encoding="utf-8")
        )

        self.followers.sort(
            key=lambda user: (
                -user.get_total_contributions(),
                user.get_username(),
            )
        )

        followers_contributions = [
            (
                position,
                user.get_username(),
                user.url,
                user.get_total_contributions(),
            )
            for position, user in enumerate(self.followers)
        ]

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

        ai_response = self.gemini_service.generate_ranking_review(json_prompt)

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

    def save(self, output: Path | str):
        if isinstance(output, str):
            output = Path(output)

        if output.is_dir():
            output = output / "output.md"

        output = output.absolute()

        output.parent.mkdir(parents=True, exist_ok=True)
        output.touch(exist_ok=True)

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
