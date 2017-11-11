from Parser import Parser
from Canvas3D import Canvas3D
import numpy as np
import matplotlib.animation as animation
import matplotlib.pyplot as plt
from matplotlib import cm
import matplotlib as mpl

test_folder = "./data/firstData"

def _shareData():
    rawVectorData, omf_header, odt_data, stages = Parser.readFolder(test_folder)
    target_dict = {
                    'omf_header':  omf_header,
                    'multiple_data': rawVectorData,
                    'iterations': stages,
                    'current_layer': 0,
                    'title': '3dgraph',
                    'i': 0
    }
    new_canvas = Canvas3D()
    new_canvas.shareData(**target_dict)
    new_canvas.createPlotCanvas()
    new_canvas.loop()

def _anims():
    test_canvas = Canvas3D()
    multiple_data, omf_header, odt_data, stages = Parser.readFolder(test_folder)
    xc = int(omf_header['xnodes'])
    yc = int(omf_header['ynodes'])
    zc = int(omf_header['znodes'])
    current_layer = 0
    title = 'test'
    iterations = stages
    print(multiple_data.shape)
    multiple_data = np.array([x.reshape(zc,yc*xc,3)[current_layer]
                                    for x in multiple_data])
    print(multiple_data.shape)
    layer = np.array([test_canvas.calculate_layer_colors(x)
                            for x in multiple_data])
    layer = np.array([x.reshape(yc, xc) for x in layer])
    print("COLOR LAYER SHAPE {}".format(layer.shape))

    x = np.linspace(0, xc, xc)
    y = np.linspace(0, yc, yc)
    dx, dy = np.meshgrid(x,y)
    fig = plt.figure()
    c = layer[0]
    scat = plt.scatter(dx, dy,
                        c=c, cmap=cm.jet)
    fig.suptitle(title)
    fig.colorbar(scat)
    #fig.canvas.mpl_connect('button_press_event', onPress)
    ani = animation.FuncAnimation(fig, update,
                frames=range(iterations),
                fargs=(scat, layer))
    plt.show()

def update(i, scat, layer):
    print(i)
    scat.set_array(layer[i].reshape(35*35))
    return scat

if __name__ == "__main__":
    _shareData()
    #_anims()
