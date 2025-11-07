import matplotlib.pyplot as plt
import matplotlib.animation as animation
import random

# Create a figure and an axes object
fig, ax = plt.subplots()

# Initial text to display
initial_text = "Current Value: 0"
text_artist = ax.text(0.5, 0.9, initial_text, transform=ax.transAxes, ha='right', va='top')

# Set up some initial plot data (optional, but common in live updates)
x_data = [0]
y_data = [0]
line, = ax.plot(x_data, y_data)

# Function to update the plot and text
def update(frame):
    # Simulate new data
    new_x = x_data[-1] + 1
    new_y = random.randint(0, 10)
    x_data.append(new_x)
    y_data.append(new_y)

    # Update the plot data
    line.set_xdata(x_data)
    line.set_ydata(y_data)
    
    # Update the text artist
    text_artist.set_text(f"noise: 40db\ntemp&hum: 24c, 15rh\ntime:12:31PM")

    # Adjust plot limits if necessary
    ax.set_xlim(min(x_data), max(x_data) + 1)
    ax.set_ylim(0, 11)

    return line, text_artist,

# Create the animation
ani = animation.FuncAnimation(fig, update, interval=1000, blit=True)

# Show the plot
plt.show()
