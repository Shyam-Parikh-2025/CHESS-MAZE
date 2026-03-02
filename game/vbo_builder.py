import numpy as np
import math

vertices = []

def add_quad(a, b, c, d):
    vertices.extend(a)
    vertices.extend(b)
    vertices.extend(c)
    vertices.extend(a)
    vertices.extend(c)
    vertices.extend(d)

def box(x1, x2, y1, y2, z1, z2):
    # 6 faces
    # Front
    add_quad([x1,y1,z2],[x2,y1,z2],[x2,y2,z2],[x1,y2,z2])
    # Back
    add_quad([x2,y1,z1],[x1,y1,z1],[x1,y2,z1],[x2,y2,z1])
    # Left
    add_quad([x1,y1,z1],[x1,y1,z2],[x1,y2,z2],[x1,y2,z1])
    # Right
    add_quad([x2,y1,z2],[x2,y1,z1],[x2,y2,z1],[x2,y2,z2])
    # Top
    add_quad([x1,y2,z2],[x2,y2,z2],[x2,y2,z1],[x1,y2,z1])
    # Bottom
    add_quad([x1,y1,z1],[x2,y1,z1],[x2,y1,z2],[x1,y1,z2])

# ---------------------------------------
# Base (wide square pedestal)
# ---------------------------------------

box(-0.9, 0.9, 0.0, 0.2, -0.9, 0.9)
box(-1.0, 1.0, 0.2, 0.35, -1.0, 1.0)

# ---------------------------------------
# Lower Body (tapered square)
# ---------------------------------------

box(-0.7, 0.7, 0.35, 0.9, -0.7, 0.7)

# Waist indent
box(-0.5, 0.5, 0.9, 1.2, -0.5, 0.5)

# Upper flare
box(-0.75, 0.75, 1.2, 1.6, -0.75, 0.75)

# Neck
box(-0.45, 0.45, 1.6, 1.9, -0.45, 0.45)

# ---------------------------------------
# Crown Platform
# ---------------------------------------

box(-0.8, 0.8, 1.9, 2.1, -0.8, 0.8)

# ---------------------------------------
# Crown Teeth (8 blocks)
# ---------------------------------------

teeth = 8
radius = 0.8
tooth_width = 0.25
tooth_depth = 0.25
tooth_height = 0.5

for i in range(teeth):
    angle = 2 * math.pi * i / teeth
    cx = radius * math.cos(angle)
    cz = radius * math.sin(angle)

    box(
        cx - tooth_width/2,
        cx + tooth_width/2,
        2.1,
        2.1 + tooth_height,
        cz - tooth_depth/2,
        cz + tooth_depth/2
    )

# ---------------------------------------
# Top Orb (low poly sphere)
# ---------------------------------------

sphere_r = 0.25
center_y = 2.8
lat = 14
lon = 28

for i in range(lat):
    theta0 = math.pi * i / lat
    theta1 = math.pi * (i + 1) / lat

    for j in range(lon):
        phi0 = 2 * math.pi * j / lon
        phi1 = 2 * math.pi * (j + 1) / lon

        def sp(t,p):
            return [
                sphere_r * math.sin(t) * math.cos(p),
                center_y + sphere_r * math.cos(t),
                sphere_r * math.sin(t) * math.sin(p)
            ]

        p0 = sp(theta0,phi0)
        p1 = sp(theta0,phi1)
        p2 = sp(theta1,phi0)
        p3 = sp(theta1,phi1)

        add_quad(p0,p1,p3,p2)

vertices = np.array(vertices, dtype="float32")

print("Triangles:", len(vertices)//9)

with open("queen_vbo.txt", "w") as f:
    f.write("import numpy as np\n\n")
    f.write("QUEEN_VBO = np.array([\n")
    for i,v in enumerate(vertices):
        f.write(f"{v:.6f},")
        if (i+1)%9==0:
            f.write("\n")
    f.write("], dtype='float32')\n")

print("Saved to queen_vbo.txt")