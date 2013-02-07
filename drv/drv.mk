SUBDIR = drv

MODULELIB := $(BUILDDIR)/lib$(MODULENAME).a

all: modulelib
	@#
modulelib: $(MODULELIB)

include $(BASEDIR)/build.mk
