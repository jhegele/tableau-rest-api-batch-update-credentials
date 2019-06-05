# Tableau REST API - Batch Update Credentials Example

A sample script that can be used to batch update data source credentials for Tableau Server.

*This example was prepared for a client by John Hegele, a Sales Consultant on the Tableau GSI Team. If you need help with the Tableau REST API, please check the [REST API documentation](https://onlinehelp.tableau.com/current/api/rest_api/en-us/REST/rest_api_ref.htm) first.*

## A Word of Caution

Before we go any further, I want to reiterate that this example was built specifically to assist a Tableau Client. This script is not meant to serve as a generalizable method for batch restoring credentials via Tableau's REST API. In fact, I've hardcoded a number of options here that may be highly undesirable in your specific use case. One of the big ones is that this script will _always_ embed credentials when it updates a datasource. Depending on your needs and security requirements that behavior may be against policy. Please keep in mind that this serves **only** as a high level example and that you'll need to adapt this and perhaps even rewrite it in its entirety to work based on your specific business needs.

## How to Use This Example

This example script requires several steps. Use the following process to update your credentials:

### Providing Tableau Server Info & Login Details

In order to interact with your Tableau Server, you'll need to provide some basic information about the server along with a set of user credentials that will be used to login via the REST API. There are a couple of approaches that can be used to provide this information, one of which is *far* superior to the other, but I'll document both here for the sake of completeness.

Keep in mind that Tableau Server's REST API respects the same permissioning model used by the frontend GUI. So, if you need to batch update a bunch of credentials across a large number of sites, it may be easiest to use the login information of a Server Admin.

#### Loading Via Environment Variables

By default, this script looks for four different environment variables:
- **TS_API_VERSION**: The API Version for your Tableau Server. Check the section below, titled, *Tableau REST API Versions* for more details on this value.
- **TS_ADDRESS**: The URL for your Tableau Server. **DO NOT** use a trailing slash for this value! So, instead of `https://tableau.acme.com/`, use `https://tableau.acme.com`.
- **TS_USERNAME**: The username that will be used to login to Tableau Server.
- **TS_PASSWORD**: The corresponding password that will be used to login to Tableau Server.

I **strongly** advise using this approach to supply this information as it helps avoid a situation where you have hardcoded these values into the script and share it with someone else without removing the credentials. That would be bad since, in that scenario, the recipient of the script has the URL for your Tableau Server along with your username and password and, you guessed it, that would enable this person to login to Tableau as you! So, while I will discuss hardcoding these values below, please try to avoid that approach at all costs.

#### Hardcoding

**DISCLAIMER**: If you just read the previous section, you're going to get this warning *one more time*. Yes, I realize that I sound like a broken record here, but I cannot stress enough how important it is to understand the ramifications of hardcoding these values into this script. Will hardcoding the server and login info work? Absolutely! Is it a good idea. Absolutely not! If at all possible, please use environment variables, as documented above to load this information. Imagine a scenario where you hardcode these values into your script. Six months pass by then the new guy Jim needs to use the script to batch update some credentials. You, being the super thoughtful colleague you are, offer to just send your script over to Jim to help him out. Guess what? Now Jim has the URL for your Tableau Server along with your username and password.

But, there may be situations where environment variables aren't workable so, in those cases, here's how to avoid using environment variables and, instead, supply this information in the script itself.

Near the top of the script, find these lines:

```python
API_VERSION = os.environ.get('TS_API_VERSION')
TABLEAU_SERVER_URL = os.environ.get('TS_ADDRESS')
USERNAME = os.environ.get('TS_USERNAME')
PASSWORD = os.environ.get('TS_PASSWORD')
```

Replace the portion after the `=` sign with the hardcoded values. The result should look something like this:

```python
API_VERSION = 3.4
TABLEAU_SERVER_URL = 'https://tableau.acme.com' # DO NOT use a trailing slash here!
USERNAME = 'my_username'
PASSWORD = 'my_password'
```

### Running the Batch Update Process

1) Run the `build_datasoures_as_csv()` function to generate a CSV file containing all datasources for those sites that the user has access. You can, optionally, supply a path to output the resultant CSV. If no path is supplied, the script will generate a CSV named `datasources.csv` in the same directory where the script is run.
2) Open the CSV generated in step 1. Each line in this CSV represents a single datasource on your Tableau Server. **DO NOT** change any of the values that are pre-filled into this CSV! For those lines where you *do not* need to update credentials, simply delete them from the CSV. For any lines where you want to update credentials, you **MUST** supply both an updated username and password. If, for example, you only wish to update the password, you would need to copy the username into the `updated_username` field, then provide the new password in the `updated_password` field.
3) Once you have made all necessary adjustments in the CSV, run the `update_datasources_from_csv()` function supplying the path to your updated and saved CSV from Step 2. This process will push your updated credentials to Tableau Server. **IMPORTANT NOTE**: Because this is a sample script, it is coded to embed credentials in Tableau Server. If you do not wish to have credentials embedded, you'll need to update the `update_datasources_from_csv()` function.

## Tableau REST API Versions

The Tableau REST API is versioned independently of Tableau Server itself. This means that, if you are running Tableau Server 2019.1, your API version number is `3.4` and **not** `2019.1`! Thankfully, all of this is nicely documented [here](https://onlinehelp.tableau.com/current/api/rest_api/en-us/REST/rest_api_concepts_versions.htm) so you should have no problem finding your API version.

At the time of writing, the most recent release of Tableau Server is 2019.2. For convenience, here are the API versions from 2019.2 back to 10.0. If your Tableau Server version is not listed here, click the link above to find it.

| Tableau Server Version | REST API Version |
| :--------------------: | :--------------: |
|         2019.2         |       3.4        |
|         2019.1         |       3.3        |
|         2018.3         |       3.2        |
|         2018.2         |       3.1        |
|         2018.1         |       3.0        |
|          10.5          |       2.8        |
|          10.4          |       2.7        |
|          10.3          |       2.6        |
|          10.2          |       2.5        |
|          10.1          |       2.4        |
|          10.0          |       2.3        |

## Support and Other Information

While this code is the property of Tableau, it was not written nor released through Tableau's standard product release cycle and was written specifically to assist a single Tableau client. Thus, this code should not be considered to be "officially supported" by Tableau and any requests for support or assistance should, instead, be made directly to John Hegele.