import requests
import svgwrite
import os
from datetime import datetime

def calculate_uptime(start_date):
    current_date = datetime.now()
    delta = current_date - start_date
    years = delta.days // 365
    remaining_days = delta.days % 365
    months = remaining_days // 30
    remaining_days = remaining_days % 30
    weeks = remaining_days // 7
    days = remaining_days % 7
    uptime = f"{years} years, {months} months, {weeks} weeks, {days} days"
    return uptime

start_date = datetime(2008, 3, 8)
uptime = calculate_uptime(start_date)
print(uptime)

TOKEN = os.getenv('GH_PRIVATE_TOKEN')
OWNER = os.getenv('GH_OWNER')

headers = {
    'Authorization': f'token {TOKEN}',
    'Accept': 'application/vnd.github.v3+json'
}

def get_repositories(owner):
    url = f'https://api.github.com/users/{owner}/repos'
    repos = []
    page = 1

    while True:
        while True:
            response = requests.get(url, headers=headers, params={'per_page': 100, 'page': page})
            if response.status_code == 200:
                break
            print(f"Error fetching repositories: {response.status_code} - {response.json()}. Retrying...")

        data = response.json()
        if not data:
            break

        repos.extend(data)
        page += 1

    return repos

def get_commit_stats(owner, repo_name):
    url = f'https://api.github.com/repos/{owner}/{repo_name}/stats/contributors'

    while True:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.json()
        print(f"Error fetching commit stats for {repo_name}: {response.status_code} - {response.json()}. Retrying...")

repositories = get_repositories(OWNER)
total_repos = len(repositories)
total_commits = 0
total_additions = 0
total_deletions = 0
total_lines_of_code = 0

print(f"Total Repositories: {total_repos}")

for repo in repositories:
    repo_name = repo['name']
    commit_stats = get_commit_stats(OWNER, repo_name)

    if commit_stats is None:
        continue

    for contributor in commit_stats:
        total_commits += sum(week['c'] for week in contributor['weeks'])
        total_additions += sum(week['a'] for week in contributor['weeks'])
        total_deletions += sum(week['d'] for week in contributor['weeks'])

total_lines_of_code = total_additions + total_deletions
total_commits = f"{total_commits:,}"
total_additions = f"{total_additions:,}"
total_deletions = f"{total_deletions:,}"
total_lines_of_code = f"{total_lines_of_code:,}"

print(f"Total Commits: {total_commits}")
print(f"Additions: {total_additions}")
print(f"Deletions: {total_deletions}")
print(f"Lines of Code: {total_lines_of_code}")


