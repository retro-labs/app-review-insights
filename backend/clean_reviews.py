import json
import pandas as pd
import os

def clean_data(raw_path, clean_path):
    with open(raw_path, "r", encoding="utf-8") as f:
        raw_list = json.load(f)
    df = pd.DataFrame(raw_list)

    # 容错：如果存在review列才清洗，不存在就新建空列
    if "review" in df.columns:
        df["review"] = df["review"].str.strip()
        df = df[df["review"] != ""]
    else:
        df["review"] = ""

    os.makedirs(os.path.dirname(clean_path), exist_ok=True)
    df.to_csv(clean_path, index=False, encoding="utf-8-sig")
    return df