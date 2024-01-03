# Bitwarden to Keeper Migration Tool
<img src="https://raw.githubusercontent.com/namnamir/Bitwarden-to-Keeper/main/logo.png" align="center">

If you would like to migrate from Bitwarden, as a password manager, to Keeper, you can't use the built-in import feature of Keeper; it needs to be fixed. This tool helps you do it swiftly.

## How to use it?
1. Expert your passwords from **Bitwarden** in JSON format. You need to export shared passwords (in _collections_ related to the _organization_) separately. The output will be one `.json` file for personal items and another `.json` file for each organization if any organization is set up.
2. Modify the script and change the lines according to the exported items from **Bitwarden**.
```python
# Bitwarden file paths
bitwarden_file_normal = 'bitwarden.json'
bitwarden_file_organization = 'bitwarden_org.json'
```
3. Run the script. The output will be a file called `keeper.json`.
4. log in to your Keeper account and import this file.
