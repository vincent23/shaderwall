#! /usr/bin/python3
import numpy as np
import matplotlib.pyplot as plt

plt.xkcd()

x = np.arange(0.5, 1.5, 0.01)
y = x*0 + 1
plt.plot(x, y)
plt.ylim([-0.2,1.2])
plt.xlim([-0.2,1.2])

# Get the axes to do some settings there
axes = plt.gca()
# Set the exact positions where the ticks on the axes should be placed
axes.get_xaxis().set_ticks([0.5])
axes.get_yaxis().set_ticks([0,1])
# Rename the tick labels
axes.set_xticklabels(['e'])
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
axes.annotate('step(e,x)', xy=(-0.07,1), ha='left', va='top', xycoords='axes fraction', textcoords='offset points')

# Draw some dotted lines
plt.plot([0.5, 0.5], [0, 1], color='blue', linewidth=1.5, linestyle="--")
axes.plot((0.5),(1),'o',color='blue')


# Try writing the plot to a file
plt.savefig('step.png', bbox_inches='tight')

# Also display it in a window
plt.show()
