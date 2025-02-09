from pathlib import Path
from src.modules import User
from src.utils import (
    get_template_path,
    resolve_username,
    format_number,
    encode_image_from_url_to_data_image,
)
import xml.etree.ElementTree as ET
from textwrap import shorten


class Top3ContributorsGenerator:
    SVG_NS = {"svg": "http://www.w3.org/2000/svg"}

    def __init__(self, users: list[User] = []) -> None:
        self.tree = None
        self.users = users
        self.template_path = get_template_path("top3/top3.svg")
        self.need_users_template = get_template_path(
            "top3/need-followers-contributions.svg"
        )

    def create(self):
        if self.template_path is None:
            raise ValueError("No template found for top3 contributors generator")

        if (
            len(self.users) < 3
            or sum(
                [
                    user.contributionsCollection.contributionCalendar.totalContributions
                    for user in self.users
                ]
            )
            < 1
        ):
            self.tree = ET.parse(self.need_users_template)
            root = self.tree.getroot()

            element = root.find(".//*[@id='message']", self.SVG_NS)

            if element is not None:
                element.text = (
                    f"waiting for contributions from followers ({len(self.users)}/3)"
                )
            return

        self.users.sort(
            key=lambda x: (
                -x.contributionsCollection.contributionCalendar.totalContributions,
                resolve_username(x),
            )
        )

        top3_users = self.users[:3]

        self.tree = ET.parse(self.template_path)
        root = self.tree.getroot()

        users_contents = {
            "texts": {},
            "images": {},
        }

        for index, user in enumerate(top3_users):
            user_contributions = (
                user.contributionsCollection.contributionCalendar.totalContributions
            )

            users_contents["texts"].update(
                {
                    f"user_{index}_username": shorten(
                        resolve_username(user), width=19, placeholder="..."
                    ),
                    f"user_{index}_contributions": f"{format_number(user_contributions)} Ctr.",
                }
            )

            users_contents["images"].update(
                {
                    f"user_{index}_avatar": encode_image_from_url_to_data_image(
                        f"{user.avatarUrl}&size=128"
                    )
                }
            )

        for content_type in users_contents.keys():
            for key, value in users_contents[content_type].items():
                element = root.find(".//*[@id='{}']".format(key), self.SVG_NS)

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
        return f"Top3ContributorsGenerator(users={self.users!r}, template={self.template_path!r})"
