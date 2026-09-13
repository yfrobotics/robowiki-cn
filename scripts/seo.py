"""Derive page descriptions from rendered prose; front matter takes precedence."""

from html.parser import HTMLParser
import re


class ProseParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.paragraphs = []
        self.parts = None
        self.skip = 0

    def handle_starttag(self, tag, attrs):
        if tag in {"script", "style", "pre"}:
            self.skip += 1
        if tag == "p":
            self.parts = []
            if "admonition-title" in dict(attrs).get("class", "").split():
                self.parts = None

    def handle_endtag(self, tag):
        if tag == "p" and self.parts is not None:
            prose = re.sub(r"\s+", " ", "".join(self.parts)).strip()
            if len(prose) >= 30:
                self.paragraphs.append(prose)
            self.parts = None
        if tag in {"script", "style", "pre"}:
            self.skip = max(0, self.skip - 1)

    def handle_data(self, data):
        if self.parts is not None and not self.skip:
            self.parts.append(data)


def on_page_content(html, page, config, files):
    if not page.meta.get("description"):
        parser = ProseParser()
        parser.feed(html)
        description = next(iter(parser.paragraphs), f"{page.title}：{config['site_description']}")
        page.meta["description"] = (
            description if len(description) <= 160 else description[:159].rstrip() + "…"
        )
    return html
