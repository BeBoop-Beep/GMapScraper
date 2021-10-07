# Importing all libraries necessary
import pandas as pd
import re
import numpy as np

# Global variables required for comparisons outside of parse_data() method.
domain_formatted = '^[w]{3}[.].+[.][a-zA-Z-]+'
phone_formatted = '^[2-9][0-9]{2}[-][0-9]{3}[-][0-9]{4}'
phone_10d = '^[2-9][0-9]{9}'


# Removing any left over data after that is after any '|' in data frame.
def split_function(value):
    val = value.split(sep='|', maxsplit=1)[0]
    return val


# Method used to attach www. to website names
def format_domain(domain):
    # Checking to see if the string domain matches the global pattern.
    match_domain_formatted = re.search(pattern=domain_formatted, string=domain)

    # If there was not a match, we change the website to the right format.
    if match_domain_formatted is None:
        # Not formatted (www.)
        domain = 'www.' + domain

    return domain


# Method used to reformat phone number to 000-000-0000.
def format_phone(phone):
    # Creating an element for the match of phone and proper format (phone_formatted).
    phone = str(phone)
    match_phone_formatted = re.search(pattern=phone_formatted, string=phone)

    # If the phone number is not in proper format then we enter if statement.
    if match_phone_formatted is None:
        # Creating a string of digits that only holds digits and no other elements.
        # Create match_10d element to see if the phone number has 10 digits in phone number.
        digits = str(''.join(c for c in phone if c.isdigit()))
        digits = digits.lstrip('0').lstrip('1')
        match_10d = re.search(pattern=phone_10d, string=digits)

        # Invalid phone number , not matching 10 valid digits.
        if match_10d is None:
            return None

        # Valid phone number and puts in proper format.
        else:
            digits = digits[0:3] + '-' + digits[3:6] + '-' + digits[6:10]
            return digits

    # Phone number already in right format, no changes required.
    else:
        return phone


# A method that cleans and organizes data scraped from google maps.
def parse_data():
    # Entrance message to console.
    # Placing Excel information from GMapScraper into a data frame object.
    print('Data organization started')
    data_frame = pd.read_excel("CT_MediSpas.xlsx")

    # A dictionary array created to hold the data being changed.
    rows_dict_list = []

    # For loop created to cycle through each row of data within data excel sheet.
    for i in range(0, len(data_frame)):

        # Going through 1 row at a time with all columns.
        # Joining each cell of the row into one string but separating with a '|'.
        # Replacing values with | values for easier separation later.
        row = data_frame.loc[i, :]
        row = '|'.join(row[row.notnull()].astype(str))

        # Changing values to make it easier to separate later.
        row = (row
               .replace('|', '|Name: ', 1)
               .replace('@', '|Address:')
               .replace('\n', '|col1: ', 1)
               .replace('\n', '|col2: ', 1)
               .replace('\n', '|col3: ', 1))

        # Splitting the string based off any value with | some words and a colon with a space.
        txt = re.split(pattern='[|][a-zA-Z0-9&\s]+[:][\s]', string=row)

        # The values that were parsed are taken into a list.
        cols_tmp = re.findall(pattern='[|][a-zA-Z0-9&\s]+[:][\s]', string=row)

        # Replacing values with nothing and removing any unnecessary spaces.
        cols_tmp = [col.replace(':', '').replace('|', '').rstrip(' ') for col in cols_tmp]

        # Creating column headers based on the cols_tmp entries.
        cols = ['google_maps_url']
        cols.extend(cols_tmp)

        # Mapping Column names to column data
        dictionary = dict(zip(cols, txt))

        # Creating keys for Rating, Reviews and Speciality
        values = [dictionary.get('col1'), dictionary.get('col2'), dictionary.get('col3')]
        patterns = ['[0-9\.]+$', '[0-9]+[a-zA-Z\s]*$', '[a-zA-Z\s]+$']
        keys = ['Rating', 'Reviews', 'Speciality']

        # Replacing dictionary values col1, col2, col3 and placing them in their respected keys.
        for j in [0, 1, 2]:  # Values
            for k in [0, 1, 2]:  # Patterns, Keys
                if values[j] is None:
                    break
                else:
                    match = re.search(pattern=patterns[k], string=values[j])

                    if match is not None:
                        old_key = 'col' + str(j + 1)
                        dictionary[keys[k]] = dictionary.pop(old_key)
                        break

        # Appending the new keys and values in the key headers to rows_dict_list
        rows_dict_list.append(dictionary)

    # Adding the updated data frame to a new data frame object.
    data_frame_new = pd.DataFrame(rows_dict_list)

    # Creating Phone, Address, and Website variables.
    ph = data_frame_new.Phone
    ad = data_frame_new.Address
    dm = data_frame_new.Website

    # Removing any unneeded, excess data in all rows from Phone and Address columns.
    data_frame_new.loc[:, 'Phone'] = ph[ph.notnull()].apply(split_function)
    data_frame_new.loc[:, 'Address'] = ad[ad.notnull()].apply(split_function)

    # Filter and format not null domains.
    data_frame_new['Website'] = dm[~dm.isna()].apply(format_domain)

    # Array created to sort websites later.
    inv_dom_exts = ['gov', 'org', 'edu']

    # Splitting domain name extensions and telling console how many different domain types there are.
    domain_names = data_frame_new.Website.str.rsplit(pat='.', n=1, expand=True)[[1]][1]
    print('\nDistribution of domain name extensions:')
    print(domain_names.value_counts().to_string())

    # Removing any of the invalid domain types and its corresponding data from data frame (the entire row).
    val_dom_rows = np.invert([x in inv_dom_exts for x in domain_names])
    l1 = len(data_frame)
    data_frame_new = data_frame_new[val_dom_rows].copy()
    l2 = len(data_frame_new)

    # Telling console how many rows were removed
    print('\nRemoved ' + str(l1 - l2) + ' row(s) for invalid domains.')

    # Calling method to reformat Phone numbers in Phone column of the new data frame.
    data_frame_new['Phone'] = ph[~ph.isna()].apply(format_phone)

    # Resetting the data frame indexes after cleaning/removal of certain indexes.
    data_frame_new.reset_index(drop=True, inplace=True)

    # Removing all unnecessary data columns before saving the data frame to the excel sheet.
    data_frame_new.drop(columns=['Health & safety', 'Plus code', 'Located in', 'Warning', 'Open now'], inplace=True)

    # Saving that new data frame to the same Excel file.
    # Exit message to console.
    data_frame_new.to_excel('CT_MediSpas.xlsx', index=False)
    print('Data organization completed')

    # Not necessary at the moment but returning the new data frame object.
    return data_frame_new
