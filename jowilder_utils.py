# from google.colab import files
from matplotlib import pyplot as plt
import numpy as np
import pandas as pd
from IPython.display import display
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
from imblearn.pipeline import make_pipeline
from sklearn.compose import ColumnTransformer


def response_boxplot(df, category, verbose=False):
    print('\n'+category)
    fig, axs = plt.subplots(1, 3, figsize=(20, 10))
    qs = ['EFL_yes_no', 'skill_low_med_high', 'enjoy_high_med_low_none']
    for i, f in enumerate(['R0_quiz_response', 'R1_quiz_response', 'R2_quiz_response', ]):
        if verbose:
            print(qs[i])
        bp = df.boxplot(column=category, by=df[f].astype(
            'category'), ax=axs[i])
        bp.set_xlabel('')
        for choice in range(df[f].min(), df[f].max()+1):
            query = f"{f}=={choice}"
            cat_df = df.query(query)[category]
            num_chose = len(cat_df)
            mean = cat_df.mean()
            std = cat_df.std()
            if verbose:
                print(
                    f'{f} # chose {choice}: {num_chose} ({round(num_chose/len(df)*100)}%). Avg {mean}, std {std}.')
    plt.suptitle(f'{category} Boxplot')
    fig.show()


def group_by_func(df, func, title='', show=True):
    r0_groups = {0: 'native', 1: 'nonnative'}
    r1_groups = {0: 'not very good skill',
                 1: 'okay skill', 2: 'very good skill'}
    r2_groups = {0: 'really enjoy', 1: 'enjoy', 2: 'okay', 3: 'not enjoy'}
    def group_string(r0, r1, r2): return ', '.join(
        [r0_groups[r0], r1_groups[r1], r2_groups[r2]])
    result_dfs = [pd.DataFrame(index=r1_groups.values(), columns=r2_groups.values(
    )), pd.DataFrame(index=r1_groups.values(), columns=r2_groups.values())]
    if show:
        print(f'{"-"*6}  {title}  {"-"*6}')
    for r0 in [0, 1]:
        subtitle = "Nonnatives" if r0 else "Natives"
        if show:
            print(f'\n{subtitle}:')
        tdf0 = df.query(f"R0_quiz_response == {r0}")
        for r1 in [0, 1, 2]:
            tdf1 = tdf0.query(f"R1_quiz_response == {r1}")
            for r2 in [0, 1, 2, 3]:
                tdf2 = tdf1.query(f"R2_quiz_response == {r2}")
                result_dfs[r0].loc[r1_groups[r1], r2_groups[r2]
                                   ] = func(df, tdf0, tdf1, tdf2)
        if show:
            display(result_dfs[r0])
    return result_dfs


def standard_group_by_func(fulldf, per_category_stats_list=None):
    per_category_stats_list = None or ['sess_count_clicks',
                                                            'sess_count_hovers',
                                                            'sess_meaningful_action_count',
                                                            'sess_EventCount',
                                                            'sess_count_notebook_uses',
                                                            'sess_avg_time_between_clicks',
                                                            'sess_first_enc_words_read',
                                                            'sess_first_enc_boxes_read',
                                                            'sess_num_enc',
                                                            'sess_first_enc_duration',
                                                            'sess_first_enc_avg_wps',
                                                            'sess_first_enc_var_wps',
                                                            'sess_first_enc_avg_tbps',
                                                            'sess_first_enc_var_tbps',
                                                            'sess_start_obj',
                                                            'sess_end_obj',
                                                            'start_level',
                                                            'max_level',
                                                            'sessDuration']
    dfs_list = []
    title_list = []

    def df_func(df, tdf0, tdf1, tdf2): return len(tdf2)
    title = 'count'
    dfs = group_by_func(fulldf, df_func, title)
    dfs_list.append(dfs)
    title_list.append(title)

    def df_func(df, tdf0, tdf1, tdf2): return round(len(tdf2)/len(df)*100, 2)
    title = 'percent total pop'
    dfs = group_by_func(fulldf, df_func, title)
    dfs_list.append(dfs)
    title_list.append(title)

    def df_func(df, tdf0, tdf1, tdf2): return round(len(tdf2)/len(tdf0)*100, 2)
    title = 'percent native class pop'
    dfs = group_by_func(fulldf, df_func, title)
    dfs_list.append(dfs)
    title_list.append(title)

    for category in per_category_stats_list:
        df_func = get_avg_std_df_func(category)
        title = f'(avg, std) {category}'
        dfs = group_by_func(fulldf, df_func, title)
        dfs_list.append(dfs)
        title_list.append(title)
    return title_list, dfs_list


