SRC_COMMON	= bitBoard.cpp book.cpp cluster.cpp clustertt.cpp computerPlayer.cpp \
		  endGameEval.cpp evaluate.cpp game.cpp history.cpp humanPlayer.cpp \
		  killerTable.cpp kpkTable.cpp krkpTable.cpp krpkrTable.cpp \
		  largePageAlloc.cpp material.cpp move.cpp moveGen.cpp numa.cpp \
		  parameters.cpp parallel.cpp piece.cpp polyglot.cpp \
		  position.cpp search.cpp tbgen.cpp tbprobe.cpp textio.cpp \
		  transpositionTable.cpp treeLogger.cpp \
		  util/logger.cpp util/random.cpp util/timeUtil.cpp util/util.cpp \
		  syzygy/rtb-probe.cpp

SRC_UTIL_COMMON = bookbuild.cpp gametree.cpp proofgame.cpp

SRC	= $(SRC_COMMON) enginecontrol.cpp texel.cpp tuigame.cpp uciprotocol.cpp

SRC_GTB = gtb/compression/lzma/Lzma86Dec.c gtb/compression/lzma/LzFind.c \
	  gtb/compression/lzma/Lzma86Enc.c gtb/compression/lzma/LzmaDec.c \
	  gtb/compression/lzma/Alloc.c gtb/compression/lzma/Bra86.c \
	  gtb/compression/lzma/LzmaEnc.c gtb/compression/wrap.c gtb/gtb-dec.c \
	  gtb/gtb-att.c gtb/sysport/sysport.c gtb/gtb-probe.c

SRC_TEST	= bitBoardTest.cpp pieceTest.cpp bookTest.cpp positionTest.cpp \
	          computerPlayerTest.cpp searchTest.cpp evaluateTest.cpp tbTest.cpp \
	          gameTest.cpp tbgenTest.cpp historyTest.cpp texelTest.cpp \
	          killerTableTest.cpp textioTest.cpp moveGenTest.cpp \
	          transpositionTableTest.cpp moveTest.cpp treeLoggerTest.cpp \
	          parallelTest.cpp polyglotTest.cpp utilTest.cpp

SRC_UTIL	= bookbuild.cpp chesstool.cpp gametree.cpp posgen.cpp spsa.cpp \
		  proofgame.cpp matchbookcreator.cpp \
		  test/bookBuildTest.cpp test/proofgameTest.cpp texelutil.cpp \
		  test/gameTreeTest.cpp

SRC_BOOKGUI	= bookbuildcontrol.cpp bookgui.cpp chessboard.cpp resource.cpp

INC		= -Isrc/gtb/sysport -Isrc/gtb/compression -Isrc/gtb/compression/lzma
INC_TEST	= -Itest/cute -Isrc
INC_UTIL	= -Iutil/cute -Isrc -Iutil/src
INC_BOOKGUI	= -Isrc -Iutil/src

# The following preprocessor symbols can be defined to enable CPU, OS and compiler
# specific features:
#
# -DHAS_BMI2        : Use BMI2 instructions to speed up move generation. Requires
#                     the gcc compiler and a CPU that supports BMI2 instructions.
#	              The compiler flag '-mbmi2' must be used when HAS_BMI2 is defined.
#
# -DHAS_POPCNT      : Use CPU popcount instructions to speed up counting of number of
#                     1 bits in a bitboard object. Requires a compiler that supports the
#                     __builtin_popcountl() function and a CPU that supports the
#                     corresponding machine code instruction.
#
# -DHAS_CTZ         : Use a special CPU instruction to find the first 1 bit in a bitboard
#                     object. Requires a compiler that supports the __builtin_ctzl function
#                     and a CPU that supports the corresponding machine code instruction.
#
# -DHAS_PREFETCH    : Use CPU prefetch instructions to speed up hash table access. Requires
#                     a compiler that supports the __builtin_prefetch() function and a CPU
#                     that supports the corresponding machine code instruction.
#
# -DHAS_RT          : Use the posix clock_gettime() function to get the current time
#                     with nanosecond resolution. When used, "-lrt" may have to be added to
#                     the linker flags.
#
# -DNUMA            : Optimize thread affinity and memory allocation when running on
#                     NUMA hardware.
#
# -DUSE_LARGE_PAGES : Use large pages when allocating memory for the transposition table,
#                     if supported by the operating system.
#
# -DCLUSTER         : Use MPI to distribute the search to several computers connected
#                     in a cluster.

