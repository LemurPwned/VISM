class AnimatedWidget():
    WIDGET_ID = 0
    def shareData(self, **kwargs):
        """
        @param **kwargs are the arguments to be passed to the main widget
        iterator
        """
        for k, v in kwargs.items():
            setattr(self, k, v)

    def handleOptionalData(self):
        """
        needs to handle all optional data that are stored in
        json file
        please implement
        """
        pass

    def loop_guard(self):
        self.i %= self.iterations

    def set_i(self, value, trigger=False, record=False):
        """
        This is iterating setter. Function set_i should provide
        a neat way to change the current data of Widget and then
        refresh it immediately.
        """
        pass

    def receivedOptions(self):
        self.normalize = self.options[0]
        self.subsampling = int(self.options[1])
        if self.subsampling == 0:
            self.subsampling = 1
        self.layer = self.options[2]
        self.scale = int(self.options[3])
        self.vector_set = self.options[4]
        self.color_policy_type = self.options[5]
        self.hyperContrast = self.options[6]
        try:    
            # only arrows have resolution
            self.resolution = self.options[7]
        except IndexError:
            pass

    def initial_transformation(self):
        pass