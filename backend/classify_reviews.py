import pandas as pd
import os

def classify_comment(input_csv, out_csv):
    df = pd.read_csv(input_csv, encoding="utf-8-sig")
    def tag_classify(text):
        text = str(text).lower()
        if "crash" in text or "close" in text:
            return "崩溃闪退"
        elif "slow" in text or "lag" in text:
            return "卡顿性能差"
        elif "pay" in text or "subscribe" in text:
            return "付费订阅问题"
        elif "ad" in text:
            return "广告过多"
        else:
            return "其他反馈"
    df["pain_point_tag"] = df["review"].apply(tag_classify)
    os.makedirs(os.path.dirname(out_csv), exist_ok=True)
    df.to_csv(out_csv, index=False, encoding="utf-8-sig")
    return df