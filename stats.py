from datetime import datetime
from os import path
import sys
import logging
import github

logger = logging.getLogger(__name__)

def main():
    if len(sys.argv) < 1:
        raise ValueError('expected argument to be github org')
    flatten_stats(sys.argv[1])


def flatten_stats(org_name):
    flattened_json = ""
    file_path = './data/orgs/' + org_name + '/flattened_stats.json'
    if path.exists(file_path):
        with open(file_path, 'r') as f:
            flattened_json = f.read()
        logger.info('returning stats from disk at: %s', file_path)
        return flattened_json
    org, repos, users = github.fetch_all(org_name)
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


def create_item(org, repo, user, week):
    week_date, month, year = parse_week_tstamp(week['w'])
    return {
        'Organization': org['login'],
        'Repository': repo['name'],
        'GithubId': user['login'],
        'Week': week_date,
        'Month': month,
        'Year': year,
        'Added': week['a'],
        'Deleted': week['d'],
        'Commits': week['c'],
    }


def parse_week_tstamp(tstamp):
    date = datetime.fromtimestamp(int(tstamp))
    week_string = date.strftime('%Y-%m-%d')
    year = date.strftime('%Y')
    month = date.strftime('%m-%b')
    return week_string, month, year


if __name__ == '__main__':
    main()
