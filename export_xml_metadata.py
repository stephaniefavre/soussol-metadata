# Version: 	1.0.0
# Author: 	Stephanie Favre
#			University of Geneva
#			Institute for Environmental Sciences/enviroSPACE
#			Uni Carl-Vogt
#			66 boulevard Carl-Vogt
#			CH - 1205 Genève
#			http://www.unige.ch/envirospace/people/stephanie-favre/
#			http://www.unige.ch/envirospace
#
# Python script to export PostgreSQL metadata to XML format
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.


import psycopg2.extras
import xml.etree.cElementTree as ET
from xml.dom import minidom
import os


# Method to get a list of all attributes with table name, attribute, data type, description (theme set value to 'none')
def get_attribute_type_desc(
        cur
):
    metadata_list = []
    querry = """
        SELECT table_name, attribute, data_type, description FROM metadata.tmeta_global
    """
    cur.execute(querry)

    for elements in cur.fetchall():
        metadata_obj = {
            "theme": 'none',
            "table_name": elements['table_name'],
            "attribute": elements['attribute'],
            "data_type": elements['data_type'],
            "description": elements['description']
        }
        metadata_list.append(metadata_obj)

    return metadata_list


# Method to add theme values to metadata list from table tmeta_theme
def add_theme_to_metadatalist(
    cur,
    metadata_list
    ):

    for metadata_obj in metadata_list :
        theme_list = []
        querry = """
            SELECT theme FROM metadata.tmeta_theme where table_name='{table_name}'
        """.format(table_name=metadata_obj['table_name'])
        cur.execute(querry)
        for themes in cur.fetchall():
            for element in themes:
                theme_list.append(element)

        metadata_obj.update(
                 {
                     "theme" : theme_list
                 }
        )

    return metadata_list

# Method to get distinct themes from database
def get_themes(
    cur
    ):
    theme_list = []
    querry = """
        SELECT DISTINCT ON (theme)theme FROM metadata.tmeta_theme 
    """
    cur.execute(querry)

    for themes in cur.fetchall():
        for element in themes:
            theme_list.append(element)

    return theme_list

# Method to get a human readable XML file
def prettify(elem):

    rough_string = ET.tostring(elem, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="  ")


if __name__ == '__main__':

    xml_folder = './xml/'

    # Check if XML folder exists, otherwise create it
    if os.path.exists(xml_folder) == False:
        os.mkdir(xml_folder)


    # Drop existing XML files
    os.system("rm -f ./xml/*.xml")

    # Connect to PostgreSQL database
    db = "soussol"

    conn = psycopg2.connect(dbname=db, user="postgres", password="123", host="127.0.0.1")
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    # Get all elements (theme, table name, attribute, data type, description) from the metadata table -> Create metadata list
    metadata_list = []
    metadata_list = get_attribute_type_desc(cur=cur
    )

    # Add theme value related to the metadata list
    metadata_list = add_theme_to_metadatalist(
        cur=cur,
        metadata_list=metadata_list
    )


    # Get list of all themes
    theme_list = get_themes(cur)

    # Iterate on each theme
    # Start implementing XML parts
    for theme_element in theme_list:
        metadata = ET.Element('metadata')

        theme = ET.SubElement(metadata, 'theme')
        theme.text = theme_element

        # Get all tables related to the selected theme
        querry = """
        SELECT table_name FROM metadata.tmeta_theme  WHERE theme='{theme_element}'
        """.format(
            theme_element=theme_element
        )
        cur.execute(querry)

        tables_list = []
        for elements in cur.fetchall():
            for table in elements:
                tables_list.append(table)

        # Create object 'Table name'
        for table in tables_list:
            table_name = ET.SubElement(theme, 'table_name')
            table_name.text = table


            # Get all attributes related to the selected table
            querry = """
                SELECT table_name,attribute,data_type,description  FROM metadata.tmeta_global WHERE table_name='{table}'
            """.format(
                table=table
            )

            # Get data type and description for each attribute
            cur.execute(querry)
            for elements in cur.fetchall():

                attribute = ET.SubElement(table_name, 'attribute')
                attribute.text = elements['attribute']

                data_type = ET.SubElement(attribute, 'data_type')
                data_type.text = elements['data_type']

                description = ET.SubElement(attribute, 'description')
                description.text = elements['description']

        # Create an XML file for each theme
        with open('xml/{theme_element}.xml'.format(
                theme_element=theme_element), 'w') as file:
            file.write(prettify(metadata))

        print("XML File created for {theme_element}".format(
            theme_element=theme_element
        ))

    print("All metadata assembled in XML Object")



