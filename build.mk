BUILDDIR ?= build

MODULES ?=

BASEDIR ?= .

ifneq ($(MAKELEVEL),0)
	ECHOLEVEL := $(shell yes "\ " | head -n$(MAKELEVEL) | xargs echo)
endif

ifeq ($(MAKECMDGOALS),clean)
	MODULEGOAL := clean
endif

$(shell mkdir -p $(BUILDDIR))

BUILDDIR := $(realpath $(BUILDDIR))
BASEDIR := $(realpath $(BASEDIR))

OBJ := $(patsubst %.c,$(BUILDDIR)/%.o,$(SRC))
OBJ_LTO := $(patsubst %.c,$(BUILDDIR)/%.lto.o,$(SRC_LTO))

MODULELIBS := $(addprefix $(BUILDDIR)/,$(addsuffix .a,$(join $(addsuffix /lib,$(MODULES)),$(notdir $(MODULES)))))

DEP := $(addsuffix .d,$(OBJ) $(OBJ_LTO))

CLEANFILES += $(OBJ) $(OBJ_LTO) $(DEP) $(MODULELIB) $(ELF) $(HEX) $(BIN) $(SREC) $(DUMP) $(MAP)
CLEANFILES := $(wildcard $(CLEANFILES))

modules: $(MODULELIBS)

.PHONY: all clean distclean modules $(MODULELIBS)

$(shell mkdir -p $(dir $(OBJ) $(OBJ_LTO)))

$(MODULELIBS):
	@echo "  $(ECHOLEVEL)MAKE   $(subst $(BUILDDIR),,$(@D))"
	$(V)+$(MAKE) -e -C $(subst $(BUILDDIR),$(BASEDIR),$(@D)) BUILDDIR=$(@D) BASEDIR=$(BASEDIR) $(MODULEGOAL)

$(MODULELIB): $(OBJ) $(OBJ_LTO)
	@echo "  $(ECHOLEVEL)AR     $(@F) ($(^F))"
	$(V)$(AR) cur $@ $^

$(BUILDDIR)/%.o: %.c
	@echo "  $(ECHOLEVEL)CC     $(@F) ($(<F))"
	$(V)$(CC) $(CCFLAGS) -MD -MF $@.d $< -o $@

$(BUILDDIR)/%.lto.o: %.c
	@echo "  $(ECHOLEVEL)CC     $(@F) ($(<F))"
	$(V)$(CC) $(CCFLAGS) -MD -MF $@.d -flto $< -o $@

$(ELF): $(OBJ) $(OBJ_LTO) $(MODULELIBS)
	@echo "  $(ECHOLEVEL)LN     $(@F) ($(^F))"
	$(V)$(LN) $(LNFLAGS) -o $@ $^ -Wl,-Map=$(MAP)

clean: $(MODULELIBS)
	@echo "  $(ECHOLEVEL)CLEAN  $(notdir $(CLEANFILES))"
	$(V)rm -f $(CLEANFILES)

distclean: clean
	@echo "  $(ECHOLEVEL)DISTCLEAN $(notdir $(BUILDDIR))"
	$(V)rm -rf $(BUILDDIR)

-include $(DEP)

.PHONY: all hex bin srec dump dep meminfo clean modules $(MODULES)
