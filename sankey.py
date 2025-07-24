import pandas as pd
import plotly.graph_objects as go

pd.set_option("future.no_silent_downcasting", True)

def code_mapping(df, src, targ):
    """ Parameters: dataframe, source node column (string), target node column (string)
        Does: maps labels in src and targ columns to integers
        Returns: dataframe and mapped labels
    """
    if type(src) == str or type(targ) == str:
        df[src] = df[src].astype(str)
        df[targ] = df[targ].astype(str)
        # Code syntax help from ChatGPT to combine columns of type string
        # OpenAI. (2024). ChatGPT (May 13, 2024 version) [Large Language Model] https://chat.openai.com/chat
        labels = sorted(set(df[src].unique()).union(set(df[targ].unique())))
    else:
        labels = sorted(list(set(list(df[src]) + list(df[targ]))))

    codes = range(len(labels))
    lc_map = dict(zip(labels, codes))
    df = df.replace({src: lc_map, targ: lc_map})
    return df, labels

def agg_and_clean(df, cols_lst, threshold = 0):
    """
    Parameters: dataframe, list of columns to aggregate by (strings), count threshold to filter data by (integer)
    Does: aggregates data, removes invalid and missing data, and filters data
    Returns: N/A
    """
    # Code syntax help from ChatGPT to create a column with counts and filter out all zeroes across agg_df[cols_lst]
    # OpenAI. (2024). ChatGPT (May 13, 2024 version) [Large Language Model] https://chat.openai.com/chat
    agg_df = df.groupby(cols_lst).size().reset_index(name = "Count")
    agg_df = agg_df[(agg_df[cols_lst] != 0).all(axis = 1) & (agg_df["Count"] != 0)]
    agg_df = agg_df.dropna()
    agg_df = agg_df[agg_df["Count"] > threshold]
    return agg_df

def df_stacking(agg_df, threshold = 0):
    """
    Parameters: aggregated dataframe, threshold to filter "Count" column by (integer)
    Does: create a stacked dataframe, re-aggregate by source & target combinations, and filter by "Count" column
    Returns: filtered, stacked dataframe
    """
    dfs = []
    cols_lst = list(agg_df.columns)
    for i in range(len(cols_lst) - 2):
        temp_df = agg_df[[cols_lst[i], cols_lst[i + 1], "Count"]]
        temp_df.columns = ["src", "targ", "Count"]
        dfs.append(temp_df)
    stacked = pd.concat(dfs, axis = 0)

    stacked = stacked.groupby(["src", "targ"], as_index = False)["Count"].sum()
    stacked = stacked[stacked["Count"] > threshold]

    return stacked

def make_sankey(df, src, targ, *cols, vals = None, to_agg = False, threshold = 0, **kwargs):
    """
    Parameters: dataframe, source node column (string), target node column (string), additional columns (strings),
    link values/thickness (string), need to aggregate (boolean), threshold to filter values by (integer),
    additional parameters
    Does: processes data (aggregation and/or stacking) if necessary and creates a sankey figure
    Returns: N/A
    """
    if vals:
        values = df[vals]
    else:
        if cols:
            all_cols = [src, targ]
            for col in cols:
                all_cols.append(col)
            agg_df = agg_and_clean(df, all_cols)
            df = df_stacking(agg_df, threshold)
            src = "src"
            targ = "targ"
            values = df["Count"]
        elif to_agg is True:
            df = agg_and_clean(df, [src, targ], threshold)
            values = df["Count"]
        else:
            values = [1] * len(df)

    df, labels = code_mapping(df, src, targ)
    link = {"source": df[src], "target": df[targ], "value": values}

    thickness = kwargs.get("thickness", 50)
    pad = kwargs.get("pad", 50)

    node = {"label": labels, "thickness": thickness, "pad": pad}

    sk = go.Sankey(link = link, node = node)
    fig = go.Figure(sk)

    width = kwargs.get("width", 800)
    height = kwargs.get("height", 400)
    fig.update_layout(
        autosize=False,
        width=width,
        height=height)

    return fig
