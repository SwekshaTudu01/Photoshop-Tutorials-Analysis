import pandas as pd

# Define file paths
tool_sequence_file = "/Users/studu/Desktop/video_tool_sequences.csv"  # Main dataset
metadata_file = "/Users/studu/Downloads/video_tool_usage_dataset - Merged.csv"  # Contains Category & Youtuber's Experience

# Load both datasets
df_tools = pd.read_csv(tool_sequence_file)  # Contains Video Name & Tool Sequence
df_metadata = pd.read_csv(metadata_file)  # Contains Video Name, Category, Youtuber's Experience

# Ensure the column names match exactly
df_metadata.rename(columns={"Video Name": "Video Name"}, inplace=True)

# Merge both datasets on "Video Name"
df_merged = df_tools.merge(df_metadata, on="Video Name", how="left")

# Save the updated dataset
output_file = "/Users/studu/Desktop/video_tool_sequence_updated.csv"
df_merged.to_csv(output_file, index=False)

print(f"Updated CSV saved at: {output_file}")
