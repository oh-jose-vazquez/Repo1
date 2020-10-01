"""
Script to deploy the tick files to Kapacitor.

Flow:

- Get all existing alerts in Kapacitor
- Get the list of all tick files in the repository
- Process each file as follow:
    - If the file exists in Kapacitor alerts then update the alert
    - If the file doesn't exist in Kapacitor alerts then create the alert
    - If exist in Kapacitor alerts but not in the repository then delete the alert
"""
import os
import datetime
import requests

DB_LINE = 'var db = '
SLACK_CHANNEL_LINE = 'var slackChannel = '
ASE_URL_LINE = 'var aseUrl ='
LS_URL_LINE = 'var lsUrl = '
MDM_URL_LINE = 'var mdmUrl = '
ASE = 'ASE'
LS = 'LS'
MDM = 'MDM'


def get_existing_alerts(url):
    """
    Get current alerts in Kapacitor
    """
    existing_alerts = set()
    try:
        req = requests.get(url + '/kapacitor/v1/tasks',
                           auth=get_credentials())
        req.raise_for_status()

        for task in req.json()['tasks']:
            existing_alerts.add(task['id'])

        return existing_alerts
    except requests.exceptions.HTTPError as err:
        raise SystemExit(err) from err


def get_credentials():
    """
    Get credentials for Kapacitor, they are defined in ENV VARS
    """
    if 'KAPACITOR_USER' not in os.environ or 'KAPACITOR_PASSWORD' not in os.environ:
        raise SystemExit('Undefined credentials for kapacitor')
    print(os.environ.get('KAPACITOR_USER'))
    print(os.environ.get('KAPACITOR_PASSWORD'))
    return (os.environ.get('KAPACITOR_USER'), os.environ.get('KAPACITOR_PASSWORD'))


def update_alert_content(file_path, db_name, slack_channel, urls):
    """
    Process the tick files and update the content based on the ENV VARS
    """
    with open(file_path) as reader:
        lines = reader.readlines()
        header_line = '//Deployed at ' + str(datetime.datetime.now()) + '\n\n'
        db_line = DB_LINE + "'{}'\n\n".format(db_name)
        slack_channel_line = SLACK_CHANNEL_LINE + \
            "'{}'\n\n".format(slack_channel)
        content = ''
        for line in lines:
            if DB_LINE not in line and SLACK_CHANNEL_LINE not in line:
                if line.startswith(ASE_URL_LINE):
                    content += ASE_URL_LINE + "'{}'\n\n".format(urls[ASE])
                elif line.startswith(LS_URL_LINE):
                    content += LS_URL_LINE + "'{}'\n\n".format(urls[LS])
                elif line.startswith(MDM_URL_LINE):
                    content += MDM_URL_LINE + "'{}'\n\n".format(urls[MDM])
                else:
                    content += line
        return header_line + db_line + slack_channel_line + content


def create_alert(url, alert__id, db_name, alert__content):
    """
    Create a new alert in Kapacitor
    """
    payload = get_payload(alert__id, db_name, alert__content)
    try:
        req = requests.post(url + '/kapacitor/v1/tasks', json=payload,
                            auth=get_credentials())
        req.raise_for_status()
        return 'CREATED'
    except requests.exceptions.HTTPError as err:
        return err.response.text


def update_alert(url, alert__id, db_name, alert__content):
    """
    Update an exisitng alert in Kapacitor
    """
    payload = get_payload(alert__id, db_name, alert__content)
    try:
        req = requests.patch(url + '/kapacitor/v1/tasks/' + alert_id, json=payload,
                             auth=get_credentials())
        req.raise_for_status()
        return 'UPDATED'
    except requests.exceptions.HTTPError as err:
        return err.response.text


def get_payload(alert__id, db_name, alert__content):
    """
    Payload for creating or updating alerts
    """
    return {
        'id': alert__id,
        'type': 'stream',
        'dbrps': [
            {
                'db': db_name,
                'rp': 'autogen'
            }
        ],
        'script': alert__content,
        'status': 'enabled'
    }


def delete_alert(url, alert__id):
    """
    Delete an alert from Kapacitor
    """
    try:
        req = requests.delete(url + '/kapacitor/v1/tasks/' + alert__id,
                              auth=get_credentials())
        req.raise_for_status()
        return 'DELETED'
    except requests.exceptions.HTTPError as err:
        return err.response.text


# Main Flow
if 'KAPACITOR_URL' not in os.environ:
    raise SystemExit('KAPACITOR_URL undefined')

if 'KAPACITOR_DB' not in os.environ:
    raise SystemExit('KAPACITOR_DB undefined')

if 'KAPACITOR_SLACK_CHANNEL' not in os.environ:
    raise SystemExit('KAPACITOR_SLACK_CHANNEL undefined')

if 'ASE_URL' not in os.environ:
    raise SystemExit('ASE_URL undefined')

if 'LS_URL' not in os.environ:
    raise SystemExit('LS_URL undefined')

if 'MDM_URL' not in os.environ:
    raise SystemExit('MDM_URL undefined')

kapacitor_url = os.environ.get('KAPACITOR_URL')
kapacitor_db = os.environ.get('KAPACITOR_DB')
kapacitor_slack_channel = os.environ.get('KAPACITOR_SLACK_CHANNEL')
ase_url = os.environ.get('ASE_URL')
ls_url = os.environ.get('LS_URL')
mdm_url = os.environ.get('MDM_URL')

print(kapacitor_url)
print(kapacitor_db)
print(kapacitor_slack_channel)
print(ase_url)
print(ls_url)
print(mdm_url)


app_urls = {
    ASE: ase_url,
    LS: ls_url,
    MDM: mdm_url
}

currentAlerts = get_existing_alerts(kapacitor_url)

PATH = '.'
for root, directory, files in os.walk(PATH):
    for file in files:
        if '.tick' in file:
            f_path = os.path.join(root, file)
            alert_id = file.replace('.tick', '')
            alert_content = update_alert_content(
                f_path, kapacitor_db, kapacitor_slack_channel, app_urls)
            if alert_id in currentAlerts:
                result = update_alert(
                    kapacitor_url, alert_id, kapacitor_db, alert_content)
                currentAlerts.remove(alert_id)
            else:
                result = create_alert(
                    kapacitor_url, alert_id, kapacitor_db, alert_content)
            status = alert_id.ljust(50, '.')
            print(status + '[' + result.replace('\n', '') + ']')


for existingAlert in currentAlerts:
    result = delete_alert(kapacitor_url, existingAlert)
    status = existingAlert.ljust(50, '.')
    print(status + '[' + result.replace('\n', '') + ']')