# Definitions used by the "texel" target
CXX_DEF		= g++
FLAGS_DEF	= -O3 -Wall -Wno-misleading-indentation -pthread $(INC)
CXXFLAGS_DEF	= -std=c++11 $(FLAGS_DEF)
CXXFLAGS_UTIL_DEF = -fopenmp
CXXFLAGS_BOOKGUI_DEF = $$(pkg-config gtkmm-3.0 --cflags)
CC_DEF		= gcc
CFLAGS_DEF	= $(FLAGS_DEF)
LDFLAGS_DEF	= -pthread
LDFLAGS_UTIL_DEF = -lrt -larmadillo -lgsl -fopenmp
LDFLAGS_BOOKGUI_DEF = $$(pkg-config gtkmm-3.0 --libs) -lfreetype
STRIP_DEF	= strip
OBJS_COMMON_DEF	= $(patsubst %.cpp,objdef/%.o,$(SRC_COMMON))
OBJS_UTIL_COMMON_DEF = $(patsubst %.cpp,objdef/%.o,$(SRC_UTIL_COMMON))
OBJS_DEF	= $(patsubst %.cpp,objdef/%.o,$(SRC))
OBJS_C_DEF	= $(patsubst %.c,objdef/%.o,$(SRC_GTB))
OBJS_TEST_DEF   = $(patsubst %.cpp,objdef/%.o,$(SRC_TEST))
OBJS_UTIL_DEF   = $(patsubst %.cpp,objdef/%.o,$(SRC_UTIL))
OBJS_BOOKGUI_DEF = $(patsubst %.cpp,objdef/%.o,$(SRC_BOOKGUI))
#FLAGS_DEF	+= -DNUMA
#LDFLAGS_DEF	+= -lnuma


# Definitions used by the "texel32" and "texel64" targets
#CXX		= mpic++
CXX		= g++
FLAGS		= -O3 -Wall -pthread $(INC) -march=corei7 -Wno-misleading-indentation \
		  -DHAS_CTZ -DHAS_POPCNT -DHAS_PREFETCH -DHAS_RT -DUSE_LARGE_PAGES -fno-PIC
CXXFLAGS	= -std=c++11 $(FLAGS)
#CC		= mpicc
CC		= gcc
CFLAGS		= $(FLAGS)
LDFLAGS		= -pthread -lrt
STRIP		= strip
OBJS_32		= $(patsubst %.cpp,obj32/%.o,$(SRC))
OBJS_64		= $(patsubst %.cpp,obj64/%.o,$(SRC))
OBJS_C_32	= $(patsubst %.c,obj32/%.o,$(SRC_GTB))
OBJS_C_64	= $(patsubst %.c,obj64/%.o,$(SRC_GTB))
#FLAGS		+= -DNUMA -DCLUSTER
#LDFLAGS	+= -lnuma


# Definitions used by the "texel64.exe" target
CXX_WIN 	= x86_64-w64-mingw32-g++
FLAGS_WIN	= -O3 -Wall -pthread $(INC) -march=corei7 -Wno-misleading-indentation \
		  -DHAS_CTZ -DHAS_POPCNT -DHAS_PREFETCH -DHAS_RT -DUSE_LARGE_PAGES -DNUMA -D_WIN32_WINNT=0x0601
CXXFLAGS_WIN	= -std=c++11 $(FLAGS_WIN)
CC_WIN		= x86_64-w64-mingw32-gcc
CFLAGS_WIN	= $(FLAGS_WIN)
LDFLAGS_WIN	= -pthread
STRIP_WIN	= x86_64-w64-mingw32-strip
OBJS_W64 	= $(patsubst %.cpp,objw64/%.o,$(SRC))
OBJS_C_W64 	= $(patsubst %.c,objw64/%.o,$(SRC_GTB))

# Definitions used by the "texel64bmi.exe" target
CXX_WINBMI 	= x86_64-w64-mingw32-g++
FLAGS_WINBMI	= -O3 -Wall -pthread $(INC) -march=corei7 -Wno-misleading-indentation \
		  -DHAS_CTZ -DHAS_POPCNT -DHAS_PREFETCH -DHAS_RT -DUSE_LARGE_PAGES -DNUMA \
                  -D_WIN32_WINNT=0x0601 -DHAS_BMI2 -mbmi2
