import json
import os
import urllib
import urllib.request

import psycopg2
from tqdm import tqdm

# https://api.crossref.org/swagger-ui/index.html

# Replace with the DOI you want to query
# doi = "10.1037/0003-066X.59.1.29"

# Replace with the ISSN you want to query
# issn = "0102-311X"

def get_crossref_data(doi):
    base_url = "https://api.crossref.org/works/"
    url = base_url + doi

    try:
        with urllib.request.urlopen(url) as response:
            data = json.loads(response.read().decode())
            return data['message']
    except urllib.error.HTTPError as e:
        print(f"HTTP Error {e.code}: {e.reason}")
        return None
    except json.JSONDecodeError:
        print("Error decoding JSON response")
        return None

def get_crossref_journal(issn):
    base_url = "https://api.crossref.org/journals/"
    url = base_url + issn

    try:
        with urllib.request.urlopen(url) as response:
            data = json.loads(response.read().decode())
            return data['message']
    except urllib.error.HTTPError as e:
        print(f"HTTP Error {e.code}: {e.reason}")
        return None
    except json.JSONDecodeError:
        print("Error decoding JSON response")
        return None


def is_in_crossref_journal(issn):

    is_in = True if get_crossref_journal(issn) else False
    print(f"issn: {issn}, is in crossref: {is_in}")

    return is_in

def is_in_crossref(doi):

    is_in = True if get_crossref_data(doi) else False
    print(f"doi: {doi}, is in crossref: {is_in}")

    return is_in


def check_for_crossref(schemaname, tablename, source_colname, target_colname, target_colname_time):

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

    # Establish a connection to the database
    conn = psycopg2.connect(**db_params)

    # Create a cursor object
    cur = conn.cursor()

    sql = f"alter table {schemaname}.{tablename} add column if not exists {target_colname} boolean"
    print(sql)
    cur.execute(sql)
    sql = f"alter table {schemaname}.{tablename} add column if not exists {target_colname_time} timestamp"
    print(sql)
    cur.execute(sql)

    sql = f"update {schemaname}.{tablename} set {target_colname}=null, {target_colname_time}=null"
    print(sql)
    cur.execute(sql)

    conn.commit()

    # get dois
    sql = f"select distinct({source_colname}) from {schemaname}.{tablename}"
    print(sql)
    cur.execute(sql)
    results = cur.fetchall()
    for res in tqdm(results):
        doi = res[0]
        print(doi)
        sql = f"update {schemaname}.{tablename} set {target_colname} = {is_in_crossref(doi)}, {target_colname_time}=CURRENT_TIMESTAMP where {source_colname}='{doi}'"
        print(sql)
        cur.execute(sql)
        conn.commit()


if __name__ == '__main__':

    schemaname = "project_rewi"
    # tablename = "jura_publisherdata_rabels"
    source_colname = "doi"
    target_colname = "is_in_crossref"
    target_colname_time = "found_in_crossref_timestamp"

    for tablename in ["jura_publisherdata_kj_items", "jura_publisherdata_kritv_items"]:
        check_for_crossref(schemaname, tablename, source_colname, target_colname, target_colname_time)

    # Journal example
    # print(get_crossref_journal("0102-311X"))
    # print(is_in_crossref_journal("0102-311X"))
    # print(is_in_crossref_journal("0102-3xxx"))
