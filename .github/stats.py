import json
import os
import urllib.request

USER = "gbpardave"

QUERY = """
query($login: String!) {
  user(login: $login) {
    pullRequests { totalCount }
    issues { totalCount }
    contributionsCollection { totalCommitContributions }
  }
}
"""


def graphql(variables):
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": QUERY, "variables": variables}).encode(),
        headers={"Authorization": f"Bearer {os.environ['GITHUB_TOKEN']}"},
    )
    with urllib.request.urlopen(req) as r:
        return json.load(r)["data"]["user"]


def fetch():
    user = graphql({"login": USER})
    return {
        "commits": user["contributionsCollection"]["totalCommitContributions"],
        "pulls": user["pullRequests"]["totalCount"],
        "issues": user["issues"]["totalCount"],
    }


def render(counts):
    width = 320
    char_w = 7.2
    widths = [len(f"{n} {label}") * char_w for label, n in counts.items()]
    gap = (width - sum(widths)) / (len(widths) + 1)
    x, row = gap, ""
    y = 30
    for (label, n), w in zip(counts.items(), widths):
        row += (
            f'<text xml:space="preserve" x="{x + w / 2:.1f}" y="{y}" text-anchor="middle">'
            f'{n}<tspan class="dim"> {label}</tspan></text>'
        )
        x += w + gap
    height = y + 14
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
<style>
  text {{ font: 12px Iosevka, ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; fill: #57606a; }}
  .dim {{ fill: #8c959f; }}
  @media (prefers-color-scheme: dark) {{
    text {{ fill: #c9d1d9; }}
    .dim {{ fill: #6e7681; }}
  }}
</style>
{row}
</svg>
"""


if __name__ == "__main__":
    with open("stats.svg", "w") as f:
        f.write(render(fetch()))
