import pandas as pd

def normalize_seq(a):
    idx = 0
    while idx < len(a)-1:
        if a[idx] == a[idx+1]:
            a.pop(idx+1)
        else:
            idx += 1
    return a

# Load the dataset
file_path = "/Users/studu/Desktop/video_tool_usage_dataset.csv"
df = pd.read_csv(file_path)

# Remove any unintended spaces or quotes in column names
df.columns = df.columns.str.strip().str.replace('"', '')

# Ensure correct sorting by Start Timestamp (in case data is not pre-sorted)
df = df.sort_values(by=["Video Name", "Start Seconds"])

# Group by Video Name and collect tool sequences
video_sequences = df.groupby("Video Name")["Action_x"].apply(lambda actions: " -> ".join(normalize_seq(list(actions)))).reset_index()

# Save the output CSV
output_path = "/Users/studu/Desktop/video_tool_sequences.csv"
video_sequences.to_csv(output_path, index=False)

print(f"Tool sequences saved to: {output_path}")
