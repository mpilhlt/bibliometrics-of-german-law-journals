import requests
import time
import os
import pandas as pd
from tqdm.notebook import tqdm
import textwrap
import regex as re


# written by ChatGPT-4
def run_query(query):
    url = 'https://query.wikidata.org/sparql'
    headers = {
        'User-Agent': 'CoolBot/0.0 (https://example.org/coolbot/; coolbot@example.org)'
    }

    for attempt in range(4):  # Try up to four times (initial + 3 retries)
        try:
            response = requests.get(url, params={'format': 'json', 'query': query}, headers=headers, timeout=10)
            response.raise_for_status()  # This will raise an HTTPError if the HTTP request returned an unsuccessful status code
            return response.json()

        except requests.exceptions.HTTPError as http_err:
            raise Exception(f"HTTP error occurred: {http_err}") from None
        except requests.exceptions.Timeout:
            if attempt == 3:  # Give up after 3 retries
                raise Exception("Maximum retry attempts reached after timeout") from None
            time.sleep(2)  # Wait for 2 seconds before retrying
        except requests.exceptions.RequestException as err:
            raise Exception(f"Error occurred during request: {err}") from None
        except ValueError as json_err:
            raise Exception(f"JSON decoding error: {json_err}\nResponse text: {response.text}") from None

    return None  # In case the loop completes without returning

def query_wikidata_issn(journal_name_or_qid: str, lang="de") -> list:
    if re.match(r'^Q\d+$', journal_name_or_qid):
        query = f'''
            SELECT ?issn WHERE {
                wd:{journal_name_or_qid} wdt:P236 ?issn.
            }
        '''
    else: 
        query = f'''
            SELECT ?issn WHERE {{
            ?journal wdt:P236 ?issn;
                    rdfs:label "{journal_name_or_qid}"@{lang}.
            }}
            LIMIT 1
        '''
    try:
        data = run_query(query)
    except Exception as e:
        print(f"An error occurred: {e}")
        return None
    issns = [item['issn']['value'] for item in data['results']['bindings']]
    return issns if issns else None



def check_wikidata_issn_coverage(df, lookup_missing=True, disable_progress_bar=False):
    """
    Given a dataframe journal names in the column 'journal',
    return the percentage value for how many of the journals have an ISSN entry in WikiData.
    """
    # For long running queries, show tqdm progress bar unless disabled
    tqdm.pandas()

    # cache data since query takes a long time
    cache_file = "data/wikidata/cache.csv"

    # make a copy and remove any existing issns in the dataframe
    df = df.copy()
    df['issn'] = pd.NA

    if os.path.exists(cache_file):
        df_cache = pd.read_csv(cache_file)
    else:
        df_cache = df.copy()
    
    # Look up if we have the issn cached from a previous query, otherwise look it up at wikidata
    pbar = tqdm(df.index, disable=disable_progress_bar or not lookup_missing)
    for idx in pbar:
        journal_name = df.at[idx, 'journal']
        if (df_cache['journal'] == journal_name).any():
            idx_cache = df_cache[df_cache['journal'] == journal_name].index[0]
            issn = df_cache.at[idx_cache, 'issn']
            cached = True
        else:
            issn = None
            cached = False

        if lookup_missing and (not issn or issn == '' or pd.isna(issn)):
            pbar.set_postfix_str(textwrap.shorten(journal_name, width=30, placeholder="..."))
            issns = query_wikidata_issn(journal_name)

        if issns is not None:
            df.at[idx, 'issn'] = ','.join(issns)
            if not cached:
                df_cache.at[idx_cache, 'issn'] = ','.join(issns)

    df_cache.to_csv(cache_file, index=False)

    # Calculate the percentage of successful ISSN queries
    total_rows = len(df)
    non_empty_issn_count = df['issn'].notna().sum()
    percentage_hits = round((non_empty_issn_count / total_rows) * 100, 2)
    return percentage_hits
    