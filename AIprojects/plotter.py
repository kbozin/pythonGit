import pandas as pd
import matplotlib.pyplot as plt

# Read the Excel file
# Replace 'your_file.xlsx' with your Excel file path
try:
    df = pd.read_excel('data.xlsx')
except FileNotFoundError:
    print("Error: File not found. Please provide the correct file path.")
    exit()

# Display column names to help select the correct ones
print("Available columns:", df.columns.tolist())

# Select three columns to plot (modify these based on your column names)
# Example: column1 = 'Time', column2 = 'Temperature', column3 = 'Pressure'
column1 = input("Enter first column name to plot: ")
column2 = input("Enter second column name to plot: ")
column3 = input("Enter third column name to plot: ")

# Verify if selected columns exist
if not all(col in df.columns for col in [column1, column2, column3]):
    print("Error: One or more selected columns not found in the Excel file.")
#    exit()

# Create a figure with three subplots
fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(10, 12))
#fig, (ax1, ax2, ax3) = plt.subplots(1, 1, figsize=(10, 12)) # trying one plot
# Plot each column
ax1.plot(df[column1], label=column1, color='blue')
ax1.set_title(f'{column1} Plot')
ax1.set_xlabel('Index')
ax1.set_ylabel(column1)
ax1.grid(True)
ax1.legend()

ax2.plot(df[column2], label=column2, color='green')
ax2.set_title(f'{column2} Plot')
ax2.set_xlabel('Index')
ax2.set_ylabel(column2)
ax2.grid(True)
ax2.legend()

ax3.plot(df[column3], label=column3, color='red')
ax3.set_title(f'{column3} Plot')
ax3.set_xlabel('Index')
ax3.set_ylabel(column3)
ax3.grid(True)
ax3.legend()

# Adjust layout to prevent overlap
plt.tight_layout()

# Show the plot
plt.show()

# Optional: Plot all three columns together in a single plot
plt.figure(figsize=(10, 6))
plt.plot(df[column1], label=column1, color='blue')
plt.plot(df[column2], label=column2, color='green')
plt.plot(df[column3], label=column3, color='red')
plt.title('Combined Plot of Selected Columns')
plt.xlabel('Index')
plt.ylabel('Values')
plt.grid(True)
plt.legend()
plt.show()
print(df.mean(numeric_only=True))