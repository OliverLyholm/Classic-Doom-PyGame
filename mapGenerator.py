from PIL import Image
import struct
from pathlib import Path


# colors
black = (0, 0, 0)
white = (255, 255, 255)
red = (255, 0, 0)
green = (0, 255, 0)
blue = (0, 0, 255)

# doom tile size
TILE_SIZE = 64






def gridToDoom(x, y):
    return (
        x * TILE_SIZE,
        y * TILE_SIZE
    )



def generateMap(fileName):
    
    image = Image.open(fileName).convert("RGB")
    
    width, height = image.size
    
    floor = set()
    walls = set()
    player = None
    enemies = []
    doors = []
    
    for y in range(height):
        for x in range(width):
            color = image.getpixel((x, y))
            
            
            if color == black:
                floor.add((x, y))
            
            elif color == white:
                walls.add((x, y))
                
            elif color == red:
                floor.add((x, y))
                player = (x, y)
                
            elif color == green:
                floor.add((x, y))
                enemies.append((x, y))
                
            elif color == blue:
                floor.add((x, y))
                doors.append((x, y))

    return{
        "width": width,
        "height": height,
        "floor": floor,
        "walls": walls,
        "player": player,
        "enemies": enemies,
        "doors": doors
    }

def isWall(x, y, walls):
    return (x, y) in walls

def generateWallEdges(mapData):
    
    walls = mapData["walls"]
    floor = mapData["floor"]
    
    edges = []
    
    for x, y in floor:
        
        if isWall(x, y - 1, walls):
            edges.append((
                (x, y),
                (x + 1, y)
            ))
        
        if isWall(x, y + 1, walls):
            edges.append((
                (x + 1, y + 1),
                (x, y + 1)
            ))
        
        if isWall(x - 1, y, walls):
            edges.append((
                (x, y + 1),
                (x, y)
            ))
            
        if isWall( x + 1, y, walls):
            edges.append((
                (x + 1, y),
                (x + 1, y + 1)
            ))
    return edges


def generateVertices(edges):
    
    vertices = []
    vertexLookup = {}
    
    for edge in edges:
        for point in edge:
            
            if point not in vertexLookup:
                doom_x, doom_y = gridToDoom(
                    point[0],
                    point[1]
                )
                
                vertexLookup[point] = len(vertices )
                
                vertices.append(
                    (doom_x, doom_y)
                )
    return vertices, vertexLookup


def generateLineDefs(edges, vertexLookup):
    
    linedefs = []
    
    for edgeindex, (start, end) in enumerate(edges):
        
        startVertex = vertexLookup[start]
        endVertex = vertexLookup[end]
        
        linedefs.append({
            "start": startVertex,
            "end": endVertex,
            "flags": 0,
            "special": 0,
            "tag": 0,
            "right": -1,
            "left": -1
        })
    return linedefs


def generateSectors():
    
    sectors = []
    
    sectors.append({
        "floorHeight": 0,
        "ceilingHeight": 128,
        "floorTexture": "FLOOR0_1",
        "ceilingTexture": "CEIL1_1",
        "lightLevel": 255,
        "special": 0,
        "tag": 0
    })

    return sectors

def generateSideDefs(linedefs):
    
    sidedefs = []
    
    for linedef in linedefs:
        
        sidedefIndex = len(sidedefs)
        
        sidedefs.append({
            "xOffset": 0,
            "yOffset": 0,
            "upperTexture": "-",
            "lowerTexture": "-",
            "middleTexture": "STARTAN3",
            "sector": 0
        })
        
        linedef["right"] = sidedefIndex
        linedef["left"] = -1
        
    return sidedefs


def playerThing(player):
    
    if player is None:
        raise ValueError("Map does not contain a player start")
    
    x, y = player
    
    doom_x, doom_y = gridToDoom(
        
        x + 0.5,
        y + 0.5
    )
    
    return{
        "x": int(doom_x),
        "y": int(doom_y),
        "angle": 0,
        "type": 1
    }
    
