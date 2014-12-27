#! /usr/bin/python3
import numpy as np
import matplotlib.pyplot as plt

plt.xkcd()

x = np.arange(-0.3, 1.3, 0.01)
y = x*2 + 2
plt.plot(x, y)
plt.ylim([-1,5])
plt.xlim([-0.2,1.2])

# Get the axes to do some settings there
axes = plt.gca()
# Set the exact positions where the ticks on the axes should be placed
axes.get_xaxis().set_ticks([0,1])
axes.get_yaxis().set_ticks([2,4])
# Rename the tick labels
axes.set_yticklabels(['a', 'b'])
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
axes.annotate('t', xy=(1,0.14), ha='left', va='top', xycoords='axes fraction', textcoords='offset points')
axes.annotate('mix(a,b,t)', xy=(-0.07,1), ha='left', va='top', xycoords='axes fraction', textcoords='offset points')

# Draw some dotted lines
plt.plot([1, 1], [0, 4], color='blue', linewidth=1.5, linestyle="--")
plt.plot([0, 1], [4, 4], color='blue', linewidth=1.5, linestyle="--")

# Try writing the plot to a file
plt.savefig('mix.png', bbox_inches='tight')

# Also display it in a window
plt.show()
