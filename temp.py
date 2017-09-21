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