CXXFLAGS_WINBMI	= -std=c++11 $(FLAGS_WINBMI)
CC_WINBMI	= x86_64-w64-mingw32-gcc
CFLAGS_WINBMI	= $(FLAGS_WINBMI)
LDFLAGS_WINBMI	= -pthread
STRIP_WINBMI	= x86_64-w64-mingw32-strip
OBJS_W64BMI 	= $(patsubst %.cpp,objw64bmi/%.o,$(SRC))
OBJS_C_W64BMI 	= $(patsubst %.c,objw64bmi/%.o,$(SRC_GTB))

# Definitions used by the "texel64cl.exe" target
CXX_WINCL 	= x86_64-w64-mingw32-g++
FLAGS_WINCL	= -O3 -Wall -pthread $(INC) -march=corei7 -Wno-misleading-indentation \
		  -DHAS_CTZ -DHAS_POPCNT -DHAS_PREFETCH -DHAS_RT -DUSE_LARGE_PAGES -DNUMA \
                  -D_WIN32_WINNT=0x0601 -DCLUSTER -I$(MINGW_MPI)/include
CXXFLAGS_WINCL	= -std=c++11 $(FLAGS_WINCL)
CC_WINCL	= x86_64-w64-mingw32-gcc
CFLAGS_WINCL	= $(FLAGS_WINCL)
LDFLAGS_WINCL	= -pthread $(MINGW_MPI)/libmsmpi.a
STRIP_WINCL	= x86_64-w64-mingw32-strip
OBJS_W64CL 	= $(patsubst %.cpp,objw64cl/%.o,$(SRC))
OBJS_C_W64CL 	= $(patsubst %.c,objw64cl/%.o,$(SRC_GTB))

# Definitions used by the "texel64amd.exe" target
CXX_WINAMD 	= x86_64-w64-mingw32-g++
FLAGS_WINAMD	= -O3 -Wall -pthread $(INC) -march=athlon64-sse3 -mpopcnt -Wno-misleading-indentation \
		  -DHAS_CTZ -DHAS_POPCNT -DHAS_PREFETCH -DHAS_RT -DNUMA
CXXFLAGS_WINAMD	= -std=c++11 $(FLAGS_WINAMD)
CC_WINAMD	= x86_64-w64-mingw32-gcc
CFLAGS_WINAMD	= $(FLAGS_WINAMD)
LDFLAGS_WINAMD	= -pthread
STRIP_WINAMD	= x86_64-w64-mingw32-strip
OBJS_W64AMD 	= $(patsubst %.cpp,objw64amd/%.o,$(SRC))
OBJS_C_W64AMD 	= $(patsubst %.c,objw64amd/%.o,$(SRC_GTB))

# Definitions used by the "texel64old.exe" target
CXX_WINOLD 	= x86_64-w64-mingw32-g++
FLAGS_WINOLD	= -O3 -Wall -Wno-misleading-indentation -pthread $(INC) -DHAS_RT -DNUMA
CXXFLAGS_WINOLD	= -std=c++11 $(FLAGS_WINOLD)
CC_WINOLD	= x86_64-w64-mingw32-gcc
CFLAGS_WINOLD	= $(FLAGS_WINOLD)
LDFLAGS_WINOLD	= -pthread
STRIP_WINOLD	= x86_64-w64-mingw32-strip
OBJS_W64OLD 	= $(patsubst %.cpp,objw64old/%.o,$(SRC))
OBJS_C_W64OLD 	= $(patsubst %.c,objw64old/%.o,$(SRC_GTB))

# Definitions used by the "texel32.exe" target
CXX_WIN32 	= i686-w64-mingw32-g++
FLAGS_WIN32	= -O3 -Wall -pthread $(INC) -march=athlon64-sse3 -mpopcnt -Wno-misleading-indentation \
                  -DHAS_CTZ -DHAS_POPCNT -DHAS_PREFETCH -DHAS_RT
