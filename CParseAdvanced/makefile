# location of the Python header files
PYTHON_VERSION = 3.7m
PYTHON_INCLUDE = /usr/include/python$(PYTHON_VERSION)
# location of the Boost Python include files and library
BOOST_INC = /usr/include
BOOST_LIB = /usr/lib
# this fucker
BOOST_PY = -lboost_python3 -lboost_numpy3
# compile mesh classes
TARGET = AdvParser
CVER = -std=c++17

$(TARGET).so: $(TARGET).o
	g++ $(CVER) -shared -Wl,--export-dynamic $(TARGET).o -L$(BOOST_LIB) $(BOOST_PY) $(BOOST_FS) -L/usr/lib/python$(PYTHON_VERSION)/config -lpython$(PYTHON_VERSION) -o $(TARGET).so
$(TARGET).o: $(TARGET).cpp
	g++ $(CVER) -I$(PYTHON_INCLUDE) -I$(BOOST_INC) -fPIC -c $(TARGET).cpp