def create_terminal_svg(output_file, title, body_content):
    dwg = svgwrite.Drawing(output_file, profile='tiny', size=(600, 400))

    dwg.add(dwg.rect(insert=(0, 0), size=('100%', '100%'), fill='#1E1E1E', rx=10, ry=10))
    dwg.add(dwg.rect(insert=(0, 0), size=('100%', '40'), fill='#2E2E2E', rx=10, ry=10))

    button_colors = ['#FF5F56', '#FFBD2E', '#27C93F']
    for i, color in enumerate(button_colors):
        dwg.add(dwg.circle(center=(20 + i * 20, 20), r=6, fill=color))

    title_x_position = 300
    dwg.add(dwg.text(title, insert=(title_x_position, 25), fill='#C0C0C0', font_size='14px', font_family='Menlo, Monaco, Consolas, "Courier New", monospace', text_anchor='middle'))

    dwg.add(dwg.rect(insert=(0, 40), size=('100%', '360'), fill='none', rx=10, ry=10)) 

    lines = body_content.split('\n')
    y_position = 60

    for line in lines:

        if "Last login" in line or "shaileshsaravanan@Github ~ %" in line:
            dwg.add(dwg.text(line, insert=(10, y_position), fill='#C0C0C0', font_size='12px', font_family='Menlo, Monaco, Consolas, "Courier New", monospace'))

        elif any(key in line for key in ['OS:', 'Uptime:', 'Host:', 'Kernel:', 'IDE:', 'Languages.Programming:', 'Languages.Computer:', 'Repos:', 'Commits:', 'Email:', 'LinkedIn:', 'Instagram:']):
            label, value = line.split(': ', 1)

            label_text = dwg.text(label + ':', insert=(10, y_position), fill='#d29c3f', font_size='12px', font_family='Menlo, Monaco, Consolas, "Courier New", monospace')
            dwg.add(label_text)

            label_width = len(label + ':') * 8
            value_text = dwg.text(value.strip(), insert=(10 + label_width, y_position), fill='#9fc0dc', font_size='12px', font_family='Menlo, Monaco, Consolas, "Courier New", monospace')
            dwg.add(value_text)

        elif 'Lines of Code:' in line:
            parts = line.split(': ')[1] 
            total, changes = parts.split(' (') 
            changes = changes[:-1] 

            label = 'Lines of Code:'
            label_text = dwg.text(label, insert=(10, y_position), fill='#d29c3f', font_size='12px', font_family='Menlo, Monaco, Consolas, "Courier New", monospace')
            dwg.add(label_text)

            label_width = len(label) * 8 
            total_text = dwg.text(total.strip(), insert=(10 + label_width, y_position), fill='#9fc0dc', font_size='12px', font_family='Menlo, Monaco, Consolas, "Courier New", monospace')
            dwg.add(total_text)

            open_bracket_text = dwg.text(' (', insert=(10 + label_width + len(total.strip()) * 8 + 10, y_position), fill='#C0C0C0', font_size='12px', font_family='Menlo, Monaco, Consolas, "Courier New", monospace')
            dwg.add(open_bracket_text)

            positive, negative = changes.split(', ')
            
            pos_text = dwg.text(f'{positive.strip()}', insert=(10 + label_width + len(total.strip()) * 8 + 10 + 10, y_position), fill='#4dcb6b', font_size='12px', font_family='Menlo, Monaco, Consolas, "Courier New", monospace')
            dwg.add(pos_text)

            comma_text = dwg.text(', ', insert=(10 + label_width + len(total.strip()) * 8 + 10 + len(positive.strip()) * 8 + 10, y_position), fill='#C0C0C0', font_size='12px', font_family='Menlo, Monaco, Consolas, "Courier New", monospace')
            dwg.add(comma_text)

            neg_text = dwg.text(f'{negative.strip()}', insert=(10 + label_width + len(total.strip()) * 8 + 10 + len(positive.strip()) * 8 + 10 + len(', ') * 8, y_position), fill='#dc0534', font_size='12px', font_family='Menlo, Monaco, Consolas, "Courier New", monospace')
            dwg.add(neg_text)

            close_bracket_text = dwg.text(')', insert=(10 + label_width + len(total.strip()) * 8 + 10 + len(positive.strip()) * 8 + 10 + len(', ') * 8 + len(negative.strip()) * 8 + 5, y_position), fill='#C0C0C0', font_size='12px', font_family='Menlo, Monaco, Consolas, "Courier New", monospace')
            dwg.add(close_bracket_text)

        elif '@Contact' in line:
            dwg.add(dwg.text(line, insert=(10, y_position), fill='#C0C0C0', font_size='12px', font_family='Menlo, Monaco, Consolas, "Courier New", monospace'))
        else:
            dwg.add(dwg.text(line, insert=(10, y_position), fill='#9fc0dc', font_size='12px', font_family='Menlo, Monaco, Consolas, "Courier New", monospace'))

        y_position += 15  

    dwg.save()

output_file = 'terminal.svg'
title = '@shaileshsaravanan -- -zsh -- 80x24'
body_content = f"""Last login: Sat Oct  5 17:17:29 on console
shaileshsaravanan@Github ~ % 
OS: Macintosh, iOS
Uptime: {uptime}
Host: Bangalore, India
Kernel: 11th Grade
IDE: Visual Studio Code

Languages.Programming: Python, Javascript, C++
Languages.Computer: HTML, CSS, JSON, XML, YAML, Markdown

Repos: {total_repos}
Commits: {total_commits}
Lines of Code: {total_lines_of_code} ({total_additions}++, {total_deletions}--)

shaileshsaravanan@Contact ~ % 
Email: shaileshsaravanan385@gmail.com
LinkedIn: linkedin.com/in/notshailesh
Instagram: @ssh_shailesh
"""

create_terminal_svg(output_file, title, body_content)