import requests
import json

if __name__ == '__main__':
    vendors = [
        'joeriabbo',
        'joeri-abbo',
    ]

    packages = []
    packages_processed = {}

    for vendor in vendors:
        packages_list = requests.get('https://packagist.org/packages/list.json?vendor=' + vendor).json().get(
            'packageNames')
        if packages_list:
            for package in packages_list:
                packages.append(package)

    if packages:
        print('Found {0} packages to fetch'.format(len(packages)))
        for package in packages:
            print('Fetching package {0}'.format(package))
            package_data = requests.get('https://packagist.org/packages/' + package + '.json').json().get('package')

            packages_processed[package] = {
                'name': package_data.get('name'),
                'description': package_data.get('description'),
                'downloads': package_data.get('downloads').get('total'),
                'url': 'https://packagist.org/packages/' + package_data.get('name'),
                'github_url': package_data.get('repository'),
                'versions': list(package_data.get('versions').keys())
            }
    else:
        print('No packages found')
        exit(1)

    with open('../data/packages.json', 'w') as fp:
        json.dump(packages_processed, fp)

    print('Done')
