from datetime import datetime
import sys
import github


def main():
    if len(sys.argv) < 1:
        raise ValueError('expected argument to be github org')
    org, repos, users = github.fetch_all(sys.argv[1])
    flatten_stats(org, repos, users)


def flatten_stats(org, repos, users):
    file_path = './data/orgs/'+org['login']+'/flattened_stats.json'
    flattened = []
    for repo in repos:
        for stat in repo['stats']:
            login = stat['author']['login']
            user = users[login]
            for week in stat['weeks']:
                flattened.append(create_item(org, repo, user, week))
    with open(file_path, 'w') as f:
        f.write(github.to_json(flattened))
    print 'Wrote ' + str(len(flattened)) + ' records to ' + file_path


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
