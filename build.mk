BUILDDIR ?= build

MODULES ?=

BASEDIR ?= .

$(shell mkdir -p $(BUILDDIR))

BUILDDIR := $(realpath $(BUILDDIR))
BASEDIR := $(realpath $(BASEDIR))

OBJ := $(patsubst %.c,$(BUILDDIR)/%.o,$(SRC))
OBJ_LTO := $(patsubst %.c,$(BUILDDIR)/%.lto.o,$(SRC_LTO))

MODULELIBS := $(addprefix $(BUILDDIR)/,$(addsuffix .a,$(join $(addsuffix /lib,$(MODULES)),$(notdir $(MODULES)))))

DEP := $(addsuffix .d,$(OBJ) $(OBJ_LTO))

CLEANFILES += $(OBJ) $(OBJ_LTO) $(DEP) $(MODULELIB) $(ELF) $(HEX) $(BIN) $(SREC) $(DUMP) $(MAP)
CLEANFILES := $(wildcard $(CLEANFILES))

modules: $(MODULES)

.PHONY: all clean modules $(MODULES)

$(shell mkdir -p $(dir $(OBJ) $(OBJ_LTO)) $(MODULES))

$(MODULES):
	@echo "  MK     $@ $(MAKECMDGOALS)"
	$(V)+$(MAKE) -e -C $(BASEDIR)/$@ BUILDDIR=$(BUILDDIR) BASEDIR=$(BASEDIR) $(MAKECMDGOALS)

# $(BUILDDIR)/%.a:
# 	@echo "  MK     $(@D) $(@F)"
# 	$(V)+$(MAKE) -e -C $(@D) BUILDDIR=$(BUILDDIR) BASEDIR=$(BASEDIR) $(MAKECMDGOALS)

$(MODULELIB): $(OBJ) $(OBJ_LTO)
	@echo "  AR     $(@F) ($(<F))"
	$(V)$(AR) cur $@ $<

$(BUILDDIR)/%.o: %.c
	@echo "  CC     $(@F) ($(<F))"
	$(V)$(CC) $(CCFLAGS) -MD -MF $@.d $< -o $@

$(BUILDDIR)/%.lto.o: %.c
	@echo "  CC     $(@F) ($(<F))"
	$(V)$(CC) $(CCFLAGS) -MD -MF $@.d -flto $< -o $@

$(ELF): $(OBJ) $(OBJ_LTO) $(MODULELIBS)
	@echo "  LN     $(@F) ($(^F))"
	$(V)$(LN) $(LNFLAGS) -o $@ $^ -Wl,-Map=$(MAP)

clean: $(MODULES)
	@echo "  CLEAN  $(notdir $(CLEANFILES))"
	$(V)rm -f $(CLEANFILES)

-include $(DEP)

.PHONY: all hex bin srec dump dep meminfo clean modules $(MODULES)

$(shell mkdir -p $(dir $(OBJ) $(OBJ_LTO)) $(MODULES))
