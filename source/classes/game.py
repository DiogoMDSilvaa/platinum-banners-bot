from dataclasses import dataclass
from enum import Enum, auto
from PIL import Image, ImageOps, ImageDraw, ImageFont

from .platinum import Platinum


FONT_PATH = "assets/PixelifySans-VariableFont_wght.ttf"
PLATINUM_ICON = "assets/platinum_trophy.png"
PS3_ICON = "assets/ps3_icon.png"
PS4_ICON = "assets/ps4_icon.png"
PS5_ICON = "assets/ps5_icon.png"


class Console(Enum):
    """Represents the possible consoles"""

    PS3 = auto()
    PS4 = auto()
    PS5 = auto()


@dataclass
class Game:
    """Represents a general playstation game"""

    name: str

    console: Console

    banner: str

    platinum: Platinum = None

    def create_platinum_banner(self) -> Image:
        """Creates the platinum banner for this game"""

        if self.platinum is None:
            raise ValueError("This game doesn't have a platinum trophy yet.")

        banner = Image.open(self.banner).convert("RGBA")
        initial_height = banner.size[1]

        #################### Styling ####################
        border_size = 30
        border_color = (0, 48, 135, 255)
        overlay_opacity = 0.7
        overlay_color = (128, 128, 128, round(overlay_opacity * 256))
        overlay_width = round(0.2 * banner.size[0])
        normal_font = ImageFont.truetype(FONT_PATH, 40)
        title_font = ImageFont.truetype(FONT_PATH, 60)

        #################### Border ####################
        banner = ImageOps.expand(banner, border=border_size, fill=border_color)

        #################### Drawing Canvas ####################
        overlays = Image.new("RGBA", banner.size, (255, 255, 255, 0))
        draw = ImageDraw.Draw(overlays)

        #################### Overlays ####################

        draw.rectangle(  # Left one
            [
                (border_size, border_size),
                (border_size + overlay_width, banner.size[1] - border_size),
            ],
            fill=overlay_color,
        )
        draw.rectangle(  # Right one
            [
                (banner.size[0] - overlay_width - border_size, border_size),
                (banner.size[0] - border_size, banner.size[1] - border_size),
            ],
            fill=overlay_color,
        )

        #################### Plat Stats ####################
        top_left_overlay_corner = (
            banner.size[0] - border_size - overlay_width,
            border_size,
        )
        padding = 20
        y_offset = initial_height / 3

        first_x = top_left_overlay_corner[0] + padding
        second_x = top_left_overlay_corner[0] + overlay_width - padding

        first_y = top_left_overlay_corner[1] + y_offset - y_offset / 2
        second_y = top_left_overlay_corner[1] + y_offset * 2 - y_offset / 2
        third_y = top_left_overlay_corner[1] + y_offset * 3 - y_offset / 2

        draw.text(
            (
                first_x,
                first_y,
            ),
            "Difficulty:",
            font=normal_font,
            fill="white",
            anchor="lm",
        )
        draw.text(
            (
                second_x,
                first_y,
            ),
            f"{self.platinum.difficulty}/10",
            font=normal_font,
            fill="white",
            anchor="rm",
        )
        draw.text(
            (
                first_x,
                second_y,
            ),
            "Playthroughs:",
            font=normal_font,
            fill="white",
            anchor="lm",
        )
        draw.text(
            (
                second_x,
                second_y,
            ),
            str(self.platinum.playthroughs),
            font=normal_font,
            fill="white",
            anchor="rm",
        )
        draw.text(
            (
                first_x,
                third_y,
            ),
            "Hours:",
            font=normal_font,
            fill="white",
            anchor="lm",
        )
        draw.text(
            (
                second_x,
                third_y,
            ),
            str(self.platinum.hours),
            font=normal_font,
            fill="white",
            anchor="rm",
        )

        #################### Icons and Plat Date ####################
        middle_x = border_size + overlay_width / 2
        padding = 20

        draw.text(
            (
                middle_x,
                second_y,
            ),
            self.platinum.date_earned.strftime("%d  %b  %Y"),
            font=normal_font,
            fill="white",
            anchor="mm",
        )

        match self.console:
            case Console.PS3:
                console_image = PS3_ICON
            case Console.PS4:
                console_image = PS4_ICON
            case Console.PS5:
                console_image = PS5_ICON

        console_image = Image.open(console_image).convert("RGBA")

        platinum_image = Image.open(PLATINUM_ICON).convert("RGBA")
        platinum_image = platinum_image.resize(
            [round(dim * 0.35) for dim in platinum_image.size]
        )

        #################### Title ####################

        max_width = 1 * overlay_width

        # If the game title fits in one line use the bigger font,
        # otherwise, change to multiline format with the normal font size
        if draw.textlength(self.name, title_font) <= max_width:
            draw.text(
                (
                    middle_x,
                    third_y,
                ),
                self.name,
                font=title_font,
                fill="white",
                anchor="mm",
                stroke_width=1,
                align="center",
            )

        else:

            # Add the maximum possible of words per line that don't exceed `max_width`
            lines = []
            words = self.name.split()
            i = 0
            while i < len(words):

                # Add the words to the current line until limit is exceeded
                current_line = ""
                while (
                    i < len(words)
                    and draw.textlength(current_line, normal_font) <= max_width
                ):
                    current_line += words[i] + " "
                    i += 1

                # Remove last added word and space if last added word exceeded space
                if not draw.textlength(current_line, normal_font) <= max_width:
                    i -= 1
                    current_line = current_line[: -1 - len(words[i])]

                lines.append(current_line[:-1])  # Remove last empty space

            draw.text(
                (
                    middle_x,
                    third_y,
                ),
                "\n".join(lines),
                font=normal_font,
                fill="white",
                anchor="mm",
                stroke_width=1,
                align="center",
            )

        #################### Final composition ####################

        banner = Image.alpha_composite(banner, overlays)

        banner.paste(
            platinum_image,
            (
                round((middle_x / 2) - platinum_image.size[0] / 2),
                round(first_y - platinum_image.size[1] / 2 + padding),
            ),
            platinum_image,
        )
        banner.paste(
            console_image,
            (
                round((middle_x * 1.5) - console_image.size[0] / 2),
                round(first_y - console_image.size[1] / 2 + padding),
            ),
            console_image,
        )

        return banner
