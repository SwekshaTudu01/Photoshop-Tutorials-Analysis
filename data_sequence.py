import pandas as pd

def normalize_seq(a):
    idx = 0
    while idx < len(a)-1:
        if a[idx] == a[idx+1]:
            a.pop(idx+1)
        else:
            idx += 1
    return a

file_path = "/Users/studu/Desktop/video_tool_usage_dataset.csv"
df = pd.read_csv(file_path)

df.columns = df.columns.str.strip().str.replace('"', '')


df = df.sort_values(by=["Video Name", "Start Seconds"])


video_sequences = df.groupby("Video Name")["Action_x"].apply(lambda actions: " -> ".join(normalize_seq(list(actions)))).reset_index()


output_path = "/Users/studu/Desktop/video_tool_sequences.csv"
video_sequences.to_csv(output_path, index=False)

print(f"Tool sequences saved to: {output_path}")
