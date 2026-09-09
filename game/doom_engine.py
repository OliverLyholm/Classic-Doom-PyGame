import ctypes
import time
from pathlib import Path


class DGCallbacks(ctypes.Structure):
    pass


# ---------------------------------------------------------
# Project paths
# ---------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DLL_PATH = PROJECT_ROOT / "doom" / "libdoomgeneric.dll"


# ---------------------------------------------------------
# Callback types
# ---------------------------------------------------------

DGInit = ctypes.CFUNCTYPE(None)
DGDrawFrame = ctypes.CFUNCTYPE(None)
DGSleepMs = ctypes.CFUNCTYPE(None, ctypes.c_uint32)
DGGetTicksMs = ctypes.CFUNCTYPE(ctypes.c_uint32)

DGGetKey = ctypes.CFUNCTYPE(
    ctypes.c_int,
    ctypes.POINTER(ctypes.c_int),
    ctypes.POINTER(ctypes.c_ubyte),
)

DGSetWindowTitle = ctypes.CFUNCTYPE(
    None,
    ctypes.c_char_p,
)


# ---------------------------------------------------------
# Callback structure
# ---------------------------------------------------------

DGCallbacks._fields_ = [
    ("init", DGInit),
    ("draw_frame", DGDrawFrame),
    ("sleep_ms", DGSleepMs),
    ("get_ticks_ms", DGGetTicksMs),
    ("get_key", DGGetKey),
    ("set_window_title", DGSetWindowTitle),
]


class DoomEngine:

    def __init__(self, wad_path):

        if not DLL_PATH.exists():
            raise FileNotFoundError(
                f"Doom DLL not found:\n{DLL_PATH}"
            )

        wad_path = Path(wad_path).resolve()

        if not wad_path.exists():
            raise FileNotFoundError(
                f"WAD file not found:\n{wad_path}"
            )

        # -------------------------------------------------
        # Load DLL
        # -------------------------------------------------

        self.dll = ctypes.CDLL(str(DLL_PATH))

        # -------------------------------------------------
        # Function definitions
        # -------------------------------------------------

        self.dll.dg_set_callbacks.argtypes = [
            ctypes.POINTER(DGCallbacks)
        ]
        self.dll.dg_set_callbacks.restype = None

        self.dll.dg_create.argtypes = [
            ctypes.c_int,
            ctypes.POINTER(ctypes.c_char_p),
        ]
        self.dll.dg_create.restype = None

        self.dll.dg_tick.argtypes = []
        self.dll.dg_tick.restype = None

        self.dll.dg_screen_buffer.argtypes = []
        self.dll.dg_screen_buffer.restype = (
            ctypes.POINTER(ctypes.c_uint32)
        )

        self.dll.dg_resx.argtypes = []
        self.dll.dg_resx.restype = ctypes.c_int

        self.dll.dg_resy.argtypes = []
        self.dll.dg_resy.restype = ctypes.c_int

        # -------------------------------------------------
        # Get Doom resolution
        # -------------------------------------------------

        self.width = self.dll.dg_resx()
        self.height = self.dll.dg_resy()

        print(
            f"Doom resolution: "
            f"{self.width}x{self.height}"
        )

        # -------------------------------------------------
        # Keep Python callback objects alive
        # -------------------------------------------------

        self.callbacks = DGCallbacks(
            DGInit(self._init),
            DGDrawFrame(self._draw_frame),
            DGSleepMs(self._sleep_ms),
            DGGetTicksMs(self._get_ticks_ms),
            DGGetKey(self._get_key),
            DGSetWindowTitle(self._set_window_title),
        )

        # -------------------------------------------------
        # Register callbacks
        # -------------------------------------------------

        self.dll.dg_set_callbacks(
            ctypes.byref(self.callbacks)
        )

        # -------------------------------------------------
        # Build Doom command line
        # -------------------------------------------------

        argv = [
            b"doom",
            b"-iwad",
            str(wad_path).encode("utf-8"),
        ]

        self.argv = (
            ctypes.c_char_p * len(argv)
        )(*argv)

        # -------------------------------------------------
        # Start Doom
        # -------------------------------------------------

        self.dll.dg_create(
            len(argv),
            self.argv,
        )

    # =====================================================
    # Doom callbacks
    # =====================================================

    def _init(self):
        pass

    def _draw_frame(self):
        pass

    def _sleep_ms(self, milliseconds):
        time.sleep(milliseconds / 1000.0)

    def _get_ticks_ms(self):
        return int(time.monotonic() * 1000) & 0xFFFFFFFF

    def _get_key(self, pressed, doom_key):
        # Keyboard input will be added next.
        return 0

    def _set_window_title(self, title):
        if title:
            try:
                print(
                    "Doom title:",
                    title.decode("utf-8")
                )
            except UnicodeDecodeError:
                pass

    # =====================================================
    # Framebuffer
    # =====================================================

    def get_framebuffer(self):

        pointer = self.dll.dg_screen_buffer()

        size = self.width * self.height

        return ctypes.string_at(
            pointer,
            size * ctypes.sizeof(ctypes.c_uint32),
        )

    # =====================================================
    # Advance Doom
    # =====================================================

    def tick(self):
        self.dll.dg_tick()
