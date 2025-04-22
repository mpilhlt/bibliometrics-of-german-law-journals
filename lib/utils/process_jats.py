import datetime
import os
import xml.etree.ElementTree as ET
import zipfile

import psycopg2


def drop_and_create_tables(schema, author_table, item_table, cur):

    drop_sql1 = f'drop table if exists {schema}.{author_table}'
    drop_sql2 = f'drop table if exists {schema}.{item_table}'
    create_sql1 = f'create table {schema}.{author_table} (doi text, lastname text, firstname text);'
    create_sql2 = sql = f"""create table {schema}.{item_table} (doi text, title text, volume text, issue text, firstpage text, lastpage text, 
     pubyear int, pubmonth text, pubday text, issn text, publisher text, author_cnt int, 
     wos_id text, scopus_id text, openalex_id text)"""

    cur.execute(drop_sql1)
    cur.execute(drop_sql2)
    cur.execute(create_sql1)
    cur.execute(create_sql2)


def esc(str):
    return str.replace("'", "''") if str else None


def get_item_id(doi, bdb_schema, cur):
    
    query = f"""select item_id from {bdb_schema}.items where doi='{doi.lower()}'"""
    #print(query)
    cur.execute(query)
    #print('done')

    result = cur.fetchone()

    if result is not None:
        value = result[0]
    else:
        value = None

    return value


def get_wos_scopus_openalex(doi, cur, wos_bdb, scp_bdb, openalex_bdb):
    
    wos_id = get_item_id(doi, wos_bdb, cur)
    scp_id = get_item_id(doi, scp_bdb, cur)
    openalex_id = get_item_id(doi, openalex_bdb, cur) 
    
    return wos_id, scp_id, openalex_id


def JATS_To_postgresql_table(filename, schema, author_table, item_table, cur, wos_bdb, scp_bdb, oa_bdb):

    # Define the INSERT query
    sql_insert_authors = f"""insert into {schema}.{author_table} (doi, lastname, firstname) values (%s,%s,%s)"""

    sql_insert_items = f"""insert into {schema}.{item_table} (doi, title, volume, issue, 
    firstpage, lastpage, pubyear, pubmonth, 
    pubday, issn, publisher, author_cnt, wos_id, scopus_id, openalex_id) 
    values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"""


    # Parse the XML file
    tree = ET.parse(filename)
    root = tree.getroot()

    if root.find('./front/article-meta'): # there are also files with journal info only

        doi = root.find('./front/article-meta/article-id').text
        print(doi)
        #for child in root.find('front/article-meta/title-group'):
        #    print(child.tag)
        title =root.find('./front/article-meta/title-group/article-title').text
        #print(title)
        volume = root.find('./front/article-meta/volume').text
        #print(volume)
        issue = root.find('./front/article-meta/issue').text
        #print(issue)
        firstpage = root.find('./front/article-meta/fpage').text
        #print(firstpage)
        lastpage = root.find('./front/article-meta/lpage').text
        #print(lastpage)
        pubyear = root.find('./front/article-meta/pub-date/year').text
        #print(pubyear)
        pubmonth = root.find('./front/article-meta/pub-date/month').text
        #print(pubmonth)
        pubday = root.find('./front/article-meta/pub-date/day').text
        #print(pubday)
        issn = root.find('./front/journal-meta/issn').text
        #print(issn)
        publisher = root.find('./front/journal-meta/publisher/publisher-name').text
        #print(publisher)

        authors = root.findall('./front/article-meta/contrib-group/contrib')
        if authors:
            for author in authors:
                author_surname = author.find('./name/surname').text if author.find('./name/surname') is not None else None
                author_given = author.find('./name/given-names').text if author.find('./name/given-names') is not None else None

                #print(author_surname)
                #rint(author_given)

                cur.execute(sql_insert_authors, (doi.lower(), esc(author_surname), esc(author_given)))

        author_cnt = len(root.findall('./front/article-meta/contrib-group/contrib'))
        wos_id, scopus_id, openalex_id = get_wos_scopus_openalex(doi, cur, wos_bdb, scp_bdb, oa_bdb)

        # print(sql_insert_items, (doi.lower(), esc(title), volume, issue, firstpage, lastpage,
        #                                pubyear, pubmonth, pubday, issn, esc(publisher), author_cnt,
        #                                wos_id, scopus_id, openalex_id))
        cur.execute(sql_insert_items, (doi.lower(), esc(title), volume, issue, firstpage, lastpage,
                                       pubyear, pubmonth, pubday, issn, esc(publisher), author_cnt,
                                       wos_id, scopus_id, openalex_id))


