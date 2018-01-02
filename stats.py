from datetime import datetime
from os import path
import sys
import logging
import github

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main():
    if len(sys.argv) < 1:
        raise ValueError('expected argument to be github org')
    flatten_stats(sys.argv[1], True)


def flatten_stats(org_name, refresh=False):
    flattened_json = ""
    file_path = './data/orgs/' + org_name + '/flattened_stats.json'
    if not refresh and path.exists(file_path):
        with open(file_path, 'r') as f:
            flattened_json = f.read()
        logger.info('returning stats from disk at: %s', file_path)
        return flattened_json
    org, repos, users = github.fetch_all(org_name, refresh)
    flattened = []
    for repo in repos:
        for stat in repo['stats']:
            login = stat['author']['login']
            user = users[login]
            for week in stat['weeks']:
                flattened.append(create_item(org, repo, user, week))
    flattened_json = github.to_json(flattened)
    with open(file_path, 'w') as f:
        f.write(flattened_json)
    logger.info('Wrote %s records to %s', str(len(flattened)), file_path)
    return flattened_json


def create_item(org, repo, user, week_info):
    date, week, month, year = parse_week_tstamp(week_info['w'])
    name = user['name']
    if not name:
        name = user['login']
    return {
        'Organization': org['login'],
        'Repository': repo['name'],
        'Commiter': name,
        'Date': date,
        'Week': week,
        'Month': month,
        'Year': year,
        'Added': week_info['a'],
        'Deleted': week_info['d'],
        'Commits': week_info['c'],
    }


def parse_week_tstamp(tstamp):
    dt = datetime.fromtimestamp(int(tstamp))
    date = dt.strftime('%Y-%m-%d')
    week = dt.strftime('%U')
    year = dt.strftime('%Y')
    month = dt.strftime('%m-%b')
    return date, week, month, year


if __name__ == '__main__':
    main()
