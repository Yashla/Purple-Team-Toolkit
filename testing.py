import matplotlib.pyplot as plt
import numpy as np

# Test results for "mDNS searching for multiple services"
results = np.array([5085, 5092, 5098, 5100, 5087])

# Calculate the average and median
average = np.mean(results)
median = np.median(results)

# Creating the figure and axis objects
fig, ax = plt.subplots()

# Plot each test result as a bar
ax.bar(range(len(results)), results, color='lightgreen', label='Test Results')

# Highlight the average and median
ax.axhline(average, color='blue', linewidth=2, label=f'Average: {average:.1f} ms')
ax.axhline(median, color='purple', linewidth=2, label=f'Median: {median:.1f} ms')

# Adding labels and title
ax.set_xlabel('Test Number')
ax.set_ylabel('Response Time (ms)')
ax.set_title('Performance Testing: mDNS Searching for Multiple Services')
ax.set_xticks(range(len(results)))
ax.set_xticklabels([f'Test {i+1}' for i in range(len(results))])

# Adding a legend
ax.legend()

# Show the plot
plt.show()
