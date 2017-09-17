# -*- coding: utf-8 -*-

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
# Python script to Create Metadata
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
import optparse
import pandas
import sys

# Method to get all attributes, data types and description of a table
def get_attribute_and_type(
    table_list,
    cur
    ):

    metadata_obj = {}
    metadata_list = []

    for table_name in table_list:
        cur.execute("SELECT column_name, data_type FROM information_schema.columns WHERE table_name ='{table_name}';".format(
            table_name=table_name
        ))
        for attribute_type in cur.fetchall():
            metadata_obj = {
                "table_name" : table_name,
                "attribute" : attribute_type['column_name'],
                "data_type" : attribute_type['data_type'],
                "description" : 'none'
            }
            metadata_list.append(metadata_obj)

    return metadata_list

# Create metadata table
def create_metadata(
    cur
    ):

    cur.execute(
    """
    CREATE TABLE "metadata". "tmeta_global"(
    id_metadata SERIAL PRIMARY KEY,
    table_name VARCHAR(100),
    attribute VARCHAR(100),
    data_type VARCHAR(100),
    description TEXT
    );
    """
    )
    conn.commit()

# Drop metadata table
def drop_metadata(
    cur
    ):
    cur.execute("DROP TABLE IF EXISTS  metadata.tmeta_global;")
    conn.commit()

# Method to insert all information into metadata table
def insert_metadata_to_table(
        cur,
        metadata_list
):
    for element in metadata_list:
        querry =  """INSERT INTO metadata.tmeta_global (table_name, attribute, data_type, description)
        VALUES
        ('{table_name}','{attribute}','{data_type}','{description}');
        """.format(
            table_name=element['table_name'],
            attribute=element['attribute'],
            data_type=element['data_type'],
            description=element['description'].replace("'","''")
        )

        cur.execute(querry)
        conn.commit()

# Add description values from Excel file
def add_description_to_list(
    metadata_list,
    path_excel_file
):



    # Open Excel file
    excel_open = pandas.read_excel(path_excel_file)

    FORMAT = ['Nom attribut', 'Description','Table']
    df_selected = excel_open[FORMAT].values

    # Compare attribute name from database with attribute name of Excel file, if match: get description from Excel file
    for metadata_obj in metadata_list:
        for attribute in df_selected:
            if metadata_obj['attribute'] == attribute[0] and metadata_obj['table_name'] == attribute[2]:
                metadata_obj.update(
                    {
                        'description' : attribute[1]
                    }
                )

    return metadata_list




if __name__ == '__main__':

    # Managing arguments to start the script
    parser = optparse.OptionParser(description='Import metadata from Excel file')
    parser.add_option('-f', '--excel-path',dest="excel_path", help='Path of the RAW Excel file')

    opts, args = parser.parse_args()
    path_excel_file = opts.excel_path


    # Check if excel path is valid
    try:
        with open(path_excel_file) as file:
            pass
    except IOError as e:
        print("Unable to open file, probably wrong path")
        sys.exit(2)


    # Connection to PostgreSQL database
    db = "soussol"

    table_list = []

    conn = psycopg2.connect(dbname=db, user="postgres", password="123", host="127.0.0.1")
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)


    # Drop metadata table and reconnection to database
    drop_metadata(cur=cur)

    conn = psycopg2.connect(dbname=db, user="postgres", password="123", host="127.0.0.1")
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    print("Metadata Schema + Tables dropped")

    # Create empty metadata table
    create_metadata(cur=cur)
    print("Metadata Schema Created")


    # Get all information from data tables tdata and trel
    cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema LIKE 'ssol%' AND table_name  NOT LIKE 'tval%';")

    # Analyze and format result and create list metadata
    # Get a list of distinct table name
    for table_array in cur.fetchall():
        for table_name in table_array:
            table_list.append(table_name)

    # Get list of all attributes with table name, attribute, data type (description set value to 'none')
    metadata_list = get_attribute_and_type(
        table_list=table_list,
        cur=cur
    )

    # Add description value to metadata_list
    metadata_list = add_description_to_list(
        metadata_list=metadata_list,
        path_excel_file=path_excel_file
    )


    # Insert all information in table tmetadata_global
    insert_metadata_to_table(
        cur=cur,
        metadata_list=metadata_list
    )

    print("Metadata table has been filled")