def enemyThings(enemies):
    
    things = []
    
    for x, y in enemies:
        
        doom_x, doom_y = gridToDoom(
            x + 0.5,
            y + 0.5
        )
    
        things.append({
            "x": int(doom_x),
            "y": int(doom_y),
            "angle": 0,
            "type": 3004
        })
    return things

def generateThings(mapData):
    
    things = []
    
    player = mapData["player"]
    enemies = mapData["enemies"]
    
    if player is not None:
        things.append(
            playerThing(player)
        )
        
    things.extend(
        enemyThings(enemies)
    )

    return things

def generateSegs(linedefs):
    segs = []
    
    for linedefIndex, linedef in enumerate(linedefs):
        
        segs.append({
            "start": linedef["start"],
            "end": linedef["end"],
            "angle": 0,
            "linedef": linedefIndex,
            "direction": 0,
            "offset": 0
        })
    return segs
    
def generateSubsectors(segs):
    return[{
        "firstSeg": 0,
        "segCount": len(segs)
    }]


def generateNodes(subsectors):
    
    nodes = []
    
    nodes.append({
        "x": 0,
        "y": 0,
        "dx": 1,
        "dy": 0,

        "rightBox": {
            "top": 0,
            "bottom": 0,
            "left": 0,
            "right": 0
        },

        "leftBox": {
            "top": 0,
            "bottom": 0,
            "left": 0,
            "right": 0
        },

        "rightChild": 0x8000,
        "leftChild": 0x8000
    })
    return nodes

def generateBoundingBox (vertices):
    xs = [x for x, y in vertices]
    ys = [y for x, y in vertices]
    
    return{
        "top": max(ys),
        "bottom": min(ys),
        "left": min(xs),
        "right": max(xs)
    }

# build Lumps

def lumpName(name):
    return name.encode("ascii")[:8].ljust(8, b"\x00")

def textureName(name):
    return name.encode("ascii")[:8].ljust(8, b"\x00")


def buildVertexLump(vertices):
    data = bytearray()
    
    for x, y in vertices:
        data += struct.pack(
            "<hh",
            x,
            y
        )
    return bytes(data)

def buildLineDefLump(linedefs):
    
    data = bytearray()
    
    for line in linedefs:
        data += struct.pack(
            "<7h",
            line["start"],
            line["end"],
            line["flags"],
            line["special"],
            line["tag"],
            line["right"],
            line["left"]
        )
    return bytes(data)


def buildSideDefLump(sideDefs):
    
    data = bytearray()
    
    for side in sideDefs:
        data += struct.pack(
            "<hh",
            side["xOffset"],
            side["yOffset"]
        )
        
        data += textureName(
            side["upperTexture"]
        )

        data += textureName(
            side["lowerTexture"]
        )

        data += textureName(
            side["middleTexture"]
        )

        data += struct.pack(
            "<h",
            side["sector"]
        )
        
    return bytes(data)

def buildSectorLump(sectors):
    
    data = bytearray()
    
    for sector in sectors:
        
        data += struct.pack(
            "<hh",
            sector["floorHeight"],
            sector["ceilingHeight"]
        )

        data += textureName(
            sector["floorTexture"]
        )

        data += textureName(
            sector["ceilingTexture"]
        )

        data += struct.pack(
            "<hhh",
            sector["lightLevel"],
            sector["special"],
            sector["tag"]
        )
    return bytes(data)


def buildThingsLump(things):
    
    data = bytearray()
    
    for thing in things:
        
        data += struct.pack(
            "<5h",
            thing["x"],
            thing["y"],
            thing["angle"],
            thing["type"],
            thing.get("flags", 7)
        )
    return bytes(data)

def buildSegsLump(segs):
    
    data = bytearray()
    
    for seg in segs:
        data += struct.pack(
            "<6h",
            seg["start"],
            seg["end"],
            seg["angle"],
            seg["linedef"],
            seg["direction"],
            seg["offset"]
        )
    return bytes(data)
    
def buildSubSectorLump(subsectors):
    
    data = bytearray()
    
    for subsector in subsectors:
        data += struct.pack(
            "<hh",
            subsector["segCount"],
            subsector["firstSeg"]
        )
    return bytes(data)

