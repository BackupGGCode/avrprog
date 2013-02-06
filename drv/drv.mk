SUBDIR = drv

override BUILDDIR := $(BUILDDIR)/$(SUBDIR)/$(MODULENAME)

MODULELIB := $(BUILDDIR)/lib$(MODULENAME).a

all: $(MODULELIB)

include $(BASEDIR)/build.mk