def get_avg_std_df_func(category_name):
    def inner(df, tdf0, tdf1, tdf2):
        mean = tdf2[category_name].mean()
        std = tdf2[category_name].std()
        if not pd.isna(mean):
            mean = round(mean, 2)
        if not pd.isna(std):
            std = round(std, 2)
        return (mean, std)
    return inner


def html_stats(df):
    html_strs = ['<div class="container">', '<h3>{Stats}</h3>']
    qs = ['EFL_yes_no', 'skill_low_med_high', 'enjoy_high_med_low_none']
    html_strs.append(f'<p> Total pop {len(df)} </p>')
    for i, f in enumerate(['R0_quiz_response', 'R1_quiz_response', 'R2_quiz_response', ]):
        html_strs.append(f'<p> {qs[i]}</p>')
        for choice in range(df[f].min(), df[f].max()+1):
            query = f"{f}=={choice}"
            cat_df = df.query(query)
            num_chose = len(cat_df)
            html_strs.append(
                f'<p>{f} # chose {choice}: {num_chose} ({round(num_chose/len(df)*100)}%).</p>')
    return '\n'.join(html_strs+['</div>'])


def full_html(base_df, title_list, dfs_list, suptitle=None):
    HEADER = '''<!DOCTYPE html>
<html lang="en">

<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Document</title>
</head>

<body>
  <style>
    .flex-container {
      display: flex;
      flex-wrap: wrap;
    }

    .container {
      border: thick solid black;
      padding: 10px;
      margin: 5px;
    }

    .container table:nth-of-type(2) td {
      background-color: rgb(161, 161, 230);
    }

    .container table:nth-of-type(2) th {
      background-color: rgb(20, 20, 194);
      color: white;
    }

    .container table:nth-of-type(2n-1) td {
      background-color: rgb(235, 158, 158);
    }

    .container table:nth-of-type(2n-1) th {
      background-color: rgb(160, 11, 11);
      color: white;
    }
    .break {
  flex-basis: 100%;
  height: 0;
}
  </style>
  <div class="flex-container">'''
    FOOTER = '''  </div>
    </body>

    </html>'''
    def table_header(title): return f'''    <div class="container">
        <h3>{title}</h3>'''
    table_footer = '''    </div>'''
    def table_html(title, dfs): return '\n'.join([table_header(
        title), "<p>Natives:</p>", dfs[0].to_html(), "<p>Nonnatives:</p>", dfs[1].to_html(), table_footer])

    if suptitle is not None:
        suptitle = f'<h2>{suptitle}</h2>\n<div class="break"></div> <!-- break -->'
    else:
        suptitle = ''
    return '\n'.join([HEADER, suptitle, html_stats(base_df)] +
                     [table_html(t, dfs) for t, dfs in zip(title_list, dfs_list)] +
                     [FOOTER])


def download_full_html(base_df, title_list, dfs_list, filename, suptitle=None):
    with open(filename, 'w+') as f:
        f.write(full_html(base_df, title_list, dfs_list, suptitle=suptitle))
        print("Wrote to", filename)
    files.download(filename)


