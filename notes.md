
To pretty print a dataframe: 

with pd.option_context("display.max_rows", None, "display.max_columns", None):  # more options can be specified also
    print(i.df)