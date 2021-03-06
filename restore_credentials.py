"""Batch Update Data Source Credentials Script Example

This script provides an example framework for allowing the batch updating/
restoration of credentials for data sources on Tableau Server. This script
utilizes Tableau's REST API to create a log of all data sources on a given
instance of Tableau Server and then utilize that log to push updated
credentials back to the Tableau Server instance.

Instructions:
    Please refer to the README document for instructions on running this
    script.
    
Attributes:
    API_VERSION (int/float): The API version for your Tableau Server
        instance. You can find this value by looking up your Tableau Server
        version at:
        https://onlinehelp.tableau.com/current/api/rest_api/en-us/REST/rest_api_concepts_versions.htm to set the correct version
    TABLEAU_SERVER_URL (str): The base URL (i.e. with no added path) for
        your Tableau Server. DO NOT use any trailing slashes! As an example,
        if you access your server by visiting http://tableau.acme.com/, the
        value should be http://tableau.acme.com (notice no trailing slash).
    USERNAME (str): The username that you will utilize to conduct all API
        transactions. This will need to be a Server Administrator user as
        many of these operations will require admin-level access.
    PASSWORD (str): The password corresponding to the username provided. If
        you are using Active Directory to authenticate, you'll need to
        modify this script accordingly. The Tableau REST API documentation
        provides details on authentication methods.
"""

import requests
import csv
import os

API_VERSION = os.environ.get('TS_API_VERSION') # check https://onlinehelp.tableau.com/current/api/rest_api/en-us/REST/rest_api_concepts_versions.htm to set the correct version
TABLEAU_SERVER_URL = os.environ.get('TS_ADDRESS')
USERNAME = os.environ.get('TS_USERNAME')
PASSWORD = os.environ.get('TS_PASSWORD')

def get_request_headers(token = None):
    """Build common request headers for use in REST API requests

    Args:
        token (str, optional): When provided, this includes the token in the
            `X-Tableau-Auth` header.

    Returns:
        dict: A dictionary containing key/value pairs where the
            key represents the header name and the value represents the value
            of the header.
    """
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
    if token is not None:
        headers['X-Tableau-Auth'] = token
    return headers

def logout(token):
    """Logout of the Tableau REST API

    This process will invalidate the token generated by Tableau Server's REST
    API. While logging out shouldn't be required, this step provides added
    security.

    Args:
        token (str): The token generated by Tableau Servers's REST API to
            provide access to the API

    Returns:
        None
    """
    url = '{}/api/{}/auth/signout'.format(TABLEAU_SERVER_URL, API_VERSION)
    r = requests.post(url, headers=get_request_headers(token))

def get_api_token(username, password, contentUrl = None):
    """Get an API token to allow access to Tableau Server's REST API

    In order to interact with Tableau Server's REST API, a user must first
    authenticate and obtain a token generated by Tableau Server. A login
    is specific to a single site on Tableau Server, regardless of
    permissions (i.e. a Server Admin may only authenticate to a single site
    despite having access to all sites via the UI). Logging into multiple
    sites will require generating tokens for each specific site. The
    expiry of tokens generated by Tableau Server can be set/updated via
    TSM, check the following link for more info:
    https://onlinehelp.tableau.com/current/server-linux/en-us/cli_configuration-set_tsm.htm

    Args:
        username (str): The username to login to Tableau Server.
        password (str): The password to login to Tableau Server.
        contentUrl (str, optional): The content URL specific to the site
            that you want to login to. For more info on Tableau's
            content URL's, check:
            https://onlinehelp.tableau.com/current/api/rest_api/en-us/REST/rest_api_concepts_auth.htm

    Returns:
        str: A string containing the token generated by Tableau Server
    """
    payload = {
        'credentials': {
            'name': username,
            'password': password,
            'site': {
                'contentUrl': ''
            }
        }
    }
    if contentUrl is not None:
        payload['credentials']['site']['contentUrl'] = contentUrl
    url = '{}/api/{}/auth/signin'.format(TABLEAU_SERVER_URL, API_VERSION)
    r = requests.post(url, headers=get_request_headers(), json=payload);
    return r.json()['credentials']['token']

def get_sites(token):
    """Get all sites that the user has access to.

    This function queries Tableau Server for all sites which the user, as
    identified by the token, has permission to access. The results of that
    request are transformed into a dictionary.

    Args:
        token (str): The authentication token from Tableau Server

    Returns:
        dict: A dictionary object where keys are the ID of the site and 
            values are dictionary objects containing the site name and 
            content URL.

    """
    sites_url = '{}/api/{}/sites'.format(TABLEAU_SERVER_URL, API_VERSION)
    r = requests.get(sites_url, headers=get_request_headers(token))
    return {
        site['id']: {
            'name': site['name'],
            'contentUrl': site['contentUrl']
         } for site in r.json()['sites']['site']
    }