onext_int_feats = [f'obj{i}_onext_int' for i in range(80)]
onext_int_cats = [["nan", 1],
                  ["nan", 11],
                  ["nan", 12, 86, 111, 125],
                  ["nan", 13, 14, 113, 116, 118],
                  ["nan", 14, 15, 113, 114, 116, 118],
                  ["nan", 13, 15, 113, 114, 116, 118],
                  ["nan", 16, 86, 115, 118, 132, 161],
                  ["nan", 17, 86, 115, 118, 128, 161],
                  ["nan", 18, 86, 115, 118, 161],
                  ["nan", 19, 86, 117, 118, 127, 133, 134, 161],
                  ["nan", 20, 133, 134, 136],
                  ["nan", 2, 80, 81, 82, 83],
                  ["nan", 21, 86, 117, 127, 136, 137, 161],
                  ["nan", 22, 137, 141],
                  ["nan", 23, 24, 86, 117, 127, 136, 161],
                  ["nan", 23, 24, 117, 127, 136, 161],
                  ["nan", 25, 86, 117, 118, 127, 136, 140, 147, 151, 161],
                  ["nan", 26, 142, 145],
                  ["nan", 27, 143],
                  ["nan", 28, 86, 117, 118, 136, 140, 150, 161],
                  ["nan", 29, 119, 130],
                  ["nan", 29, 30, 35, 86, 117, 118, 126, 136, 140, 149],
                  ["nan", 3, 80, 82, 83, 86, 87, 88, 93],
                  ["nan", 31, 38],
                  ["nan", 32, 153],
                  ["nan", 33, 154],
                  ["nan", 34, 155],
                  ["nan", 35, 156],
                  ["nan", 36, 157],
                  ["nan", 37, 158],
                  ["nan", 30],
                  ["nan", 39, 163],
                  ["nan", 40, 160],
                  ["nan", 3],
                  ["nan", 41, 164, 166],
                  ["nan", 42, 166],
                  ["nan", 30],
                  ["nan", 44, 85, 125],
                  ["nan", 29, 45, 47, 84, 118, 125, 136, 140, 149, 168, 169, 184],
                  ["nan", 45, 46, 169, 170],
                  ["nan", 29, 45, 47, 92, 118, 136, 140, 149, 169, 184],
                  ["nan", 29, 45, 48, 92, 118, 140, 149, 168, 184],
                  ["nan", 46, 49, 168],
                  ["nan", 46, 50, 168, 170],
                  ["nan", 5, 80, 82, 83, 86, 89, 91, 95, 97, 125],
                  ["nan", 29, 51, 92, 118, 136, 140, 149, 168, 184],
                  ["nan", 52, 92, 118, 136, 149, 171, 184],
                  ["nan", 53, 54, 92, 118, 136, 140, 149, 184],
                  ["nan", 53, 54, 55, 59, 60, 90, 92, 94,
                      118, 136, 140, 149, 168, 184],
                  ["nan", 53, 55, 59, 60, 90, 92, 94, 118, 136, 140, 149, 184],
                  ["nan", 55, 56, 59, 60, 149, 174],
                  ["nan", 57, 59, 60, 174],
                  ["nan", 58, 59, 60, 136, 172, 174, 184],
                  ["nan", 29, 59, 60, 61, 92, 118, 136, 149, 168, 172, 184],
                  ["nan", 55, 56, 57, 58, 60, 61, 140, 172, 174, 184],
                  ["nan", 6, 80, 82, 83, 86, 98, 100, 125],
                  ["nan", 55, 56, 57, 58, 59, 61, 92, 118,
                      136, 140, 149, 172, 174, 184],
                  ["nan", 59, 62, 136, 140, 149, 172, 173, 175, 184],
                  ["nan", 63, 64, 176],
                  ["nan", 64, 66, 149, 175, 184],
                  ["nan", 29, 65, 66, 92, 118, 136, 140, 172, 175, 177, 184],
                  ["nan", 66, 67, 68, 92, 118, 136, 140, 146, 175, 177, 184],
                  ["nan", 67, 144],
                  ["nan", 29, 64, 65, 68, 92, 118, 131, 136,
                      140, 148, 149, 172, 175, 177, 184],
                  ["nan", 92, 118, 122, 123, 124, 131, 136, 140,
                      146, 148, 168, 172, 175, 177, 184],
                  ["nan", 70],
                  ["nan", 7],
                  ["nan", 71, 178],
                  ["nan", 72, 179],
                  ["nan", 73, 180],
                  ["nan", 74, 181],
                  ["nan", 75, 182],
                  ["nan", 69],
                  ["nan", 77, 78, 185],
                  ["nan", 78, 185],
                  ["nan", 79],
                  [0],
                  ["nan", 8],
                  ["nan", 9, 103],
                  ["nan", 104, 105, 108]]

QA_1_feats = [f'Q{i}_A1' for i in range(19)]
QA_1_cats = [['0', 'A', 'B', 'C', 'D'],
             ['0', 'A', 'B', 'C', 'D'],
             ['0', 'A', 'B', 'C', 'D'],
             ['0', 'A', 'B', 'C', 'D'],
             ['0', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H',
              'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q'],
             ['0', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H',
              'I', 'J', 'K', 'L', 'M', 'O', 'P', 'Q'],
             ['0', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H',
              'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q'],
             ['0', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H',
              'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q'],
             ['0', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H',
              'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q'],
             ['0', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H',
              'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q'],
             ['0', '?', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H',
              'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q'],
             ['0', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H',
              'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q'],
             ['0', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H',
              'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q'],
             ['0', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H',
              'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q'],
             ['0', 'A', 'B', 'C', 'D', 'F', 'G', 'I', 'M', 'N', 'O', 'P', 'Q',
              'R', 'S', 'V', 'W', 'X', 'Y', 'Z', 'a', 'b', 'c', 'd', 'e', 'f'],
             ['0', 'Q', 'V', 'X', 'Y', 'Z', 'a', 'b', 'c', 'd', 'e', 'f'],
             ['0', '?', 'X', 'Y', 'Z', 'b', 'c', 'd', 'e', 'f'],
             ['0', 'X', 'Y', 'b', 'c', 'd', 'e', 'f'],
             ['0', 'X', 'Y', 'Z', 'a', 'b', 'c', 'd', 'e', 'f']]



