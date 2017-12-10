# -*-coding:Latin-1 -*
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
import os
from jinja2 import Template,Environment,FileSystemLoader
import random
from datetime import date
import uuid
from time import gmtime, strftime


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





# Method to generate XML from Template
def iso19139_generator(attributes_list,
                       theme,
                       template_path):

    random_id = random.getrandbits(128)

    templateloader = FileSystemLoader(searchpath=template_path)
    templateenv = Environment(loader=templateloader,trim_blocks=True)
    TEMPLATE_FILE = "sitg_iso_19139.xml"
    template = templateenv.get_template(TEMPLATE_FILE)
    rendered = template.render(attributes_list=attributes_list,
                               theme=theme,
                               random_id=random_id,
                               today_date=date.today(),
                               today_date_time=strftime("%Y-%m-%dT%H:%M:%S", gmtime()),
                               uuid=uuid.uuid4(),
                               today_separate=strftime("%Y-%m-%d", gmtime())
    )
    return rendered


# Define Object Attribute (Description, name..)
class Attribute(object):
    def __init__(self, theme, name, table_name, data_type, description):
        self.theme = theme
        self.name = name
        self.table_name = table_name
        self.data_type = data_type
        self.description = description



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


    attributes_list = []

    # Get Theme List
    theme_list = get_themes(cur)

    for theme_element in theme_list:
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
                # Get all attributes related to the selected table
                querry = """
                    SELECT table_name,attribute,data_type,description  FROM metadata.tmeta_global WHERE table_name='{table}'
                """.format(
                    table=table
                )

                # Get data type and description for each attribute
                cur.execute(querry)
                for elements in cur.fetchall():
                    attributes_list.append(
                        Attribute(
                            theme=theme_element,
                            name=elements['attribute'],
                            table_name=table,
                            data_type=elements['data_type'],
                            description=elements['description']
                        )
                    )
        #Generate Template for each theme
        xml_generated = iso19139_generator(attributes_list=attributes_list,
                           theme=theme_element,
                           template_path='../source-files/templates/')

        # Create an XML file for each theme
        with open('xml/{theme_element}.xml'.format(
            theme_element=theme_element), 'w') as file:
            file.write(xml_generated)


        print("XML File created for {theme_element}".format(
            theme_element=theme_element
        ))

        print("All metadata assembled in XML Object")