CXXFLAGS_WIN32	= -std=c++11 $(FLAGS_WIN32)
CC_WIN32	= i686-w64-mingw32-gcc
CFLAGS_WIN32	= $(FLAGS_WIN32)
LDFLAGS_WIN32	= -pthread
STRIP_WIN32	= i686-w64-mingw32-strip
OBJS_W32 	= $(patsubst %.cpp,objw32/%.o,$(SRC))
OBJS_C_W32 	= $(patsubst %.c,objw32/%.o,$(SRC_GTB))

# Definitions used by the "texel32old.exe" target
CXX_WIN32OLD 	= i686-w64-mingw32-g++
FLAGS_WIN32OLD	= -O3 -Wall -Wno-misleading-indentation -pthread $(INC) -DHAS_RT
CXXFLAGS_WIN32OLD = -std=c++11 $(FLAGS_WIN32OLD)
CC_WIN32OLD 	= i686-w64-mingw32-gcc
CFLAGS_WIN32OLD	= $(FLAGS_WIN32OLD)
LDFLAGS_WIN32OLD = -pthread
STRIP_WIN32OLD	= i686-w64-mingw32-strip
OBJS_W32OLD 	= $(patsubst %.cpp,objw32old/%.o,$(SRC))
OBJS_C_W32OLD 	= $(patsubst %.c,objw32old/%.o,$(SRC_GTB))

# Definitions used by the "texel-arm" target
CXX_ARM 	= arm-linux-androideabi-g++
FLAGS_ARM	= -O3 -Wall -pthread $(INC) -mthumb -march=armv7-a \
		  -DHAS_CTZ -DHAS_PREFETCH -DHAS_RT
CXXFLAGS_ARM	= -std=c++11 $(FLAGS_ARM)
CC_ARM		= arm-linux-androideabi-gcc
CFLAGS_ARM	= $(FLAGS_ARM)
LDFLAGS_ARM	= -pthread -mthumb -march=armv7-a
STRIP_ARM 	= arm-linux-androideabi-strip
OBJS_ARM 	= $(patsubst %.cpp,objarm/%.o,$(SRC))
OBJS_C_ARM 	= $(patsubst %.c,objarm/%.o,$(SRC_GTB))

# Definitions used by the "texel-arm64" target
CXX_ARM64 	= aarch64-linux-android-g++
FLAGS_ARM64	= -O3 -Wall -pthread $(INC) -march=armv8-a -fPIE \
		  -DHAS_CTZ -DHAS_PREFETCH -DHAS_RT
CXXFLAGS_ARM64	= -std=c++11 $(FLAGS_ARM64)
CC_ARM64	= aarch64-linux-android-gcc
CFLAGS_ARM64	= $(FLAGS_ARM64)
LDFLAGS_ARM64	= -pthread -march=armv8-a -fPIE -pie
STRIP_ARM64 	= aarch64-linux-android-strip
OBJS_ARM64 	= $(patsubst %.cpp,objarm64/%.o,$(SRC))
OBJS_C_ARM64 	= $(patsubst %.c,objarm64/%.o,$(SRC_GTB))

ALL_EXE = texel64 texel-arm texel-arm64 texel64bmi.exe texel64.exe texel64cl.exe texel64amd.exe \
          texel64old.exe texel32.exe texel32old.exe
TEST = texeltest
UTIL = texelutil

OBJS    = $(OBJS_32) $(OBJS_64) $(OBJS_ARM) $(OBJS_ARM64) $(OBJS_W64BMI) $(OBJS_W64) $(OBJS_W64CL) \
	  $(OBJS_W64AMD) $(OBJS_W64OLD) $(OBJS_W32) $(OBJS_W32OLD) $(OBJS_DEF)


default : texel
all	: $(ALL_EXE) $(TEST) $(UTIL)

strip   : FORCE $(ALL_EXE)
	$(STRIP) texel64
	$(STRIP_WINBMI) texel64bmi.exe
	$(STRIP_WIN) texel64.exe
	$(STRIP_WINCL) texel64cl.exe
	$(STRIP_WINAMD) texel64amd.exe
	$(STRIP_WINOLD) texel64old.exe
	$(STRIP_WIN32) texel32.exe
	$(STRIP_WIN32OLD) texel32old.exe
	$(STRIP_ARM) texel-arm
	$(STRIP_ARM64) texel-arm64