def build_datasources_csv(save_as='datasources.csv'):
    """Build a CSV file of all datasources available on Tableau Server

    This function should be used as the first step in the process of batch
    updating data source credentials. This process will iterate through all
    sites where the user has permissions on Tableau Server and will build a
    CSV file containing information about the site, data source, and connection.
    This file can then be updated to include username and password information
    for those data sources that need to be updated.
    
    Keyword Arguments:
        save_as {str} -- Full path, including filename, where the output CSV
            should be saved. (default: {'datasources.csv'})
    """
    token = get_api_token(USERNAME, PASSWORD)
    print('Getting all sites on Tableau Server [{}]...'.format(TABLEAU_SERVER_URL))
    sites = get_sites(token)
    logout(token)
    datasources = []
    for site_id, site_data in sites.items():
        print('Getting datasources for {} site...'.format(site_data['name']))
        site_token = get_api_token(USERNAME, PASSWORD, site_data['contentUrl'])
        datasources_url = '{}/api/{}/sites/{}/datasources'.format(TABLEAU_SERVER_URL, API_VERSION, site_id)
        r = requests.get(datasources_url, headers=get_request_headers(site_token))
        if 'datasource' in r.json()['datasources']:
            sources = r.json()['datasources']['datasource']
            for source in sources:
                connections_url = '{}/api/{}/sites/{}/datasources/{}/connections'.format(TABLEAU_SERVER_URL, API_VERSION, site_id, source['id'])
                r = requests.get(connections_url, headers=get_request_headers(site_token))
                if 'connection' in r.json()['connections']:
                    connections = r.json()['connections']['connection']
                    for connection in connections:
                        datasources.append({
                            'site_id': site_id,
                            'site_name': site_data['name'],
                            'site_content_url': site_data['contentUrl'],
                            'datasource_id': source['id'],
                            'datasource_name': source['name'],
                            'datasource_content_url': source['contentUrl'],
                            'connection_id': connection['id'],
                            'connection_type': connection['type'],
                            'connection_server_address': connection['serverAddress'],
                            'connection_server_port': connection['serverPort'],
                            'connection_username': connection['userName'],
                            'updated_username': None,
                            'updated_password': None
                        })
        logout(site_token)
    print('Writing CSV...')
    with open(save_as, 'w') as output_csv:
        writer = csv.DictWriter(
            output_csv, 
            fieldnames=[
                'site_id', 
                'site_name', 
                'site_content_url', 
                'datasource_id', 
                'datasource_name', 
                'datasource_content_url',
                'connection_id',
                'connection_type',
                'connection_server_address',
                'connection_server_port',
                'connection_username',
                'updated_username',
                'updated_password'
            ]
        )
        writer.writeheader()
        writer.writerows(datasources)
        print('Wrote {} datasources to {}'.format(len(datasources), save_as))

def update_datasources_from_csv(path_to_csv):
    """Use an input CSV to batch update data source credentials on Tableau Server.

    This function expects a CSV that is formatted based on the process in the
    `build_datasources_csv` function. Please use that function to first generate a CSV,
    make any necessary updates to that CSV, then execute this function to push those
    updates to Tableau Server.
    
    Arguments:
        path_to_csv {str} -- The full path, including the filename, to the location of
            the CSV file used in the update process.
    
    Raises:
        ValueError: If an updated username value is not present in any CSV row, raise
            an error.
        ValueError: If an updated password value is not present in any CSV row, raise
            an error.
    """
    updates = {}
    with open(path_to_csv, 'r') as input_csv:
        reader = csv.DictReader(input_csv)
        print('Collecting data from CSV [{}]...'.format(path_to_csv))
        for row in reader:
            if len(row['updated_username']) == 0 or row['updated_username'] is None:
                raise ValueError('Updated username must be provided, even if you are not changing the value.')
            if len(row['updated_password']) == 0 or row['updated_password'] is None:
                raise ValueError('Updated password must be provided, even if you are not changing the value.')
            if row['site_content_url'] not in updates:
                updates[row['site_content_url']] = {
                    'site_id': row['site_id'],
                    'site_name': row['site_name'],
                    'datasources': {}
                }
            if row['datasource_id'] not in updates[row['site_content_url']]['datasources']:
                updates[row['site_content_url']]['datasources'][row['datasource_id']] = {
                    'datasource_name': row['datasource_name'],
                    'connections': []
                }
            updates[row['site_content_url']]['datasources'][row['datasource_id']]['connections'].append({
                'connection_id': row['connection_id'],
                'username': row['updated_username'],
                'password': row['updated_password']
            })
    for site_content_url, site_data in updates.items():
        print((
            '\nUpdating connections for site {}\n'
            '-------------------------------------------------'
        ).format(site_data['site_name']))
        update_token = get_api_token(USERNAME, PASSWORD, site_content_url)
        for datasource_id, datasource_data in site_data['datasources'].items():
            for connection in datasource_data['connections']:
                update_url = '{}/api/{}/sites/{}/datasources/{}/connections/{}'.format(TABLEAU_SERVER_URL, API_VERSION, site_data['site_id'], datasource_id, connection['connection_id'])
                payload = {
                    'connection': {
                        'userName': connection['username'],
                        'password': connection['password'],
                        'embedPassword': True
                    }
                }
                r = requests.put(update_url, headers=get_request_headers(update_token), json=payload)
                message = 'Updated data source {}.\nUsername: {} | Password: {}'.format(
                    datasource_data['datasource_name'],
                    connection['username'],
                    connection['password'][0] + '...' + connection['password'][-1]    
                )
                if 'connection' not in r.json():
                    message = 'ERROR: Error while updating {} on site {}:\n{}'.format(
                        datasource_data['datasource_name'],
                        site_data['site_name'],
                        r.json()
                    )
                print(message)

# Uncomment this line to build a CSV from your Tableau Server data sources
# build_datasources_csv()

# Uncomment this line to use the CSV you built above to push new credentials to Tableau Server
# update_datasources_from_csv('datasources.csv')