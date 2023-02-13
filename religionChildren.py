import pandas as pd

def find_children(df):
    children = {}
    for index, row in df.iterrows():
        parent = row["origin"]
        child = row["i"]
        if parent in children:
            children[parent].append(child)
        else:
            children[parent] = [child]
    df["children"] = df["i"].map(children).apply(lambda x: x if x is not None else [])
    return df

file_path = "combined_data.xlsx"
df = pd.read_excel(file_path, sheet_name="religion")

# Call the function
result = find_children(df)
result.to_excel("religionChildren.xlsx", index=False)

# Print the result
print(result)
