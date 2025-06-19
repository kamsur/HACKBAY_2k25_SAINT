import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

def circular_plot(data):
    if not isinstance(data, pd.DataFrame):
        raise ValueError("Input must be a pandas DataFrame.")
    
    num_objects = len(data)
    num_features = len(data.columns)
    
    # fig, ax = plt.subplots()
    fig, ax = plt.subplots(figsize=(10, 5))
    # axs.set_aspect('equal')
    # ax.axis('off')  # Hide axes

    # Normalize each column to [0, 1] for scaling radii
    

    colors = plt.cm.viridis(np.linspace(0, 1, num_features))

    radius = []
    for i, col in enumerate(data.columns):
        vals = data.values[:,i]
        radius.append((vals / vals.max()) * 0.5)

    radius = np.array(radius)

    norm_radius = 0.2 + (radius) * (0.5 - 0.2) / 0.5

    for i, col in enumerate(data.columns):
        for j in range(num_objects):
            
            # radius = radius[j]
            x = 0.5 + i*2
            y = 0.5 
            
            circle = plt.Circle((x, y), radius=norm_radius[i][j]   , alpha=0.4, color=colors[j], label=col)
            ax.add_patch(circle)
            # if radius[j] < 0.5:
            ax.text(x, -0.5, f'Energy consumed {col}' , ha='center', va='center', fontsize=8, color='black')
            if norm_radius[i][j] < 0.5:   
                ax.text(x, y, f'{round(radius[i][j]*100,2)}%' , ha='center', va='center', fontsize=8, color='black')

            # ax.set_xlim(0, 1)
            # ax.set_ylim(0, 1)   
        # print(f"Column: {col}, Radius: {radius}")
    
    ax.set_xlim(-1, num_features * 2)
    ax.set_ylim(-1, 2 )

    # Add legend once per column
    # handles, labels = ax.get_legend_handles_labels()
    # by_label = dict(zip(labels, handles))
    # ax.legend(by_label.values(), by_label.keys(), loc='upper right')

    # plt.title("Circular Plot by Column and Value")
    plt.show()

data = pd.DataFrame({
    'RAM': [0.348, 0.006],
    'CPU': [1.482, 0.025],
    'GPU': [0.135, 0.007],
})

print(data)

circular_plot(data)
    