import json
import matplotlib.pyplot as plt
import numpy as np
import os

def generate_benchmark_chart(json_filepath="docs/benchmarks.json", output_filepath="benchmark_plot.png"):
    """
    Parses a pytest-benchmark JSON file and generates a horizontal bar chart.
    """
    if not os.path.exists(json_filepath):
        print(f"Error: Could not find {json_filepath}.")
        print("Please run: python -m pytest tests/test_performance.py --benchmark-json=docs/benchmarks.json")
        return

    # Load the JSON data
    with open(json_filepath, 'r') as f:
        data = json.load(f)

    names = []
    means = []
    stddevs = []

    # Extract the relevant stats
    for b in data.get('benchmarks', []):
        # Clean up the test names for a professional display
        name = b['name'].replace('test_benchmark_', '').replace('_', ' ').title()
        names.append(name)
        
        # Pytest-benchmark saves times in seconds. Convert to milliseconds (ms).
        means.append(b['stats']['mean'] * 1000)
        stddevs.append(b['stats']['stddev'] * 1000)

    # Sort the data from fastest to slowest
    sorted_indices = np.argsort(means)
    names = [names[i] for i in sorted_indices]
    means = [means[i] for i in sorted_indices]
    stddevs = [stddevs[i] for i in sorted_indices]

    # Initialize the plot
    fig, ax = plt.subplots(figsize=(10, 6))
    y_pos = np.arange(len(names))

    # Create horizontal bars with error bars for standard deviation
    ax.barh(y_pos, means, xerr=stddevs, align='center', color='#4C72B0', edgecolor='black', capsize=5)
    
    # Format the axes
    ax.set_yticks(y_pos)
    ax.set_yticklabels(names, fontsize=11)
    ax.invert_yaxis()  # Read top-to-bottom
    ax.set_xlabel('Mean Execution Time (milliseconds)', fontsize=12)
    ax.set_title('Search Engine Query Performance', fontsize=14, fontweight='bold', pad=15)

    # Add data labels to the end of each bar
    for i, v in enumerate(means):
        # Position the text slightly past the error bar
        offset = v + stddevs[i] + (max(means) * 0.02)
        ax.text(offset, i, f"{v:.3f} ms", va='center', fontweight='bold', color='#333333')

    # Remove top and right borders for a cleaner look
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    # Save the plot
    plt.tight_layout()
    plt.savefig(output_filepath, dpi=300)
    print(f"✅ Success! Benchmark visualization saved to '{output_filepath}'")

if __name__ == "__main__":
    generate_benchmark_chart()