class AnimatedWidget():
    def shareData(self, **kwargs):
        """
        @param **kwargs are the arguments to be passed to the main widget
        iterator
        """
        for k, v in kwargs.items():
            setattr(self, k, v)

    def loop_guard(self):
        self.i %= self.iterations

    def parameter_check(self):
        """
        parameter_check function should define minimum number and list
        of parameters used by widgets. This function provides a proper
        way to verify if widget has received every chunk of data it
        needs in order to be operational
        """
        _MISSING_FLAG_ = False
        for attribute in self._MINIMUM_PARAMS_:
            try:
                getattr(self, attribute)
            except AttributeError:
                _MISSING_FLAG_ = True
                msg = "There is an attribute missing: {}".format(attribute)
                print(msg)
        return _MISSING_FLAG_

    def set_i(self, value):
        """
        This is iterating setter. Function set_i should provide
        a neat way to change the current data of Widget and then
        refresh it immediately.
        """
        pass
