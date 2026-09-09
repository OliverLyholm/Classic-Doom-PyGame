import ctypes
import time
from pathlib import Path
from collections import deque

import pygame


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
        
        self.key_queue = deque()

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
        if not self.key_queue:
            return 0
        
        key_pressed, key = self.key_queue.popleft()
        
        pressed[0] = key_pressed
        doom_key[0] = key
        return 1

    def _set_window_title(self, title):
        if title:
            try:
                print(
                    "Doom title:",
                    title.decode("utf-8")
                )
            except UnicodeDecodeError:
                pass
    
    
    # Key functions
    
    def handle_event(self, event):

        if event.type == pygame.KEYDOWN:

            doom_key = self._translate_key(event.key)

            if doom_key is not None:
                self.key_queue.append((1, doom_key))

        elif event.type == pygame.KEYUP:

            doom_key = self._translate_key(event.key)

            if doom_key is not None:
                self.key_queue.append((0, doom_key))

        elif event.type == pygame.MOUSEBUTTONDOWN:

            if event.button == 1:
                self.key_queue.append((1, 0xA3))

        elif event.type == pygame.MOUSEBUTTONUP:

            if event.button == 1:
                self.key_queue.append((0, 0xA3))

    
    def _translate_key(self, key):


    # Movement


    # Forward
        if key == pygame.K_w:
            return 0xAD

        if key == pygame.K_UP:
            return 0xAD

        # Backward
        if key == pygame.K_s:
            return 0xAF

        if key == pygame.K_DOWN:
            return 0xAF

        # Strafe left
        if key == pygame.K_a:
            return 0xA0

        # Strafe right
        if key == pygame.K_d:
            return 0xA1
        
        if key == pygame.K_LSHIFT:
            return 0xB6



        # Turning


        if key == pygame.K_q:
            return 0xAC

        if key == pygame.K_e:
            return 0xAE


        # Actions


        # Fire
        if key == pygame.K_LCTRL:
            return 0xA3

        # Use / open doors
        if key == pygame.K_SPACE:
            return 0xA2


        # Menu


        if key == pygame.K_ESCAPE:
            return 27

        if key == pygame.K_RETURN:
            return 13


        # Automap


        if key == pygame.K_TAB:
            return 9


        # Weapon selection


        if key == pygame.K_1:
            return ord("1")

        if key == pygame.K_2:
            return ord("2")

        if key == pygame.K_3:
            return ord("3")

        if key == pygame.K_4:
            return ord("4")

        if key == pygame.K_5:
            return ord("5")

        if key == pygame.K_6:
            return ord("6")

        if key == pygame.K_7:
            return ord("7")

        return None



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
