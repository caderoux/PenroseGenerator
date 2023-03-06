import cmath
import math
import svgwrite
import sys

golden_ratio = (1 + math.sqrt(5)) / 2
interior_angle = math.pi/5
bounding_rects = []
bounding_rects.append([100 + 0 + 100j + 0j, 100 + 1400 + 100j + 3200j])
bounding_rects.append([100 + 1400 + 100j + 2000j, 100 + 2100 + 100j + (2000 + 458) * 1j])

# python .\penrose.py sun 9 sun_tiling.svg

class Point:
    def __init__(self, val, color):
        self.val = val
        self.color = color

# Get a vector V of magnitude size in the direction of vector P1P2
def project(P1, P2, size):
    return P1 + size * (P2 - P1) / abs(P2 - P1)

# Given a set of triangles, divide them into sub-triangles according to P2 Penrose Tiling substitution rules
def subdivide(triangles):
    result = []
    for color, A, B, C in triangles:
        # Check the color of the triangle.
        # 0 indicates acute Robinson triangle, 1 is obtuse Robinson triangle
        if color == 0:
            # The actute triangle subdivides into two acute triangles, and one obtuse triangle
            # So we will introduce two addintional vertices, P and Q
            pbisect_edge, qbisect_edge = C, B
            if B.color == A.color:
                pbisect_edge, qbisect_edge = B, C
            
            # The size of the edge A->P will be the distance between the longer edges of the actue triangle, 
            # or the short side of the triangle
            sz = abs(pbisect_edge.val - qbisect_edge.val)
            P = project(A.val, pbisect_edge.val, sz)
            # The vectors A->P and A->Q make up the long and short sides of an obtuse Robinson triangle, respectively
            # so the size from A->Q must be |A->P|/golden ratio
            Q = project(A.val, qbisect_edge.val, sz/golden_ratio)
            
            # Recolor the vertices according to substitution rules
            pP = Point(P, A.color)
            pQ = Point(Q, not A.color)
            pA = Point(A.val, not A.color)
            pC = Point(qbisect_edge.val, A.color)
            pB = Point(pbisect_edge.val, not A.color)
            
            result += [(0, pC, pQ, pP), (0, pC, pB, pP), (1,pA, pP, pQ)] 
        else: 
            # The obtuse triangle subdivides into one acute triangle and one obtuse triangle
            # So we will introduce one additional vertex, P

            # We want to bisect the edge A->C or A->B, we want the ending vertex to be the opposite color of the A vertex
            bisect_edge, unmodified_edge = C, B
            if B.color != A.color:
                bisect_edge, unmodified_edge = B, C
            
            # The size of the new edge will be the magnitude of A->X/golden_ratio
            P = project(A.val, bisect_edge.val, abs(A.val - bisect_edge.val) / golden_ratio)
            pP = Point(P, bisect_edge.color)
            result += [(1, bisect_edge, pP, unmodified_edge), (0, A, pP, unmodified_edge)]
    return result

# generates polar coordinates of two edges of a Robinson triangle 
#  
# The angle between them is acute angle of both triangles-- 36 degrees) 
#
def init_vertex_pair(x, s1, s2):
     A = cmath.rect(s1, x*interior_angle)     
     B = cmath.rect(s2, (x+1)*interior_angle)
     return A, B 

# Initial triangles will be in a star configuration, x number triangles @ size size
def initial_star(x, size, pos):
    triangles = []
    for i in range(x):
        # We will make an obtuse Robinson triangle
        # The short and long sides of Robinson triangle have ratio 1:golden ratio
        s1 = size if i%2 == 0 else size/golden_ratio
        s2 = size/golden_ratio if i%2 == 0 else size
        # They have a an angle of 36 degrees between them
        A, B = init_vertex_pair(i, s1, s2)
        triangles.append([1, Point(0j, 1), Point(A, i%2!=0), Point(B, i%2==0)])
    return triangles

# Initial triangles will be in a sun configuration, x number triangles @ size size
def initial_sun(x, size, pos):
    triangles = []
    for i in range(x):
        # We will make an acute Robinson triangle
        # They have the same size, but an angle of 36 degrees between them
        A, B = init_vertex_pair(i, size, size)
        if i%2 == 0: 
            A,B = B,A
        triangles.append([0, Point(0j + pos,0), Point(A + pos, 0), Point(B + pos, 1)])
    return triangles

def draw(triangles, fname, sz):
    dwg = svgwrite.Drawing(fname, profile='tiny', size=(2500, 3500))
    for t in triangles:
        color = 'rgb(64, 64, 64)' if t[0] == 1 else 'rgb(128, 128, 128)'
        coords = [p.val for p in t[1:]]
        points = [(p.real, p.imag) for p in coords]
        for rect in bounding_rects:
            if any((rect[0].real < p.real < rect[1].real) and (rect[0].imag < p.imag < rect[1].imag) for p in coords):
                dwg.add(dwg.polygon(points=points, fill = color, stroke='black', stroke_width=0.5))
                break
    dwg.save()
    print(abs(coords[0] - coords[1]))
    print(abs(coords[0] - coords[2]))
    print(abs(coords[1] - coords[2]))

if __name__ == "__main__":
    sz = 4250
    pos = 550 + 1375j
    if sys.argv[1] == 'star':
        t = initial_star(10, sz, pos)
    elif sys.argv[1] == 'sun':
        t = initial_sun(10, sz, pos)
    else:
        sys.exit(1)
    draw(t, 'none.svg', sz*2)
    for x in range(int(sys.argv[2])):
        t = subdivide(t)
        fname = sys.argv[3].split('.')[0] + '%s.svg'%(x)
        draw(t, fname, sz*2)
