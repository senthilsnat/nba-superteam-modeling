# adapted from matplotlib radar chart api example

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.path import Path
from matplotlib.spines import Spine
from matplotlib.projections.polar import PolarAxes
from matplotlib.projections import register_projection


def _radar_factory(num_vars):
    theta = 2 * np.pi * np.linspace(0, 1 - 1. / num_vars, num_vars)
    theta += np.pi / 2

    def unit_poly_verts(theta):
        x0, y0, r = [0.5] * 3
        verts = [(r * np.cos(t) + x0, r * np.sin(t) + y0) for t in theta]
        return verts

    class RadarAxes(PolarAxes):
        name = 'radar'
        RESOLUTION = 2

        def fill(self, *args, **kwargs):
            closed = kwargs.pop('closed', True)
            return super(RadarAxes, self).fill(closed=closed, *args, **kwargs)

        def plot(self, *args, **kwargs):
            lines = super(RadarAxes, self).plot(*args, **kwargs)
            for line in lines:
                self._close_line(line)

        def _close_line(self, line):
            x, y = line.get_data()
            # FIXME: markers at x[0], y[0] get doubled-up
            if x[0] != x[-1]:
                x = np.concatenate((x, [x[0]]))
                y = np.concatenate((y, [y[0]]))
                line.set_data(x, y)

        def set_varlabels(self, labels):
            self.set_thetagrids(theta * 180 / np.pi, labels)

        def _gen_axes_patch(self):
            verts = unit_poly_verts(theta)
            return plt.Polygon(verts, closed=True, edgecolor='k')

        def _gen_axes_spines(self):
            spine_type = 'circle'
            verts = unit_poly_verts(theta)
            verts.append(verts[0])
            path = Path(verts)
            spine = Spine(self, spine_type, path)
            spine.set_transform(self.transAxes)
            return {'polar': spine}

    register_projection(RadarAxes)
    return theta

'''
def radar_graph(header, labels=[], leg=[], case=[], comp1=[], comp2=[], comp3=[]):
    N = len(labels)
    theta = _radar_factory(N)
    fig = plt.figure(figsize=(8, 7))
    fig.subplots_adjust(left=0, wspace=0.25, hspace=0.20, top=0.85, bottom=0.05)
    ax = fig.add_subplot(1, 1, 1, projection='radar')
    # plt.rgrids((1, 2, 3, 4, 5, 6, 7, 8, 9))
    ax.plot(theta, case, color='y')
    ax.fill(theta, case, color='y', alpha=0.5)
    ax.plot(theta, comp1, color='r')
    ax.plot(theta, comp2, color='g')
    ax.plot(theta, comp3, color='b')
    ax.set_varlabels(labels)
    ax.set_title(header, weight='bold', size='large', position=(0.5, 1.1),
                 horizontalalignment='center', verticalalignment='center')
    leg = (leg[0], leg[1], leg[2], leg[3])
    legend = plt.legend(leg, loc=(0.9, .95), labelspacing=0.1)
    plt.setp(legend.get_texts(), fontsize='small')

    plt.savefig(leg[0] + ".png", dpi=100)
    plt.show()
'''

def radar_graph(header, labels=[], leg=[], case=[], comp1=[]):
    N = len(labels)
    theta = _radar_factory(N)
    fig = plt.figure(figsize=(8, 7))
    fig.subplots_adjust(left=0, wspace=0.25, hspace=0.20, top=0.85, bottom=0.05)
    ax = fig.add_subplot(1, 1, 1, projection='radar')
    # plt.rgrids((1, 2, 3, 4, 5, 6, 7, 8, 9))
    ax.plot(theta, case, color='y')
    ax.fill(theta, case, color='y', alpha=0.5)
    ax.plot(theta, comp1, color='r')
    ax.set_varlabels(labels)
    ax.set_title(header, weight='bold', size='large', position=(0.5, 1.1),
                 horizontalalignment='center', verticalalignment='center')
    leg = (leg[0], leg[1])
    legend = plt.legend(leg, loc=(0.9, .95), labelspacing=0.1)
    plt.setp(legend.get_texts(), fontsize='small')

    plt.savefig(leg[0] + ".png", dpi=100)
    plt.show()