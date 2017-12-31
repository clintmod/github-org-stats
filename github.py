import base64
import json
from operator import itemgetter
import os
from os import path
import re
import sys
import urllib2

username = os.environ['GITHUB_USERNAME']
password = os.environ['GITHUB_PASSWORD']


def main():
    if len(sys.argv) < 1:
        raise ValueError('expected argument to be github org')
    fetch_all(sys.argv[1])


def fetch_all(org_name):
    init_dirs(org_name)
    org = get_org(org_name)
    repos = get_repos(org['login'])
    repos = sorted(repos, key=itemgetter('pushed_at'), reverse=True)
    users = {}
    for repo in repos:
        repo['stats'] = get_contributor_stats_for_repo(org_name, repo['name'])
        for stat in repo['stats']:
            login = stat['author']['login']
            if login not in users:
                users[login] = get_user(login)
    return org, repos, users


def init_dirs(org):
    if not path.exists('./data/users'):
        os.makedirs('./data/users')
    if not path.exists('./data/orgs/' + org + '/stats/'):
        os.makedirs('./data/orgs/' + org + '/stats/')


def get_repos(org, repos=None, page_number=1):
    file_path = './data/orgs/' + org + '/repos.json'
    if not repos and path.exists(file_path):
        with open(file_path, 'r') as f:
            repos = json.loads(f.read())
        print 'returning repos from disk at: ' + file_path
        return repos
    url = 'https://api.github.com/orgs/' + \
        org + '/repos?page=' + str(page_number)
    request = get_request(url)
    try:
        print 'requesting ' + url
        stream = urllib2.urlopen(request)
        repos = json.load(stream)
        response_header = stream.info()
        # if we have a Link header
        if 'Link' in response_header:
            print response_header['Link']
            next_link = response_header['Link'].split(',')[0]
            if 'rel="next"' in next_link:
                next_page_number = re.search('page=(\\d*)', next_link).group(1)
                repos += get_repos(org, repos, next_page_number)
        with open(file_path, 'w') as f:
            f.write(to_json(repos))
    except urllib2.HTTPError, e:
        print url, None, e.fp.read()
    return repos


def get_contributor_stats_for_repo(org, repo):
    file_path = './data/orgs/' + org + '/stats/' + repo + '.json'
    if path.exists(file_path):
        with open(file_path, 'r') as f:
            user = json.loads(f.read())
        print 'returning stats from disk at: ' + file_path
        return user
    print 'Fetching stats for repo ' + org + '/' + repo
    url = 'https://api.github.com/repos/' + org + '/' + repo + '/stats/contributors'
    request = get_request(url)
    try:
        stream = urllib2.urlopen(request)
        stats = json.load(stream)
        with open(file_path, 'w') as f:
            f.write(to_json(stats))
    except urllib2.HTTPError, e:
        print url, None, e.fp.read()
    return stats


def get_user(login):
    user = {}
    file_path = './data/users/' + login + '.json'
    if path.exists(file_path):
        with open(file_path, 'r') as f:
            user = json.loads(f.read())
        print 'returning user from disk at: ' + file_path
        return user
    print 'Fetching user ' + login
    url = 'https://api.github.com/users/' + login
    request = get_request(url)
    try:
        stream = urllib2.urlopen(request)
        user = json.load(stream)
        with open(file_path, 'w') as f:
            f.write(to_json(user))
        return user
    except urllib2.HTTPError, e:
        print url, None, e.fp.read()


def get_org(org):
    org_json = {}
    file_path = './data/orgs/' + org + '/org.json'
    if path.exists(file_path):
        with open(file_path, 'r') as f:
            org_json = json.loads(f.read())
        print 'returning org from disk at: ' + file_path
        return org_json
    print 'Fetching org ' + org
    url = 'https://api.github.com/orgs/' + org
    request = get_request(url)
    try:
        stream = urllib2.urlopen(request)
        org_json = json.load(stream)
        with open(file_path, 'w') as f:
            f.write(to_json(org_json))
        return org_json
    except urllib2.HTTPError, e:
        print url, None, e.fp.read()


def get_request(url):
    request = urllib2.Request(url)
    base64string = base64.b64encode('%s:%s' % (username, password))
    request.add_header('Authorization', 'Basic %s' % base64string)
    return request


def to_json(obj):
    return json.dumps(obj, sort_keys=True, indent=4, separators=(',', ': '))


if __name__ == '__main__':
    main()