def get_preprocessor(df,scaler=StandardScaler(), imputer=SimpleImputer(strategy='constant')):
    """
    By default has a number of steps:
    1. drops columns from use in preprocessor if present:
       - [f'Q{q}_answers' for q in range(19)]
       - ["play_year", "play_month", "play_day", "play_hour", "play_minute", "play_second"]
       - ["_continue", "continue", "save_code", "music", "hq", "fullscreen", "persistentSessionID"]
    2. Creates a preprocessor for all non-y columns and non-boolean columns with the following steps:
       a. Standard Scaler (0 mean, 1 std)
       b. Simple Imputer(strategy='constant') (fill NaN with 0)
    3. Fits the preprocessor to the given X
    4. returns the unfitted preprocessor (sklearn pipeline), and the unprocessed X dataframe
    :param df: jowilder dataframe
    :param scaler: sklearn compatible scaler
    :param imputer: sklearn compatible imputer
    :return: the unfitted preprocessor (sklearn pipeline), and the unprocessed X dataframe
    """
    df = df.drop(
            [f'Q{q}_answers' for q in range(19)] + ["play_year", "play_month", "play_day", "play_hour", "play_minute",
                                                    "play_second",
                                                    "_continue", "continue", "save_code", "music", "hq", "fullscreen",
                                                    "persistentSessionID", ], axis=1, errors='ignore').copy()
    y_cols, bool_cols, int_cols = separate_columns(df)
    X = df.loc[:,bool_cols+int_cols]

    # too complicated to allow for pipeline order
    # pipeline_strings = [pipeline_order[i:i+2] for i in range(0,len(pipeline_order),2)]
    # transformers = []
    # num_sa, num_sc, num_im = 0,0,0
    # for s in pipeline_strings:
    #     if s == 'Sa':
    #         transformer = make_pipeline(sampler)
    #         cols = int_cols + bool_cols
    #         name = f'{s}{num_sa}'
    #         num_sa += 1
    #     elif s == 'Sc':
    #         transformer = scaler
    #         name = f'{s}{num_sc}'
    #         cols = int_cols
    #         num_sc += 1
    #     elif s == 'Im':
    #         transformer = imputer
    #         name = f'{s}{num_im}'
    #         cols = int_cols
    #         num_im += 1
    #     else:
    #         raise ValueError("Pipeline substrings must be Sa Sc or Im")
    #     transformers.append((name, transformer, cols))

    col_str_to_int = lambda col_strs: [X.columns.get_loc(s) for s in col_strs]
    column_transformer = ColumnTransformer(
        transformers=[
            ('num', make_pipeline(scaler,imputer), col_str_to_int(int_cols)),
            ('bool', 'passthrough', col_str_to_int(bool_cols))
        ],
        remainder='passthrough')
    return column_transformer, X

def get_ys(df):
    """

    :rtype: dictionary of y columns (df series). keys: y0,y1,y2,y1_bin
    """
    y0 = df["R0_quiz_response"].astype('category')
    y1 = df["R1_quiz_response"].astype('category')
    y2 = df["R2_quiz_response"].astype('category')
    y1_bin = df["R1_quiz_response_bin"].astype('category')
    y2_bin = df['R2_quiz_response_bin'].astype('category')
    ys = {
        'y0': y0,
        'y1': y1,
        'y2': y2,
        'y1_bin': y1_bin,
        'y2_bin': y2_bin
    }
    return ys


def separate_columns(df) -> (list, list, list):
    """

    :param df:
    :return: tuple of lists of column names for y_columns, bool_columns, and integer_columns
    """
    y_cols = [col for col in df.columns if 'quiz_response' in col]
    bool_cols = [col for col in df.select_dtypes(include=['int64'])
                    if np.isin(df[col].dropna().unique(), [0, 1]).all() and
                    col not in y_cols]
    int_cols = [col for col in df.columns if col not in bool_cols and col not in y_cols]
    return y_cols, bool_cols, int_cols