# Bitwarden to Keeper Migration Tool
<img src="https://raw.githubusercontent.com/namnamir/Bitwarden-to-Keeper/main/logo.png" align="center">

If you would like to migrate from Bitwarden, as a password manager, to Keeper, you can't use the built-in import feature of Keeper; it needs to be fixed. This tool helps you do it swiftly.

## How to use it?
1. Expert your passwords from **Bitwarden** in JSON format. You need to export shared passwords (in _collections_ related to the _organization_) separately. The output will be one `.json` file for personal items and another `.json` file for each organization if any organization is set up.
2. Modify the script and change the lines according to the exported items from **Bitwarden** and the `.json` file name you like to save the output. You can also define whether you like to log the password history; the default is `False`.
```python
# Exported Bitwarden file paths
bitwarden_file_normal = 'bitwarden.json'
bitwarden_file_organization = 'bitwarden_org.json'

# Output path of the Keeper file
keeper_file = 'keeper.json'

# A flag to write the password change history into the note section
password_history_log = False
```
Also, if you'd like to make the Bitwarden shared folders sharable on Keeper, please change the following `False` values to `True`.
```python
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
```
3. Run the script. The output will be a file called `keeper.json`.
4. log in to your Keeper account and import this file.

## Features
- Transfer all passwords, secret notes, and bank cards.
- Transfer all URLs.
- Transfer MFA one-time passwords (TOPT).
- Keep items in their original folders.
- Transfer the creation date of secure notes.
- Error handling and statistics.

### To-Dos
- Transfer custom fields.
