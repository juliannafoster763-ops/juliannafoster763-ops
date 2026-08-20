#!/usr/bin/env python3
"""Fetch real GitHub stats for the profile card. Writes stats.json.
Uses GITHUB_TOKEN if present (in Actions); works unauthenticated too."""
import json, os, time, urllib.request

USER = 'juliannafoster763-ops'
TOKEN = os.environ.get('GITHUB_TOKEN', '')

def api(path):
    req = urllib.request.Request('https://api.github.com' + path)
    req.add_header('Accept', 'application/vnd.github+json')
    if TOKEN:
        req.add_header('Authorization', 'Bearer ' + TOKEN)
    with urllib.request.urlopen(req) as r:
        return r.status, json.load(r)

def api_ok(path, retries=1):
    for _ in range(retries):
        try:
            st, data = api(path)
            if st == 200:
                return data
        except Exception as e:
            print('warn:', path, e)
        time.sleep(3)
    return None

# previous values as fallback
try:
    stats = json.load(open('stats.json'))
except Exception:
    stats = {'repos': 0, 'contributed': 0, 'commits': 0, 'stars': 0,
             'followers': 0, 'loc_add': 0, 'loc_del': 0}

user = api_ok('/users/' + USER)
if user:
    stats['followers'] = user['followers']

repos = api_ok(f'/users/{USER}/repos?per_page=100&type=owner') or []
own = [r for r in repos if not r['fork']]
stats['repos'] = len(repos)
stats['stars'] = sum(r['stargazers_count'] for r in repos)

# repos contributed to (beyond own) via recent events, best-effort
contributed = set()
events = api_ok(f'/users/{USER}/events/public?per_page=100') or []
for ev in events:
    if ev.get('type') == 'PushEvent':
        name = ev['repo']['name']
        if not name.startswith(USER + '/'):
            contributed.add(name)
stats['contributed'] = max(stats.get('contributed', 0), len(contributed))

# commits + lines of code across own repos via stats/contributors
total_commits, add, dele, pending = 0, 0, 0, False
for r in own:
    data = None
    for attempt in range(4):          # endpoint returns 202 while computing
        try:
            st, data = api(f"/repos/{r['full_name']}/stats/contributors")
            if st == 200:
                break
        except Exception as e:
            print('warn:', r['name'], e)
        time.sleep(4)
        data = None
    if not isinstance(data, list):
        pending = True
        continue
    for c in data:
        if c.get('author') and c['author']['login'].lower() == USER.lower():
            total_commits += c['total']
            for wk in c['weeks']:
                add += wk['a']
                dele += wk['d']

if not pending or total_commits > 0:
    stats['commits'] = total_commits
    stats['loc_add'] = add
    stats['loc_del'] = dele

json.dump(stats, open('stats.json', 'w'), indent=1)
print(json.dumps(stats))
