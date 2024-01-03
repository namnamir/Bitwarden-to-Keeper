from datetime import datetime
import json
import os.path


# Bitwarden file paths
bitwarden_file_normal = 'bitwarden.json'
bitwarden_file_organization = 'bitwarden_org.json'

# Output path of the Keeper file
keeper_file = 'keeper.json'

# Datetime format in Bitwarden
bitwarden_datetime_format = '%Y-%m-%dT%H:%M:%S.%fZ'

# A dictionary to translate Bitwarden types to the Keeper ones
bitwarden_keeper_types = {
    # Numbers are for Bitwarden
    # Texts are for Keeper
    1: 'login',
    2: 'encryptedNotes',
    3: 'bankCard'
}

# Some variables to store data in
keeper = {
    'shared_folders': [],
    'records': []
}
bitwarden_folders = {}
bitwarden_collenctions = {}
counter = 0    # Count all items
counter_1 = 0  # Count items with type 1
counter_2 = 0  # Count items with type 2
counter_3 = 0  # Count items with type 3

# Open the Bitwarden JSON file and read items and folders
if os.path.isfile(bitwarden_file_normal):
    with open(bitwarden_file_normal, 'r', encoding='utf8') as bitwarden_json:
        bitwarden = json.load(bitwarden_json)
        bitwarden_items = bitwarden['items']
        # Convert Bitwarden folders in a format that can be used eaiser during the convert
        for folder in bitwarden['folders']:
            bitwarden_folders[folder['id']] = folder['name']
else:
    print(f"The file '{bitwarden_file_normal}' doesn't exist. Check it and try again.")

# If there is any collections, merge it with the original one
if os.path.isfile(bitwarden_file_organization):
    with open(bitwarden_file_organization, 'r', encoding='utf8') as bitwarden_org_json:
        bitwarden_org = json.load(bitwarden_org_json)
        bitwarden_items += bitwarden_org['items']
        # Convert Bitwarden collections in a format that can be used eaiser during the convert
        for collection in bitwarden_org['collections']:
            bitwarden_collenctions[collection['id']] = collection['name']
else:
    print(f"The file '{bitwarden_file_organization}' doesn't exist. Check it and try again.")

# Iterate over the items in bitwarden
for bitwarden_item in bitwarden_items:
    # If the Bitwarden item is a login
    if bitwarden_item['type'] == 1:
        # Get URIs/URLs from Bitwarden item
        url_1 = None
        urls = {}
        if 'uris' in bitwarden_item['login']:
            for i in range(0, len(bitwarden_item['login']['uris'])):
                if i == 0:
                    url_1 = bitwarden_item['login']['uris'][0]['uri']
                elif i >= 1:
                    urls[f'$url::{i+1}'] = bitwarden_item['login']['uris'][i]['uri']

        # Form the base JSON format of a login in Keeper
        keeper_item = {
            'title': bitwarden_item['name'].strip(),
            'notes': bitwarden_item['notes'].replace( '\u0010', '') if bitwarden_item['notes'] else '',
            '$type': 'login',
            'schema': [
                '$passkey::1',
                '$login::1',
                '$password::1',
                "$fileRef::1",
                '$url::1'
            ],
            'custom_fields': {
            },
            'login': bitwarden_item['login']['username'],
            'password': bitwarden_item['login']['password'],
            'login_url': url_1,
            'folders': []
        }

        # Add additional URLs to Keeper
        if urls:
            keeper_item['custom_fields'].update(urls)

        # If TOPT (MFA) is set in Bitwarden, add it to Keeper
        if bitwarden_item['login']['totp']:
            keeper_item['custom_fields'].update(
                {
                    '$oneTimeCode::1': bitwarden_item['login']['totp']
                }
            )
            keeper_item['schema'].append('$oneTimeCode::1')

        # Keep the record of password changes
        if bitwarden_item['passwordHistory']:
            keeper_item['notes'] += '\n----- Password History -----\n'
            for password in bitwarden_item['passwordHistory']:
                keeper_item['notes'] += f"{str(password['password'])}  --  {str(password['lastUsedDate'])}\n"

        # Count the number of items with the type 1
        counter_1 += 1

    # If the Bitwarden item is a secure note
    if bitwarden_item['type'] == 2:
        # Convert the UTC time (Bitwarden) to Epoch (Keeper)
        utc_creation_date = datetime.strptime(bitwarden_item['creationDate'], bitwarden_datetime_format)
        epoch_creation_date = (utc_creation_date - datetime(1970, 1, 1)).total_seconds()
        epoch_creation_date = int(str(int(epoch_creation_date)).ljust(13, '0'))

        # Form the base JSON format of a secure note in Keeper
        keeper_item = {
            'title': bitwarden_item['name'].strip(),
            'notes': None,
            '$type': 'encryptedNotes',
            'schema': [
                '$note::1',
                '$date::1',
            ],
            'custom_fields': {
                '$note::1': bitwarden_item['notes'].replace( '\u0010', '') if bitwarden_item['notes'] else '',
                '$date::1': epoch_creation_date
            },
            'folders': []
        }

        # Count the number of items with the type 2
        counter_2 += 1

    # If the Bitwarden item is a card
    if bitwarden_item['type'] == 3:
        # Form the base JSON format of a cards in Keeper
        keeper_item = {
            'title': bitwarden_item['name'].strip(),
            'notes': bitwarden_item['notes'].replace( '\u0010', '') if bitwarden_item['notes'] else '',
            '$type': 'bankCard',
            'schema': [
                '$paymentCard::1',
                '$text:cardholderName:1',
                '$addressRef::1',
                "$fileRef::1",
            ],
            'custom_fields': {
                '$paymentCard::1': {
                'cardNumber': bitwarden_item['card']['number'],
                'cardExpirationDate': f"{str(bitwarden_item['card']['expMonth']).zfill(2)}/{bitwarden_item['card']['expYear']}",
                'cardSecurityCode': bitwarden_item['card']['code']
                },
                '$text:cardholderName:1': bitwarden_item['card']['cardholderName'].strip() if bitwarden_item['card']['cardholderName'] else None,
                '$pinCode::1': None
            },
            'folders': []
        }

        # Count the number of items with the type 3
        counter_3 += 1

    # Add folders to Keeper
    if bitwarden_item['folderId']:
        keeper_item['folders'].append(
            {
                'folder': bitwarden_folders[bitwarden_item['folderId']].replace('/', '\\')
            }
        )

    # Add shared folders (collections) to Keeper
    if bitwarden_item['collectionIds']:
        for id in bitwarden_item['collectionIds']:
            keeper_item['folders'].append(
                {
                    'shared_folder': bitwarden_collenctions[id].replace('/', '\\'),
                    'can_edit': False,  # For security reasons
                    'can_share': False  # For security reasons
                }
            )

    # Add the new formed Keeper item into a dictionary
    keeper['records'].append(keeper_item)

    # Count the number of items
    counter += 1

    print(f"{counter:>5}/{len(bitwarden_items)}  ::  Item {keeper_item['title']}")

# Convert and write Keeper JSON object to file
with open(keeper_file, 'w', encoding='utf8') as outfile:
    json.dump(keeper, outfile, ensure_ascii=False, indent=4)

# Print the stats
print(f"""

 [+]┓ {counter} items are saved in the file {keeper_file}.
    ┣━━━ Logins       : {counter_1}
    ┣━━━ Secure Notes : {counter_2}
    ┣━━━ Cards        : {counter_3}
    ┗━━━ Shared Items : {len(bitwarden_org['items'])} of {counter}

""")