if __name__ == '__main__':

    start = datetime.datetime.now()
    print(f'Start processing records: {start}')

    schema = 'fizcrimmert'
    #author_table = 'jura_publisherdata_kj_authors'
    #item_table = 'jura_publisherdata_kj_items'
    #author_table = 'jura_publisherdata_kritv_authors'
    #item_table = 'jura_publisherdata_kritv_items'
    author_table = 'jura_publisherdata_der_staat_authors'
    item_table = 'jura_publisherdata_der_staat_items'

    db_host = "biblio-p-db03.fiz-karlsruhe.de"
    db_port = 5432
    db_name = "kbprod"
    db_user = "kbprodadmin"
    db_password = os.environ['PG_PW_KBPRODADMIN']

    db_params = {
        "host": db_host,
        "database": db_name,
        "user": db_user,
        "password": db_password,
        "port": db_port
    }

    wos_bdb = 'wos_b_202404'
    scp_bdb = 'scp_b_202404'
    openalex_bdb = 'fiz_openalex_bdb_20240427'

    # Establish a connection to the database
    conn = psycopg2.connect(**db_params)

    # Create a cursor object
    cur = conn.cursor()

    drop_and_create_tables(schema, author_table, item_table, cur)

    #xml_file = "C:/Users/CHR/Documents/gitlab_projects/kb-bibliometry/staa.62.4.751.xml"
    # xml_file = "C:/Users/CHR/Desktop/jura_daten_von_den_publishern/Daten/Daten/KJ (1969-)/example2.xml"
    #JATS_To_postgresql_table(xml_file, schema, author_table, item_table, cur, wos_bdb, scp_bdb, openalex_bdb)

    zip_directory = 'C:/Users/CHR/Desktop/jura_daten_von_den_publishern/Daten/Daten/Der Staat (1962-)/Der_Staat_Vol.47.1-63.1'
    # zip_directory = 'C:/Users/CHR/Desktop/jura_daten_von_den_publishern/Daten/Daten/KJ (1969-)/KJ_JATS'
    # #zip_directory = 'C:/Users/CHR/Desktop/jura_daten_von_den_publishern/Daten/Daten/KritV (1859-)/KritV_JATS'
    for filename in os.listdir(zip_directory):
        if filename.endswith(".zip"):
            zip_path = os.path.join(zip_directory, filename)
            print('##########################')
            print(filename)
            print('--------------------------')
            # Open the ZIP file
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                # Iterate over files in the ZIP
                for file_info in zip_ref.infolist():
                    if file_info.filename.endswith(".xml"):
                        print(file_info.filename)
                        with zip_ref.open(file_info) as xml_file:
                            #filename = "C:/Users/CHR/Documents/gitlab_projects/kb-bibliometry/staa.62.4.751.xml"
                            #filename = "C:/Users/CHR/Desktop/jura_daten_von_den_publishern/Daten/Daten/KJ (1969-)/example2.xml"
                            JATS_To_postgresql_table(xml_file, schema, author_table, item_table, cur, wos_bdb, scp_bdb, openalex_bdb)

                conn.commit()

    conn.commit()
    if cur:
        cur.close()
    if conn:
        conn.close()