depend	: FORCE
	$(CXX_DEF) -MM $(CXXFLAGS_DEF) $(INC_TEST) $(INC_UTIL) $(patsubst %.cpp,src/%.cpp,$(SRC)) \
	$(patsubst %.c,src/%.c,$(SRC_GTB)) $(patsubst %.cpp,test/src/%.cpp,$(SRC_TEST)) \
	$(patsubst %.cpp,util/src/%.cpp,$(SRC_UTIL)) \
	$(patsubst %.cpp,bookgui/src/%.cpp,$(SRC_BOOKGUI)) | \
	sed -e 's!\(.*\):!obj64/\1 objarm/\1 objarm64/\1 objdef/\1 objw32/\1 objw32old/\1 objw64bmi/\1 objw64/\1 objw64cl/\1 objw64amd/\1 objw64old/\1:!' >.depend

dist	: texel.7z

texel.7z: FORCE $(ALL_EXE) strip
	(VER=$$(echo -e 'uci\nquit' | ./texel64 | grep 'id name' | awk '{print $$4}' | tr -d .) ; \
	 rm -f texel$${VER}.7z ; \
	 rm -rf texel$${VER} ; \
	 mkdir texel$${VER} ; \
	 cp --parents \
		Makefile .depend COPYING readme.txt src/*.?pp src/util/*.?pp \
		src/gtb/*.[ch] src/gtb/*.txt src/gtb/sysport/*.[ch] src/gtb/compression/*.[ch] \
		src/gtb/compression/lzma/*.[ch] src/syzygy/*.?pp \
		test/src/*.?pp test/cute/* util/src/*.?pp util/src/test/*.?pp util/cute/* \
		bookgui/src/*.?pp bookgui/src/*.xml bookgui/src/ChessCases.ttf \
		$(ALL_EXE) texelbook.bin texel$${VER}/; \
	 chmod -R ug+w texel$${VER} ; \
	 rm texel$${VER}/bookgui/src/resource.cpp ; \
	 7za a texel$${VER}.7z texel$${VER} ; \
	 rm -rf texel$${VER})

$(OBJS_DEF) : objdef/%.o : src/%.cpp
	@mkdir -p $$(dirname $@)
	$(CXX_DEF) $(CXXFLAGS_DEF) -c -o $@ $<

$(OBJS_C_DEF) : objdef/%.o : src/%.c
	@mkdir -p $$(dirname $@)
	$(CC_DEF) $(CFLAGS_DEF) -c -o $@ $<

$(OBJS_TEST_DEF) : objdef/%.o : test/src/%.cpp
	@mkdir -p $$(dirname $@)
	$(CXX_DEF) $(CXXFLAGS_DEF) $(INC_TEST) -c -o $@ $<

$(OBJS_UTIL_DEF) : objdef/%.o : util/src/%.cpp
	@mkdir -p $$(dirname $@)
	$(CXX_DEF) $(CXXFLAGS_DEF) $(CXXFLAGS_UTIL_DEF) $(INC_UTIL) -c -o $@ $<

$(OBJS_BOOKGUI_DEF) : objdef/%.o : bookgui/src/%.cpp
	@mkdir -p $$(dirname $@)
	$(CXX_DEF) $(CXXFLAGS_DEF) $(CXXFLAGS_BOOKGUI_DEF) $(INC_BOOKGUI) -c -o $@ $<

bookgui/src/resource.cpp : bookgui/src/gresource.xml bookgui/src/bookgui_glade.xml bookgui/src/ChessCases.ttf
	(cd bookgui/src ; \
	glib-compile-resources --generate-source --target=resource.cpp gresource.xml)

texel	 : $(OBJS_DEF) $(OBJS_C_DEF) Makefile
	$(CXX_DEF) $(LDFLAGS_DEF) -o $@ $(OBJS_DEF) $(OBJS_C_DEF)

texeltest : $(OBJS_COMMON_DEF) $(OBJS_C_DEF) $(OBJS_TEST_DEF) Makefile
	$(CXX_DEF) $(LDFLAGS_DEF) -o $@ $(OBJS_COMMON_DEF) $(OBJS_C_DEF) $(OBJS_TEST_DEF)

texelutil : $(OBJS_COMMON_DEF) $(OBJS_C_DEF) $(OBJS_UTIL_DEF) Makefile
	$(CXX_DEF) $(LDFLAGS_DEF) $(LDFLAGS_UTIL_DEF) -o $@ $(OBJS_COMMON_DEF) $(OBJS_C_DEF) $(OBJS_UTIL_DEF)

texelbookgui : $(OBJS_COMMON_DEF) $(OBJS_UTIL_COMMON_DEF) $(OBJS_C_DEF) $(OBJS_BOOKGUI_DEF) Makefile
	$(CXX_DEF) $(LDFLAGS_DEF) $(LDFLAGS_BOOKGUI_DEF) -o $@ $(OBJS_COMMON_DEF) \
	           $(OBJS_UTIL_COMMON_DEF) $(OBJS_C_DEF) $(OBJS_BOOKGUI_DEF)

$(OBJS_64) : obj64/%.o : src/%.cpp
	@mkdir -p $$(dirname $@)
	$(CXX) $(CXXFLAGS) -m64 -c -o $@ $<

$(OBJS_C_64) : obj64/%.o : src/%.c
	@mkdir -p $$(dirname $@)
	$(CC) $(CFLAGS) -m64 -c -o $@ $<

texel64	 : $(OBJS_64) $(OBJS_C_64) Makefile
	$(CXX) $(LDFLAGS) -m64 -o $@ $(OBJS_64) $(OBJS_C_64)

$(OBJS_32) : obj32/%.o : src/%.cpp
	@mkdir -p $$(dirname $@)
	$(CXX) $(CXXFLAGS) -m32 -c -o $@ $<

$(OBJS_C_32) : obj32/%.o : src/%.c
	@mkdir -p $$(dirname $@)
	$(CC) $(CFLAGS) -m32 -c -o $@ $<

texel32  : $(OBJS_32) $(OBJS_C_32) Makefile
	$(CXX) $(LDFLAGS) -m32 -o $@ $(OBJS_32) $(OBJS_C_32)



$(OBJS_W64BMI) : objw64bmi/%.o : src/%.cpp
	@mkdir -p $$(dirname $@)
	$(CXX_WINBMI) $(CXXFLAGS_WINBMI) -m64 -c -o $@ $<

$(OBJS_C_W64BMI) : objw64bmi/%.o : src/%.c
	@mkdir -p $$(dirname $@)
	$(CC_WINBMI) $(CFLAGS_WINBMI) -m64 -c -o $@ $<

texel64bmi.exe : $(OBJS_W64BMI) $(OBJS_C_W64BMI) Makefile
	$(CXX_WINBMI) $(LDFLAGS_WINBMI) -m64 -o $@ $(OBJS_W64BMI) $(OBJS_C_W64BMI) -static

$(OBJS_W64) : objw64/%.o : src/%.cpp
	@mkdir -p $$(dirname $@)
	$(CXX_WIN) $(CXXFLAGS_WIN) -m64 -c -o $@ $<

$(OBJS_C_W64) : objw64/%.o : src/%.c
	@mkdir -p $$(dirname $@)
	$(CC_WIN) $(CFLAGS_WIN) -m64 -c -o $@ $<

texel64.exe : $(OBJS_W64) $(OBJS_C_W64) Makefile
	$(CXX_WIN) $(LDFLAGS_WIN) -m64 -o $@ $(OBJS_W64) $(OBJS_C_W64) -static

$(OBJS_W64CL) : objw64cl/%.o : src/%.cpp
	@mkdir -p $$(dirname $@)
	$(CXX_WINCL) $(CXXFLAGS_WINCL) -m64 -c -o $@ $<

$(OBJS_C_W64CL) : objw64cl/%.o : src/%.c
	@mkdir -p $$(dirname $@)
	$(CC_WINCL) $(CFLAGS_WINCL) -m64 -c -o $@ $<

texel64cl.exe : $(OBJS_W64CL) $(OBJS_C_W64CL) Makefile
	$(CXX_WINCL) -m64 -o $@ $(OBJS_W64CL) $(OBJS_C_W64CL) $(LDFLAGS_WINCL) -static

$(OBJS_W64AMD) : objw64amd/%.o : src/%.cpp
	@mkdir -p $$(dirname $@)
	$(CXX_WINAMD) $(CXXFLAGS_WINAMD) -m64 -c -o $@ $<

$(OBJS_C_W64AMD) : objw64amd/%.o : src/%.c
	@mkdir -p $$(dirname $@)
	$(CC_WINAMD) $(CFLAGS_WINAMD) -m64 -c -o $@ $<

texel64amd.exe : $(OBJS_W64AMD) $(OBJS_C_W64AMD) Makefile
	$(CXX_WINAMD) $(LDFLAGS_WINAMD) -m64 -o $@ $(OBJS_W64AMD) $(OBJS_C_W64AMD) -static

$(OBJS_W64OLD) : objw64old/%.o : src/%.cpp
	@mkdir -p $$(dirname $@)
	$(CXX_WINOLD) $(CXXFLAGS_WINOLD) -m64 -c -o $@ $<

$(OBJS_C_W64OLD) : objw64old/%.o : src/%.c
	@mkdir -p $$(dirname $@)
	$(CC_WINOLD) $(CFLAGS_WINOLD) -m64 -c -o $@ $<

texel64old.exe : $(OBJS_W64OLD) $(OBJS_C_W64OLD) Makefile
	$(CXX_WINOLD) $(LDFLAGS_WINOLD) -m64 -o $@ $(OBJS_W64OLD) $(OBJS_C_W64OLD) -static


$(OBJS_W32) : objw32/%.o : src/%.cpp
	@mkdir -p $$(dirname $@)
	$(CXX_WIN32) $(CXXFLAGS_WIN32) -m32 -c -o $@ $<

$(OBJS_C_W32) : objw32/%.o : src/%.c
	@mkdir -p $$(dirname $@)
	$(CC_WIN32) $(CFLAGS_WIN32) -m32 -c -o $@ $<

texel32.exe : $(OBJS_W32) $(OBJS_C_W32) Makefile
	$(CXX_WIN32) $(LDFLAGS_WIN32) -m32 -o $@ $(OBJS_W32) $(OBJS_C_W32) -static

$(OBJS_W32OLD) : objw32old/%.o : src/%.cpp
	@mkdir -p $$(dirname $@)
	$(CXX_WIN32OLD) $(CXXFLAGS_WIN32OLD) -m32 -c -o $@ $<

$(OBJS_C_W32OLD) : objw32old/%.o : src/%.c
	@mkdir -p $$(dirname $@)
	$(CC_WIN32OLD) $(CFLAGS_WIN32OLD) -m32 -c -o $@ $<

texel32old.exe : $(OBJS_W32OLD) $(OBJS_C_W32OLD) Makefile
	$(CXX_WIN32OLD) $(LDFLAGS_WIN32OLD) -m32 -o $@ $(OBJS_W32OLD) $(OBJS_C_W32OLD) -static


$(OBJS_ARM) : objarm/%.o : src/%.cpp
	@mkdir -p $$(dirname $@)
	$(CXX_ARM) $(CXXFLAGS_ARM) -c -o $@ $<

$(OBJS_C_ARM) : objarm/%.o : src/%.c
	@mkdir -p $$(dirname $@)
	$(CC_ARM) $(CFLAGS_ARM) -c -o $@ $<

texel-arm  : $(OBJS_ARM) $(OBJS_C_ARM) Makefile
	$(CXX_ARM) $(LDFLAGS_ARM) -o $@ $(OBJS_ARM) $(OBJS_C_ARM)


$(OBJS_ARM64) : objarm64/%.o : src/%.cpp
	@mkdir -p $$(dirname $@)
	$(CXX_ARM64) $(CXXFLAGS_ARM64) -c -o $@ $<

$(OBJS_C_ARM64) : objarm64/%.o : src/%.c
	@mkdir -p $$(dirname $@)
	$(CC_ARM64) $(CFLAGS_ARM64) -c -o $@ $<

texel-arm64  : $(OBJS_ARM64) $(OBJS_C_ARM64) Makefile
	$(CXX_ARM64) $(LDFLAGS_ARM64) -o $@ $(OBJS_ARM64) $(OBJS_C_ARM64)


clean 	: 
	rm -rf $(OBJS) *~ obj32 obj64 objarm objarm64 objw64bmi objw64 objw64cl objw64amd
	rm -rf objw64old objw32 objw32old objdef
	rm -rf bookgui/src/resource.cpp

.PHONY	: clean dist FORCE

include .depend
