from PyQt5 import QtWidgets

class WidgetHandler:
    def __init__(self):
        self._groupBox = None
        self._button = None
        self._layout = None
        self._widget = None

    @property
    def groupBox(self):
        return self._groupBox

    @groupBox.setter
    def groupBox(self, value):
        self._groupBox = value

    @property
    def layout(self):
        return self._layout

    @layout.setter
    def layout(self, value):
        self._layout = value
        self._groupBox.setLayout(self._layout)
        self._layout.addWidget(self._button)

    @property
    def button(self):
        return self._button

    @button.setter
    def button(self, value):
        self._button = value
        self._button.setFixedSize(150, 50)

    @property
    def widget(self):
        return self._widget

    @widget.setter
    def widget(self, value):
        self._widget = value

    def isVisible(self):
        """Checks if Wisget is visible"""
        return self._groupBox.isVisible()

    def clearBox(self):
        """Clears whole Widget and leaves just groupBox with layout"""
        if self._groupBox == None:
            raise ValueError('groupBox must be initialized')

        for i in range(len(self._groupBox.children())):
            self._groupBox.children()[-1].deleteLater()

    def addWidget(self, widget):
        """Just adds new Widget to our Pane"""
        self._widget = widget

        if self._groupBox == None:
            raise ValueError("groupBox must be initialized")
        try:
            self._layout.addWidget(widget)
        except:
            raise ValueError("layout is not proper or argument is not a widget")