def buildNodesLump(nodes):

    data = bytearray()

    for node in nodes:

        data += struct.pack(
            "<4h",
            node["x"],
            node["y"],
            node["dx"],
            node["dy"]
        )

        data += struct.pack(
            "<4h",
            node["rightBox"]["top"],
            node["rightBox"]["bottom"],
            node["rightBox"]["left"],
            node["rightBox"]["right"]
        )

        data += struct.pack(
            "<4h",
            node["leftBox"]["top"],
            node["leftBox"]["bottom"],
            node["leftBox"]["left"],
            node["leftBox"]["right"]
        )

        data += struct.pack(
            "<2H",
            node["rightChild"],
            node["leftChild"]
        )

    return bytes(data)


# Write wad file

def writeWad(filename, mapData):
    
    edges = generateWallEdges(mapData)

    vertices, vertexLookup = generateVertices(edges)

    linedefs = generateLineDefs(
        edges,
        vertexLookup
    )

    sidedefs = generateSideDefs(linedefs)

    sectors = generateSectors()

    things = generateThings(mapData)
    
    segs = generateSegs(linedefs)
    
    subsectors = generateSubsectors(segs)
    
    nodes = generateNodes(subsectors)

    
    lumps = []
    
    # map marker
    lumps.append((
        "MAP01",
        b""
    ))
    
    # mapData
    
    lumps.append((
        "THINGS",
        buildThingsLump(things)
    ))

    lumps.append((
        "LINEDEFS",
        buildLineDefLump(linedefs)
    ))

    lumps.append((
        "SIDEDEFS",
        buildSideDefLump(sidedefs)
    ))

    lumps.append((
        "VERTEXES",
        buildVertexLump(vertices)
    ))
    
    lumps.append((
        "SEGS",
        buildSegsLump(segs)
    ))
    
    lumps.append((
        "SSECTORS",
        buildSubSectorLump(subsectors)
    ))
    
    lumps.append((
    "NODES",
    buildNodesLump(nodes)
    ))


    lumps.append((
        "SECTORS",
        buildSectorLump(sectors)
    ))
    

    
    
    # Write wad
    
    with open(filename, "wb") as file:
        
        file.write(
            struct.pack(
                "<4sii",
                b"PWAD",
                len(lumps),
                0
            )
        )

        lumpEntries = []
        
        # write lump data
        
        for name, data in lumps:
            offset = file.tell()
            
            file.write(data)
            
            lumpEntries.append({
                "name": name,
                "offset": offset,
                "size": len(data)
            })
            
        # directory Start
        
        directoryOffset = file.tell()
        
        for lump in lumpEntries:
            
            file.write(
                struct.pack(
                    "<ii8s",
                    lump["offset"],
                    lump["size"],
                    lumpName(lump["name"])
                )
            )

        file.seek(0)
        
        file.write(
            struct.pack(
                "<4sii",
                b"PWAD",
                len(lumps),
                directoryOffset
            )
        )


# print wad info

def printWadInfo(filename):

    with open(filename, "rb") as file:

        identification = file.read(4)
        numLumps = struct.unpack("<i", file.read(4))[0]
        directoryOffset = struct.unpack("<i", file.read(4))[0]

        print("WAD type:", identification.decode("ascii"))
        print("Number of lumps:", numLumps)
        print("Directory offset:", directoryOffset)

        file.seek(directoryOffset)

        print("\nLumps:")

        for i in range(numLumps):

            offset, size, name = struct.unpack(
                "<ii8s",
                file.read(16)
            )

            name = name.rstrip(b"\x00").decode("ascii")

            print(
                f"{i}: {name:<8} "
                f"offset={offset:<6} "
                f"size={size}"
            )


# Test

if __name__ == "__main__":

    mapData = generateMap(
        "maps/level1.png"
    )

    wadFile = "maps/level1.wad"

    writeWad(
        wadFile,
        mapData
    )

    print("WAD generated!")

    printWadInfo(wadFile)


