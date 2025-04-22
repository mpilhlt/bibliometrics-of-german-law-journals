import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import pandas as pd
import numpy as np

def compare_coverage_kb_zdb(df_kb, df_zdb, min_year, max_year):

    # todo: alle abkürzungen als kleinbuchstaben matchen

    # Make sure we can match all the abbreviations
    y_vals = df_kb['abk']
    for abk in y_vals:
        if df_zdb[df_zdb['abbr'] == abk].empty:
            # Getting the name of the abbreviation
            name = df_kb[df_kb['abk'] == abk]['zeitschrift'].values[0]

            # Checking if the name exists in the 'name' column of df_zdb
            if not df_zdb[df_zdb['name'] == name].empty:
                # If so, we write the abbreviation into the 'abbr' column
                df_zdb.loc[df_zdb['name'] == name, 'abbr'] = abk
            
    # plot
    fig, ax = plt.subplots(figsize = (10, 15))

    # Generate and plot publication ranges 
    for y in y_vals:
        df_temp = df_zdb[df_zdb['abbr'].str.lower()==y.lower()]
        for _, row in df_temp.iterrows():
            x1 = int(row['year_start']) if not pd.isna(row['year_start']) else min_year
            x2 = int(row['year_end']) if not pd.isna(row['year_end']) else max_year
            if x1 > x2: continue
            x1 = min(max_year, max(min_year, x1))
            x2 = max(min_year, min(max_year, x2))
            ax.plot((x1, x2), (y, y), color = 'r', linewidth = 5, label="Publication period (source: ZDB)")

    # Plot available years
    x1_vals = df_kb['min_pubyear_in_openalex'].clip(min_year, max_year)
    x2_vals = df_kb['max_pubyear_in_openalex'].clip(min_year, max_year)
    for y, x1, x2 in zip(y_vals, x1_vals, x2_vals):
        if pd.notna(x1) and pd.notna(x2):
            x1, x2 = int(x1), int(x2)
            ax.plot((x1, x2), (y, y), color = 'g', linewidth = 5, label="Available metadata in OpenAlex")
        

    # Setup xticks and labels
    x_ticks = range(min_year, max_year + 1)
    x_labels = [year if year%10==0 else '' for year in x_ticks]
    ax.set_xticks(x_ticks)
    ax.set_xticklabels(x_labels)

    # Labels
    plt.xlabel('Year Range')
    plt.ylabel('Journal')

    # Ensure each label is only appeared once in the legend
    handles, labels = plt.gca().get_legend_handles_labels()
    by_label = dict(zip(labels, handles))
    plt.legend(by_label.values(), by_label.keys())

    # Display the plot
    plt.show()



def compare_rankings(df, title=None, label_ranking_a=None, label_ranking_b=None):
    # Prepare the data for plotting
    x = df['ranking_a']
    y = df['ranking_b']
    labels = df['abk']
    
    # Create the bubble chart
    plt.figure(figsize=(12, 10))
    plt.scatter(x, y, s=500, alpha=0.5, c='blue', edgecolors='w', linewidth=2)

    # Add labels
    for i in range(len(labels)):
        plt.annotate(labels.iloc[i], (x.iloc[i], y.iloc[i]), fontsize=8, ha='center', va='center')

    # Draw a dotted diagonal line
    plt.plot([min(x), max(x)], [min(x), max(x)], 'r--', linewidth=2)  # Red dotted line

    # Set x and y limits
    plt.xlim(1, df['ranking_a'].max())  # Adjust x limits based on ranking_a
    plt.ylim(1, df['ranking_b'].max())  # Adjust y limits based on ranking_b
    
    # Set titles and labels
    if title:
        plt.title(title)
    plt.xlabel(label_ranking_a if label_ranking_a else 'Ranking A')
    plt.ylabel(label_ranking_b if label_ranking_b else 'Ranking B')
    
    # Set x and y ticks to integers
    plt.gca().xaxis.set_major_locator(ticker.MaxNLocator(integer=True))
    plt.gca().yaxis.set_major_locator(ticker.MaxNLocator(integer=True))

    plt.grid()

    # Show the bubble chart
    plt.show()


