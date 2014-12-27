#! /usr/bin/python3
import numpy as np
import matplotlib.pyplot as plt

plt.xkcd()

x = np.arange(-0.2, 1.2, 0.01)
# Edges for the smoothstep function
edge0 = 0.3
edge1 = 0.7
# clamp and scale the x values
x_clamped = [max(0, min((value - edge0)/(edge1 - edge0), 1.0)) for value in x]
# calculate the smoothstep function
y = [value*value*value*(value*(value*6 - 15) + 10) for value in x_clamped]
plt.plot(x, y)
plt.ylim([-0.2,1.2])
plt.xlim([-0.2,1.2])

# Get the axes to do some settings there
axes = plt.gca()
# Set the exact positions where the ticks on the axes should be placed
axes.get_xaxis().set_ticks([0.3,0.7])
axes.get_yaxis().set_ticks([0,1])
# Rename the tick labels
axes.set_xticklabels(['a', 'b'])
axes.set_yticklabels(['0', '1'])
# Make the right and top spine go away
axes.spines['right'].set_visible(False)
axes.spines['top'].set_visible(False)
# Make the ticks only appear on the remaining spines
axes.yaxis.set_ticks_position('left')
axes.xaxis.set_ticks_position('bottom')
# Put the remaining two spines in the origin
axes.spines['left'].set_position('zero')
axes.spines['bottom'].set_position('zero')

# Set labels for axes in an complicated way to set the positions... Could be done nicer, dunnolol.
axes.annotate('x', xy=(1,0.14), ha='left', va='top', xycoords='axes fraction', textcoords='offset points')
axes.annotate('smoothstep(a,b,x)', xy=(-0.07,1), ha='left', va='top', xycoords='axes fraction', textcoords='offset points')

# Draw some dotted lines
plt.plot([0.7, 0.7], [0, 1], color='blue', linewidth=1.5, linestyle="--")
plt.plot([0, 0.7], [1, 1], color='blue', linewidth=1.5, linestyle="--")


# Try writing the plot to a file
plt.savefig('smoothstep.png', bbox_inches='tight')

# Also display it in a window
plt.show()
