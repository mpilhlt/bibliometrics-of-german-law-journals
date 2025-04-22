def df_to_md(df, sort_by=None, ascending=False, minimal=False, limit=None):
    if sort_by is not None:
        df = df.sort_values(by=sort_by, ascending=ascending) 
    df.reset_index(drop=True, inplace=True)
    if limit is not None:
        df = df.head(limit)
    markdown = df.to_markdown(index=False)
    if minimal:
        while markdown.find('  ') != -1:
            markdown = markdown.replace('  ', ' ')
        while markdown.find('----') != -1:
            markdown = markdown.replace('----', '---')
    print(markdown)


def resultset_to_md(result_set, sort_by=None, ascending=False, minimal=False, limit=None):
    """prints a sql.run.resultset.ResultSet as markdown table"""
    df = result_set.DataFrame()
    df_to_md(df, sort_by, ascending, minimal, limit)
