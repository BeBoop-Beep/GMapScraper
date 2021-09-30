# Importing all libraries necessary
import pandas as pd
import re


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
        # Replacing values with | values for separation later.
        row = data_frame.loc[i, :]
        row = '|'.join(row[row.notnull()].astype(str))
        row = (row
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
        cols = ['Name']
        cols.extend(cols_tmp)

        dictionary = dict(zip(cols, txt))

        # Creating keys for Rating, Reviews and Speciality
        values = [dictionary.get('col1'), dictionary.get('col2'), dictionary.get('col3')]
        patterns = ['[0-9\.]+$', '[0-9]+[a-zA-Z\s]*$', '[a-zA-Z\s]+$']
        keys = ['Rating', 'Reviews', 'Speciality']

        # Replacing dictionary values col1, col2, col3 with the keys.
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
    # Saving that new data frame to the same Excel file.
    # Exit message to console.
    data_frame_new = pd.DataFrame(rows_dict_list)
    data_frame_new.to_excel('CT_MediSpas.xlsx', index=False)
    print('Data organization completed')

    # Not necessary at the moment but returning the new data frame object.
    return data_frame_new
