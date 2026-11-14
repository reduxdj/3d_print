"""Build a four-piece, two-color Ninjago-inspired costume helmet in Blender.

Open this file in Blender's Scripting workspace and choose Run Script (Alt-P).
Designed for Blender 4.5+; no add-on or third-party Python package is required.
All geometry coordinates are millimetres. Front is -Y; the back removes along +Y.
The photographs guide the styling; this is an approximation, not a scanned replica.

Sizing uses the confirmed 540 mm HEAD CIRCUMFERENCE plus radial fit allowance.
The original rear-panel cut is retained. Ribbon tails below it belong to the rear;
the band and upper knot remain with the front. Sixteen 6 x 3 mm magnet pairs:
eight across the top and four per sloped leading side edge. The crown stays with the front.

The front and back have white and cyan solid regions with coincident interfaces,
not painted surfaces. Import each matching STL pair as ONE multipart object.
The two main horns are independent cyan solids, glued into keyed blind sockets.
3MF files include base-material colors; assign actual filament slots in the slicer.
Never globally resize the finished model: that also resizes the magnet pockets.
Edit the dimensions here and regenerate instead.
"""

import bpy
import bmesh
import json
import math
import os
import struct
import xml.etree.ElementTree as ET
import zipfile
from datetime import datetime
from pathlib import Path
from mathutils import Vector


# ------------------------- EDIT THESE SETTINGS -------------------------
SIZE_MODE = "CIRCUMFERENCE"         # CIRCUMFERENCE or LITERAL_WIDTH
HEAD_CIRCUMFERENCE_MM = 540.0         # measured head, before clearance
LITERAL_OVERALL_WIDTH_MM = 540.0     # used only in LITERAL_WIDTH mode
HEAD_DEPTH_TO_WIDTH = 1.18            # head shape assumption: front/back vs side/side
FIT_CLEARANCE_MM = 5.0               # radial allowance for fit and thin padding
DESIGN_ENVELOPE_MM = 250.0           # construction reference; lower rim is trimmed
EYE_TOP_FROM_TOP_MM = 100.0          # measured from horn tips, NOT the white dome
EYE_MAX_HEIGHT_MM = 35.0             # tallest vertical portion of the opening
EYE_WIDTH_MM = 138.0
WALL_MM = 12.0                      # substantial costume shell; grows outward
NOSE_CLEARANCE_MM = 24.0            # local forward expansion of the INNER cavity
FACE_RELIEF_MM = 18.0               # projection at the nose corner, z=82 mm
MOUTH_VALLEY_DEPTH_MM = 14.0         # inward step at z=39 mm, from basic face
LOWER_EDGE_SETBACK_MM = 30.0         # lower edge retreats behind the basic face
REAR_RIM_RISE_MM = 55.0              # rear edge stops this far above the front lip
VENT_DIAMETER_MM = 5.0               # 2 mouth-channel vents + 2 beneath nose ridge
HORN_RAKE_DEG = 13.0                 # rearward rise of the newly lowered main fins
HORN_SPLAY_DEG = 18.0                # outward spread in the top view
FRONT_RIM_RISE_MM = 12.0             # shorter front, as marked in the overlay
MOUTH_HALF_WIDTH_MM = 62.0           # chevron ends before the cyan cheek pieces
BROW_END_Y_MM = -82.0              # front rim stops here; no band runs along the horn
BROW_FORWARD_MM = 4.0               # modest front-rim relief; avoid a deep projecting shelf
BROW_DIAMOND_SETBACK_MM = 10.0        # diamond point behind the front ridge
DIAMOND_RELIEF_SCALE = 0.70         # taper the diamond projection toward the crown
BROW_FRONT_HEIGHT_ADDITION_MM = 18.0  # extra height above the original brow contour
HORN_GLUE_CLEARANCE_MM = 0.20       # per-side clearance in the keyed glue sockets
HORN_GLUE_TAB_DEPTH_MM = 3.0        # integral keyed tabs; no extra hardware
HORN_ROOT_RELEASE_Y_MM = BROW_END_Y_MM+1.0
HORN_TIP_RIDGE_MM = 1.0             # retain a real fold through the blunt end
BROW_UPPER_EDGE_RADIUS_MM = 1.4      # geometric rounding of the rim, not just shading
BROW_UNDERSIDE_DROP_MM = 7.0         # cover the marked white strip above the eye
HORN_RIDGE_RELIEF_MM = 7.0          # actual longitudinal fold, tapering toward the tip
HORN_NOTCH_RADIUS_MM = 26.0         # shallow circular dip behind the front overlap
HORN_ROOT_EDGE_TRIM_MM = 7.0         # shave the marked outer root edge, fading into the blade
HORN_ROOT_SETBACK_MM = 8.0           # remove bulk along the forward horn attachment
HORN_ROOT_WIDTH_FACTOR = 0.50       # locally narrow the attachment; keep the blade straight
BROW_PEAK_HEIGHT_MM = 106.0          # triangular front peak above the highest eye edge
CREST_WIDTH_MM = 34.0                # broad stepped crown strip, measured across X
MAGNET_DIAMETER_MM = 6.0             # cylindrical disk magnets
MAGNET_THICKNESS_MM = 3.0
POCKET_DIAMETRAL_CLEARANCE_MM = 0.20
POCKET_GLUE_ALLOWANCE_MM = 0.10       # adhesive under magnet brings face flush
SEAM_GAP_MM = 0.30
ALIGNMENT_CLEARANCE_MM = 0.25         # radial clearance for the two guide pins
MAKE_FIT_COUPON = True
EXPORT_FILES = True
SAVE_BLEND = True
OUTPUT_DIRECTORY = str(Path(__file__).resolve().parent / "Design_Files")               # blank = timestamped folder beside this script
# ---------------------------------------------------------------------

# Environment overrides are useful for unattended validation; UI users can ignore.
SIZE_MODE = os.getenv("NINJAGO_SIZE_MODE", SIZE_MODE).upper()
OUTPUT_DIRECTORY = os.getenv("NINJAGO_OUTPUT_DIR", OUTPUT_DIRECTORY)
NS = "http://schemas.microsoft.com/3dmanufacturing/core/2015/02"
ET.register_namespace("", NS)


def log(message):
    print("[Ninjago mask] " + message, flush=True)


def validate_settings():
    if SIZE_MODE not in {"CIRCUMFERENCE", "LITERAL_WIDTH"}:
        raise ValueError("SIZE_MODE must be CIRCUMFERENCE or LITERAL_WIDTH")
    if not 450 <= HEAD_CIRCUMFERENCE_MM <= 700:
        raise ValueError("Head circumference is outside this template's 450-700 mm range")
    if not 220 <= DESIGN_ENVELOPE_MM <= 300:
        raise ValueError("This template supports heights from 220 to 300 mm")
    if not 6 <= WALL_MM <= 20:
        raise ValueError("This thick-shell revision supports WALL_MM from 6 to 20 mm")
    if not 0 < EYE_MAX_HEIGHT_MM <= 35:
        raise ValueError("The requested eye opening must be between 0 and 35 mm tall")
    if EYE_TOP_FROM_TOP_MM < 100:
        raise ValueError("The eye opening must start at least 100 mm below the top")
    if EYE_MAX_HEIGHT_MM < 20 or EYE_TOP_FROM_TOP_MM > 120:
        raise ValueError("This template's eye parameters need 20-35 mm height and 100-120 mm top offset")
    if MAGNET_DIAMETER_MM <= 0 or MAGNET_THICKNESS_MM <= 0:
        raise ValueError("Magnet dimensions must be positive")
    if not 0.15 <= SEAM_GAP_MM <= 0.8:
        raise ValueError("Use a seam gap from 0.15 to 0.8 mm")


def ellipse_perimeter(a, b):
    h = ((a - b) / (a + b)) ** 2
    return math.pi * (a + b) * (1 + 3 * h / (10 + math.sqrt(4 - 3 * h)))


validate_settings()
HEAD_A = HEAD_CIRCUMFERENCE_MM / ellipse_perimeter(1.0, HEAD_DEPTH_TO_WIDTH)
HEAD_B = HEAD_A * HEAD_DEPTH_TO_WIDTH
A = HEAD_A + FIT_CLEARANCE_MM + WALL_MM
B = HEAD_B + FIT_CLEARANCE_MM + WALL_MM
H = DESIGN_ENVELOPE_MM / 250.0
DOME_START = 150.0 * H
DOME_TOP = 215.0 * H + WALL_MM       # retain 215 mm inner crown headroom at default size
MODEL_TOP_Z = DOME_START+(DOME_TOP-DOME_START)*math.sqrt(1-.02**2)+18*.55+2
HATCH_TOP = MODEL_TOP_Z-EYE_TOP_FROM_TOP_MM+5
FRONT_SEAM = HATCH_TOP + SEAM_GAP_MM / 2
BACK_SEAM = HATCH_TOP - SEAM_GAP_MM / 2
HORN_TIP_Z = (184+173*math.tan(math.radians(HORN_RAKE_DEG)))*H
EYE_TOP = HORN_TIP_Z - EYE_TOP_FROM_TOP_MM
EYE_BOTTOM = EYE_TOP - EYE_MAX_HEIGHT_MM
X_SCALE = 1.0
TMP = None
SCENE = None
SIDE_SHADOW_CACHE = {}
SCRIPT_VERSION = "28.0"
MESH_CLEANUP_MM = 0.0001


def new_mesh(name, vertices, faces, cleanup=True):
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    TMP.objects.link(obj)
    if cleanup:fix_normals(obj)
    return obj


def fix_normals(obj):
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    original=bm.copy() if all(e.is_manifold for e in bm.edges) else None
    # Boolean intersections can leave coincident points and zero-area slivers.
    # 0.0001 mm is below print resolution; no voxel remesh or model scaling.
    bmesh.ops.remove_doubles(bm, verts=list(bm.verts), dist=MESH_CLEANUP_MM)
    bmesh.ops.dissolve_degenerate(bm, edges=list(bm.edges), dist=MESH_CLEANUP_MM)
    bmesh.ops.triangulate(bm, faces=list(bm.faces), quad_method="FIXED", ngon_method="EAR_CLIP")
    bmesh.ops.dissolve_degenerate(bm, edges=list(bm.edges), dist=MESH_CLEANUP_MM)
    # A conforming cut can contain legitimate very short edges. Never collapse
    # them when doing so would turn a closed solid into a non-manifold mesh.
    if original is not None and any(not e.is_manifold for e in bm.edges):
        bm.free();bm=original;original=None
        bmesh.ops.triangulate(bm,faces=list(bm.faces),quad_method="FIXED",ngon_method="EAR_CLIP")
    bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
    bm.to_mesh(obj.data)
    bm.free()
    if original is not None:original.free()
    obj.data.update()


def delete(obj):
    data = obj.data
    bpy.data.objects.remove(obj, do_unlink=True)
    if data.users == 0:
        bpy.data.meshes.remove(data)


def copy_obj(obj, name):
    result = obj.copy()
    result.data = obj.data.copy()
    result.name = name
    TMP.objects.link(result)
    return result


def active(obj):
    for item in bpy.context.selected_objects:
        item.select_set(False)
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj


def boolean(obj, cutter, operation="DIFFERENCE", remove=True, allow_empty=False):
    active(obj)
    mod = obj.modifiers.new(operation, "BOOLEAN")
    mod.operation = operation
    mod.solver = "MANIFOLD"
    mod.object = cutter
    modifier_name=mod.name
    result=bpy.ops.object.modifier_apply(modifier=modifier_name)
    if "FINISHED" not in result or obj.modifiers.get(modifier_name) is not None:
        raise RuntimeError(f"{operation} failed on {obj.name}, cutter {cutter.name}; geometry was not exported")
    fix_normals(obj)
    if remove:
        delete(cutter)
    if not obj.data.polygons and not allow_empty:
        raise RuntimeError(f"{operation} produced an empty mesh: {obj.name}")
    return obj


def cube(name, center, dimensions):
    x, y, z = center
    a, b, c = [d / 2 for d in dimensions]
    v = [(x + sx * a, y + sy * b, z + sz * c)
         for sx, sy, sz in [(-1,-1,-1), (1,-1,-1), (1,1,-1), (-1,1,-1),
                           (-1,-1,1), (1,-1,1), (1,1,1), (-1,1,1)]]
    return new_mesh(name, v, [(0,3,2,1), (4,5,6,7), (0,1,5,4),
                             (1,2,6,5), (2,3,7,6), (3,0,4,7)])


def cylinder_y(name, x, z, y0, y1, radius, radius_end=None, segments=64):
    """Capped cylinder (or cone) along the seam normal. Dimensions stay in mm."""
    if radius_end is None:
        radius_end = radius
    vertices = [(x + r * math.cos(i*2*math.pi/segments), y,
                 z + r * math.sin(i*2*math.pi/segments))
                for y, r in [(y0, radius), (y1, radius_end)]
                for i in range(segments)]
    faces = [tuple(reversed(range(segments))), tuple(range(segments, 2*segments))]
    faces += [(i, (i+1)%segments, (i+1)%segments+segments, i+segments)
              for i in range(segments)]
    return new_mesh(name, vertices, faces)


def lower_profile(z):
    # The lower rim does not contract: vertical dirt-bike-style chin and sides.
    return 1.0


def linear_sample(x,stations):
    if x<=stations[0][0]:return stations[0][1]
    for (a,v),(b,w) in zip(stations,stations[1:]):
        if x<=b:return v+(w-v)*(x-a)/(b-a)
    return stations[-1][1]


def face_ring_height(theta, nominal_z):
    """Carry the traced side-profile corners across the front as chevrons."""
    a=abs((theta+math.pi)%(2*math.pi)-math.pi)
    if nominal_z<=0 or nominal_z>=150*H:return nominal_z
    zh=nominal_z/H
    wave=28*H*min(a/.95,1)*min(1,max(0,(1.9-a)/.6))
    weight=zh/26 if zh<26 else (1 if zh<=82 else (150-zh)/68)
    return nominal_z+wave*weight


def face_relief(theta,z):
    # Broad nose planes, with a SHORT chevron groove confined to the front.
    a=abs((theta+math.pi)%(2*math.pi)-math.pi)
    if a>=1.30 or z>=150*H:return 0.0
    frontal=max(0,math.cos(a))**2
    edge=min(1.0,max(0,(1.30-a)/.2))
    stations=[(-15,-LOWER_EDGE_SETBACK_MM),(0,-LOWER_EDGE_SETBACK_MM),
              (34,-9),(42,-6),(82,FACE_RELIEF_MM),(110,0),(120,0),(150,0)]
    base=linear_sample(z,[(face_ring_height(theta,h*H),v) for h,v in stations])
    # Use the actual X coordinate to bound the groove, independently of fit.
    ex=2.5-.5*min(max(z/(145*H),0),1)
    x=A*abs(math.sin(a))**(2/ex)
    taper=min(1,max(0,(MOUTH_HALF_WIDTH_MM-x)/14))
    taper=taper*taper*(3-2*taper)
    valley=linear_sample(z,[(face_ring_height(theta,h*H),v) for h,v in
        [(-15,0),(34,0),(39,-MOUTH_VALLEY_DEPTH_MM+7.125),(42,0),(150,0)]])
    return (base+valley*taper)*frontal*edge

def nose_shift(theta,z):
    frontal=max(0,math.cos(theta))**6
    vertical=1.0 if z<=120*H else max(0,1-(z-120*H)/(45*H))
    return NOSE_CLEARANCE_MM*frontal*vertical+face_relief(theta,z)


def profile(z):
    if z <= DOME_START: return 1.0
    return math.sqrt(max(0,1-((z-DOME_START)/(DOME_TOP-DOME_START))**2))


def section_xy(theta,z,rx,ry,f):
    # Blend a broad, flatter lower face into an elliptical brow and crown.
    t=min(max(z/(145*H),0),1)
    exponent=2.5-.5*t
    st,ct=math.sin(theta),math.cos(theta)
    x=rx*f*math.copysign(abs(st)**(2/exponent),st)
    y=-ry*f*math.copysign(abs(ct)**(2/exponent),ct)-nose_shift(theta,z)
    return x,y


def hull(name,inset=0):
    rx,ry=A-inset,B-inset
    bottom=-15 if inset else 0
    rings=[(bottom,1.0)]
    if inset:rings.append((0,1.0))
    rings += [(z*H,1.0) for z in [12,26,34,36,39,42,54,68,75,78,82,87,91,95,99,110,114,120]]
    rings += [(i*DOME_START/28,1.0) for i in range(1,29) if i*DOME_START/28>120*H]
    rz=DOME_TOP-DOME_START-inset
    rings += [(DOME_START+rz*math.sin(i*math.pi/2/26),math.cos(i*math.pi/2/26)) for i in range(1,26)]
    n=160
    verts=[]
    for nominal_z,f in rings:
        for i in range(n):
            theta=i*2*math.pi/n;z=nominal_z
            z=face_ring_height(theta,z)
            x,y=section_xy(theta,z,rx,ry,f)
            if not inset:
                d=rear_ridge_offset(theta,z)
                x+=d*math.sin(theta);y-=d*math.cos(theta)
            verts.append((x,y,z))
    faces=[tuple(reversed(range(n)))]
    for j in range(len(rings)-1):
        faces += [(j*n+i,j*n+(i+1)%n,(j+1)*n+(i+1)%n,(j+1)*n+i) for i in range(n)]
    apex=len(verts);verts.append((0,0,DOME_TOP-inset))
    faces += [((len(rings)-1)*n+i,(len(rings)-1)*n+(i+1)%n,apex) for i in range(n)]
    return new_mesh(name,verts,faces)


def rear_ridge_offset(theta,z):
    a=abs((theta+math.pi)%(2*math.pi)-math.pi)
    fade=min(1,max(0,(a-1.8)/.35));fade=fade*fade*(3-2*fade)
    return linear_sample(z/H,[(-100,0),(78,0),(82,.8),(87,2),(91,2.4),(95,1),(99,0),(500,0)])*fade


def surface(theta,z,offset=0):
    offset+=rear_ridge_offset(theta,z)
    x,y=section_xy(theta,z,A,B,profile(z))
    return (x+offset*math.sin(theta),y-offset*math.cos(theta),z)


def patch_grid(name, rows, embed=1.0, raise_mm=2.5, wrap=False):
    """Watertight curved strip; rows hold [(theta,z), ...] of equal length."""
    nr, nc = len(rows), len(rows[0])
    verts = [surface(th,z,offset) for offset in [-embed,raise_mm]
             for row in rows for th,z in row]
    count = nr*nc
    faces = []
    for side in range(2):
        off = side*count
        for j in range(nr-1):
            for i in range(nc if wrap else nc-1):
                k=(i+1)%nc
                face=(off+j*nc+i,off+j*nc+k,off+(j+1)*nc+k,off+(j+1)*nc+i)
                faces.append(face if side else tuple(reversed(face)))
    boundary = []
    for i in range(nc if wrap else nc-1):
        boundary += [(i,(i+1)%nc),((nr-1)*nc+(i+1)%nc,(nr-1)*nc+i)]
    if not wrap:
        for j in range(nr-1):
            boundary += [(j*nc,(j+1)*nc),((j+1)*nc+nc-1,j*nc+nc-1)]
    faces += [(a,b,b+count,a+count) for a,b in boundary]
    return new_mesh(name,verts,faces)


def main_horn_outer_x(y):
    # Straight main-horn outer plane. The headband deliberately stands in
    # front of this plane at the root and returns to it across an angled bevel.
    t=(y/H+73)/203
    return A*.83+(y/H+64)*math.tan(math.radians(HORN_SPLAY_DEG))+13-11*t


def horn_root_setback(y):
    return HORN_ROOT_SETBACK_MM*linear_sample(y/H,[(-500,1),(-100,1),(-60,1),(-20,.50),(20,0),(500,0)])


def horn_root_edge_trim(y):
    # Local subtraction at the attachment only; the straight long blade stays put.
    return HORN_ROOT_EDGE_TRIM_MM*linear_sample(y/H,[(-500,0),(-108,0),
        (-90,1),(-60,1),(-20,0),(500,0)])


def horn_base_x(y):
    return main_horn_outer_x(y)-horn_root_setback(y)-horn_root_edge_trim(y)


def horn_notch_tool(sign=1):
    # A shallow circle segment at the root, not a deep semicircle mid-blade.
    # Confine the tool to one temple, preserving the center crest.
    x0,x1=(A*.55,400) if sign>0 else (-400,-A*.55)
    tool=cylinder_y("Shallow circular root dip",-25*H,204*H,x0,x1,
                    HORN_NOTCH_RADIUS_MM*H,segments=128)
    for v in tool.data.vertices:
        x,y,z=v.co
        v.co=(y,x,z)
    fix_normals(tool)
    return tool


def smooth_outline(t, points, flat_start=False):
    # Shape-preserving cubic interpolation. These stations describe the
    # perimeter, not separate blocks, triangles, or stacked ledges.
    xs=[p[0] for p in points];vs=[p[1] for p in points]
    if t<=xs[0]:return vs[0]
    if t>=xs[-1]:return vs[-1]
    slopes=[(vs[i+1]-vs[i])/(xs[i+1]-xs[i]) for i in range(len(xs)-1)]
    tangents=[0 if flat_start else slopes[0]]
    for i in range(1,len(xs)-1):
        a,b=slopes[i-1],slopes[i]
        if a*b<=0:tangents.append(0)
        else:
            h0=xs[i]-xs[i-1];h1=xs[i+1]-xs[i]
            w0=2*h1+h0;w1=h1+2*h0
            tangents.append((w0+w1)/(w0/a+w1/b))
    tangents.append(slopes[-1])
    for i in range(len(xs)-1):
        if t<=xs[i+1]:
            h=xs[i+1]-xs[i];u=(t-xs[i])/h
            return ((2*u**3-3*u*u+1)*vs[i]+(u**3-2*u*u+u)*h*tangents[i]
                    +(-2*u**3+3*u*u)*vs[i+1]+(u**3-u*u)*h*tangents[i+1])


def brow_contour(theta):
    # ONE outer contour around forehead and temples. The fuller shoulder is
    # only a widening of this contour; no raised flare sits on top of it.
    a=abs(theta)
    leading=surface(0,(EYE_TOP-12)*H,0)[1]-(3+BROW_FORWARD_MM)
    knots=[(0,0,leading),(.35,A*.45,leading+9),(.65,A*.80,leading+26),
           (.88,A-4,-B+14),(1.10,A-1,-B+37),(1.30,A+1,-B+65),
           (1.48,A+5,-15),(math.pi/2,A+7,0)]
    if a>math.pi/2:
        return ((A+7)*math.sin(theta),-(B+7)*math.cos(theta))
    x=smooth_outline(a,[(th,x) for th,x,y in knots])
    y=smooth_outline(a,[(th,y) for th,x,y in knots],True)
    return (math.copysign(x,theta),y)


def brow_heights(theta):
    a=abs(theta)
    old_base=(EYE_TOP-12+27*a) if a<=1 else (EYE_TOP+15+(HATCH_TOP-EYE_TOP-15)*min((a-1)/.57,1))
    old_width=23+10*min(1,max(0,(a-1.30)/.6))
    blend=min(1,max(0,(a-1.45)/.30));blend=blend*blend*(3-2*blend)
    bottom=(EYE_TOP-12+30*a)*(1-blend)+old_base*blend
    top=smooth_outline(a,[(0,EYE_TOP+12+BROW_FRONT_HEIGHT_ADDITION_MM),(.35,157),
                          (.65,162),(.88,172),(1.10,178),(1.30,177),
                          (1.48,172),(1.75,HATCH_TOP+33)],True)
    top=top*(1-blend)+(old_base+old_width)*blend
    front_drop=BROW_UNDERSIDE_DROP_MM if a<=1.0 else 0
    return (bottom-front_drop)*H,top*H


def band_join_point(sign=1):
    # A short outward flare at the front attachment, ending before the horn
    # notch. The main horn continues independently behind this closed end.
    y=BROW_END_Y_MM*H
    z=(163+(BROW_END_Y_MM+34)*(HORN_TIP_Z/H-7-163)/164)*H
    return (sign*(A-5),y,z)


def brow_outer(theta,u):
    a=abs(theta);sign=1 if theta>=0 else -1
    lo,hi=brow_heights(theta);z=lo+(hi-lo)*u
    if a<=.76:
        x,y=brow_contour(theta)
        trim=3.45*max(0,(a-.65)/.25)
        return (sign*(abs(x)-trim),y,z)
    point=Vector(band_join_point(sign))
    if a<=1.0:
        lo0,hi0=brow_heights(.76);x0,y0=brow_contour(.76)
        shoulder=Vector((sign*(x0-3.45*(.76-.65)/.25),y0,lo0+(hi0-lo0)*u))
        # The former flare collapsed its entire height to the ridge point.
        # Extend its lower end into the marked triangular underside instead.
        lower=Vector((point.x-sign*2,point.y-2*H,horn_lower_z(BROW_END_Y_MM)*H))
        end=lower.lerp(point,u)
        result=shoulder.lerp(end,(a-.76)/.24)
        return tuple(result)
    # This branch belongs only to the separate rear ribbon. The front band
    # ends at the point above and has no intervening temple continuation.
    x,y=brow_contour(theta)
    rear=min(1,max(0,(a-1.45)/.30));rear=rear*rear*(3-2*rear)
    old=surface(theta,z,7)
    original=Vector((x*(1-rear)+old[0]*rear,y*(1-rear)+old[1]*rear,z))
    return tuple(Vector(surface(theta,z,-1)).lerp(original,rear))


def front_brow_inner(theta,u):
    a=abs(theta);sign=1 if theta>=0 else -1
    z=brow_outer(theta,u)[2]
    # Bury the inner top rail into the crown instead of carrying the high
    # outside shoulder across the whole cap as an exposed triangular fin.
    drop=10*smooth_outline(a,[(0,0),(.45,0),(.65,.7),(.76,1),(1,1)],True)
    z-=drop*u
    if a<=.60:return surface(theta,z,-3)
    # The recessed inner rail moves steadily toward the attachment.
    # It must not double back or create a raised sliver.
    start=Vector(surface(sign*.60,z,-3))
    end=Vector((sign*(A*.67),(BROW_END_Y_MM-2)*H,z))
    return tuple(start.lerp(end,(a-.60)/.40))


def open_band_loft(name,ts,front=False):
    levels=[0,.5,1];n=len(ts);m=len(levels);count=n*m;verts=[]
    for layer in [0,1]:
        for u in levels:
            for th in ts:
                lo,hi=brow_heights(th);z=lo+(hi-lo)*u
                if layer:
                    xyz=brow_outer(th,u)
                else:
                    xyz=front_brow_inner(th,u) if front else surface(th,z,-3)
                verts.append(xyz)
    faces=[]
    for j in range(m-1):
        for i in range(n-1):
            q=(j*n+i,j*n+i+1,(j+1)*n+i+1,(j+1)*n+i)
            faces += [tuple(reversed(q)),tuple(v+count for v in q)]
    for i in range(n-1):
        faces += [(i,i+1,i+1+count,i+count),
                  ((m-1)*n+i+1,(m-1)*n+i,(m-1)*n+i+count,(m-1)*n+i+1+count)]
    for j in range(m-1):
        faces += [(j*n,(j+1)*n,(j+1)*n+count,j*n+count),
                  (j*n+n-1,j*n+n-1+count,(j+1)*n+n-1+count,(j+1)*n+n-1)]
    return new_mesh(name,verts,faces)


def front_brow_rim():
    # One continuous rim with a rounded upper outside edge. Dense stations
    # carry the curve into the short end instead of making two broad facets.
    ts=sorted(set([-1+i*2/240 for i in range(241)]+[-.76,.76,-.65,.65,-.60,.60]))
    rings=[]
    for th in ts:
        bottom=Vector(brow_outer(th,0));top=Vector(brow_outer(th,1))
        inside_top=Vector(front_brow_inner(th,1));inside_bottom=Vector(front_brow_inner(th,0))
        across=(inside_top-top).normalized()
        up=(top-bottom).normalized()
        fade=min(1,max(0,(1-abs(th))/.16))
        radius=min(BROW_UPPER_EDGE_RADIUS_MM*fade,(top-bottom).length*.20,(inside_top-top).length*.20)
        # Keep an extremely small rounded section at the end for a closed loft.
        radius=max(.015,radius)
        ring=[bottom]
        for i in range(7):
            angle=i*math.pi/12
            ring.append(top+across*radius*(1-math.cos(angle))-up*radius*(1-math.sin(angle)))
        # Subdivide across the broad top as well as around the forehead.
        # One long twisted quad per station produced alternating diagonal
        # facets; short cells approximate this same continuous loft cleanly.
        cap_start=ring[-1].copy()
        ring += [cap_start.lerp(inside_top,i/16) for i in range(1,17)]
        ring.append(inside_bottom)
        rings.append(ring)
    n=len(rings[0]);verts=[tuple(v) for ring in rings for v in ring]
    faces=[tuple(reversed(range(n)))]
    for j in range(len(rings)-1):
        faces += [(j*n+i,j*n+(i+1)%n,(j+1)*n+(i+1)%n,(j+1)*n+i) for i in range(n)]
    faces.append(tuple(range((len(rings)-1)*n,len(rings)*n)))
    rim=new_mesh("Cyan continuous rim with rounded top and filled underside",verts,faces)
    for polygon in rim.data.polygons:polygon.use_smooth=True
    rim.data.set_sharp_from_angle(angle=math.radians(28))
    return rim


def rear_brow_ribbon():
    # Retain the rear ribbon and its groove. Its ends are behind the horns,
    # spatially separate from the short front band; the horns join the solids.
    angles=sorted(set([1.45,2*math.pi-1.45,1.75,2*math.pi-1.75]+
                      [i*2*math.pi/320 for i in range(320) if 1.45<i*2*math.pi/320<2*math.pi-1.45]))
    ts=[t if t<=math.pi else t-2*math.pi for t in angles]
    return open_band_loft("Cyan rear ribbon beneath the rear of the horns",ts)


def brow():
    band=boolean(front_brow_rim(),rear_brow_ribbon(),'UNION')
    return boolean(band,ribbon_valley_tool())


def diamond_outline():
    """Measured correction to the Oct 15 cover, in mask coordinates.

    Top +18 mm; lower corner -14 mm; side corners -5 mm. The
    frontmost outline point is 10 mm behind the visor's front edge.
    The previous 50 mm edges are superseded by these fit corrections.
    """
    leading=brow_contour(0)[1]
    old_front_y=leading+2.5-5
    side_y=-B-8
    half_width=math.sqrt(50.0**2-(side_y-old_front_y)**2-11.0**2)
    return [(0,leading+BROW_DIAMOND_SETBACK_MM,EYE_TOP+27-14),
            (-half_width,side_y,EYE_TOP+38-5),
            (half_width,side_y,EYE_TOP+38-5),
            (0,-.76*B+5,199*H+18),
            (0,-B-8,EYE_TOP+BROW_PEAK_HEIGHT_MM)]


def front_brow_peak():
    faces=[(4,1,0),(4,0,2),(4,2,3),(4,3,1),(0,1,3),(0,3,2)]
    return new_mesh("Cyan inset diamond with corrected upper and lower reach",diamond_outline(),faces)


def sculpted_patch(name,stations,sign=1,edge_raise=4,ridge_raise=14):
    # Each station is (z, first angle, last angle). The central strip forms a
    # real outward triangular ridge; it is not a shading line or a flat decal.
    rows=[]
    for k in range(len(stations)-1):
        z0,a0,b0=stations[k];z1,a1,b1=stations[k+1]
        for t in [0]:
            rows.append((z0+(z1-z0)*t,a0+(a1-a0)*t,b0+(b1-b0)*t))
    rows.append(stations[-1]); us=[0,.46,1]
    n=len(us);count=len(rows)*n
    verts=[]
    for side in [0,1]:
        for z,a,b in rows:
            for u in us:
                # Crisp off-center longitudinal ridge with two large planar slopes.
                peak=max(0,1-abs(u-.46)/(.46 if u<.46 else .54))
                offset=-3.0 if side==0 else edge_raise+(ridge_raise-edge_raise)*peak
                verts.append(surface(sign*(a+(b-a)*u),z*H,offset))
    faces=[]
    for j in range(len(rows)-1):
        for i in range(n-1):
            q=(j*n+i,j*n+i+1,(j+1)*n+i+1,(j+1)*n+i)
            faces += [tuple(reversed(q)),tuple(v+count for v in q)]
    border=[(i,i+1) for i in range(n-1)]+[((len(rows)-1)*n+i+1,(len(rows)-1)*n+i) for i in range(n-1)]
    for j in range(len(rows)-1):border += [(j*n,(j+1)*n),((j+1)*n+n-1,j*n+n-1)]
    faces += [(a,b,b+count,a+count) for a,b in border]
    return new_mesh(name,verts,faces)


def side_shell_x(y,z):
    # Invert the actual shell contour; the lower front includes nose relief.
    lo,hi=0.0,math.pi
    for _ in range(45):
        th=(lo+hi)/2
        xx,yy=section_xy(th,z,A,B,profile(z))
        if yy<y:lo=th
        else:hi=th
    return section_xy((lo+hi)/2,z,A,B,profile(z))[0]


def side_blade(name,rows,sign,free=False):
    # Three columns: lower edge, one LATERAL ridge, upper edge. No zigzag
    # center strips, floating wedges, or vertical ridge on the cheek.
    n=3;count=len(rows)*n;verts=[]
    for layer in [0,1]:
        for y,lo,mid,hi,raised in rows:
            for j,z in enumerate([lo,mid,hi]):
                y0=y*H;z0=z*H
                base=(A*.93+(y+25)*.12) if free else side_shell_x(y0,z0)
                offset=(-8 if free else -3) if layer==0 else (raised if j==1 else 3)
                verts.append((sign*(base+offset),y0,z0))
    faces=[]
    for k in range(len(rows)-1):
        for j in range(n-1):
            q=(k*n+j,k*n+j+1,(k+1)*n+j+1,(k+1)*n+j)
            faces += [tuple(reversed(q)),tuple(i+count for i in q)]
    border=[(i,i+1) for i in range(2)]+[((len(rows)-1)*n+i+1,(len(rows)-1)*n+i) for i in range(2)]
    for k in range(len(rows)-1):border += [(k*n,(k+1)*n),((k+1)*n+2,k*n+2)]
    faces += [(a,b,b+count,a+count) for a,b in border]
    return new_mesh(name,verts,faces)


def cheek_rows():
    return [(-89,28,40,51,10),(-82,26,41,54,12),(-47,29,40,49,11),(-18,37,40,43,5)]


def secondary_outline():
    # Front shoulder, upper blade, rounded-off rear point, lower blade,
    # lower cheek join, lower front join, and concave cheek-side corner.
    return [(-27,143),(70,148),(80,141),(69,124),(-24,36),(-65,36),(15,100)]


def side_detail_outlines():
    rows=cheek_rows()
    cheek=[(y,lo) for y,lo,mid,hi,r in rows]+[(y,hi) for y,lo,mid,hi,r in reversed(rows)]
    return [cheek,secondary_outline()]


def loft_three_columns(name,verts,rows):
    # Closed volume from matching rear/front grids, each with three columns.
    n=3;count=rows*n;faces=[]
    for k in range(rows-1):
        for j in range(2):
            q=(k*n+j,k*n+j+1,(k+1)*n+j+1,(k+1)*n+j)
            faces += [tuple(reversed(q)),tuple(i+count for i in q)]
    border=[(i,i+1) for i in range(2)]+[((rows-1)*n+i+1,(rows-1)*n+i) for i in range(2)]
    for k in range(rows-1):border += [(k*n,(k+1)*n),((k+1)*n+2,k*n+2)]
    faces += [(a,b,b+count,a+count) for a,b in border]
    return new_mesh(name,verts,faces)


def descending_horn(sign):
    # Explicit folds replace the old curved apron. The upper ridge runs to
    # the rear tip; the same fold turns down into the short cheek blade.
    outline=secondary_outline();points=outline+[(24,123),(-44,42)]
    def point(y,z,outer,ridge=False):
        shell=side_shell_x(y*H,z*H)
        blend=min(1,max(0,(z-50)/60))
        base=shell*(1-blend)+(A*.94+(y+25)*.11)*blend
        x=base+((20 if z>100 else 10) if ridge else 3) if outer else base-3-5*blend
        return (sign*x,y*H,z*H)
    n=len(outline)
    verts=[point(y,z,False) for y,z in outline]
    verts += [point(y,z,True,i>=n) for i,(y,z) in enumerate(points)]
    facets=[(0,1,7),(1,2,7),(2,3,7),(3,4,8),(3,8,7),
            (4,5,8),(5,6,8),(6,7,8),(6,0,7)]
    faces=[tuple(reversed(range(n)))]
    faces += [tuple(n+i for i in f) for f in facets]
    faces += [(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
    return new_mesh("Cyan folded secondary wedge and descending cheek",verts,faces)


def cheek_parts(sign):
    return [side_blade("Cyan short cheek with lateral ridge",cheek_rows(),sign),
            descending_horn(sign)]

def horn_lower_z(y):
    # The lower attachment rises smoothly into the straight long blade.
    tip_z=184+173*math.tan(math.radians(HORN_RAKE_DEG))
    if y<=-22:
        return smooth_outline(y,[(-108,128),(-90,128.8),(-64,131),(-42,135),(-22,140)])
    if y<=124:return 140+(y+22)*(tip_z-11-140)/146
    return linear_sample(y,[(124,tip_z-11),(129,tip_z-10),(130,tip_z-9)])


def horn(sign, notched=True):
    # Three rails share a continuous center ridge. Every change in the local
    # attachment taper gets an explicit cross-section; no non-planar ngon
    # can introduce spurious inset-looking diagonals over the blade.
    tip_z=184+173*math.tan(math.radians(HORN_RAKE_DEG))
    def upper(y):return 184+(y+49)*(tip_z-184)/173
    def lower(y):return 140+(y+22)*(tip_z-11-140)/146
    top=[(-108,146),(-103,153),(-85,169),(-64,179),(-49,184),
         (45,upper(45)),(90,upper(90)),(124,tip_z),(129,tip_z-2),(130,tip_z-5)]
    bottom=[(-108,131),(-103,126),(-99,126),(-70,127),(-22,140),
            (45,lower(45)),(90,lower(90)),(124,tip_z-11),(129,tip_z-10),(130,tip_z-9)]
    ys=sorted(set([y for y,z in top+bottom]+list(range(-108,-20,2))+[-100,-90,-73,-60,-35,-20,20]))
    jy,jz=-34,163;ty,tz=130,tip_z-7
    def plane(y,z,anchor):
        ay,az=anchor;den=(jy-ty)*(az-tz)-(ay-ty)*(jz-tz)
        start=((y-ty)*(az-tz)-(ay-ty)*(z-tz))/den
        end=((y-jy)*(az-jz)-(ay-jy)*(z-jz))/((ty-jy)*(az-jz)-(ay-jy)*(tz-jz))
        return HORN_RIDGE_RELIEF_MM*start+HORN_TIP_RIDGE_MM*end
    verts=[]
    for outer in [False,True]:
        for y in ys:
            ridge_z=163+(y+34)*(tip_z-7-163)/164
            for column,z in enumerate([horn_lower_z(y),ridge_z,linear_sample(y,top)]):
                x=horn_base_x(y*H)
                if outer:
                    x+=plane(y,z,(-22,140) if column==0 else (-49,184))
                else:
                    x=main_horn_outer_x(y*H)
                    t=min(1,max(0,(y+73)/203))
                    root=linear_sample(y,[(-108,.50),(-73,HORN_ROOT_WIDTH_FACTOR),
                                         (-64,.65),(-49,.90),(-35,1),(130,1)])
                    x-=2*(13-11*t)*root
                    # Keep at least 3 mm behind the shaved outside attachment.
                    # This hidden face stays inside the existing shell; the
                    # exterior facet and long blade positions do not change.
                    skin=min(horn_base_x(y*H)+plane(y,z0,anchor)
                             for z0,anchor in [(horn_lower_z(y),(-22,140)),
                                               (linear_sample(y,top),(-49,184))])
                    if horn_root_edge_trim(y*H)>0:x=min(x,skin-3.0)
                verts.append((sign*x,y*H,z*H))
    fin=loft_three_columns("Cyan straight horn ridge beneath front rim flare",verts,len(ys))
    return boolean(fin,horn_notch_tool(sign)) if notched else fin

def crest():
    # The top reference shows a broad stripe and two flared stepped wedges.
    stations=[(-.99,1.10,5),(-.89,1.02,8),(-.76,.90,17),(-.60,.82,20),
              (-.45,1.08,21),(-.39,1.05,8),(-.26,.86,8),(-.15,.95,16),
              (.02,.90,18),(.16,1.02,18),(.23,1.02,7),(.42,.91,8),
              (.58,.84,11),(.69,.80,4),(.87,.75,3)]
    verts=[]
    for frac,mult,raised in stations:
        w=CREST_WIDTH_MM/2*mult;y=frac*B
        for x,delta in [(-w,-3),(w,-3),(w,raised*.55),(0,raised*.55+2),(-w,raised*.55)]:
            z=DOME_START+(DOME_TOP-DOME_START)*math.sqrt(max(.002,1-(y/B)**2-(x/A)**2))
            verts.append((x,y,z+delta))
    n=5;faces=[tuple(reversed(range(n)))]
    for j in range(len(stations)-1):faces += [(j*n+i,j*n+(i+1)%n,(j+1)*n+(i+1)%n,(j+1)*n+i) for i in range(n)]
    faces.append(tuple(range((len(stations)-1)*n,len(stations)*n)))
    return new_mesh("Cyan broad stepped crown crest",verts,faces)


def ribbon_valley_tool():
    # V-section groove on the rear ribbon, fading out toward the temples.
    n=81;zs=[HATCH_TOP+9,HATCH_TOP+12,HATCH_TOP+16,HATCH_TOP+20,HATCH_TOP+23];depths=[8,6,4.8,6,8]
    verts=[]
    for layer in [0,1]:
        for z,depth in zip(zs,depths):
            for i in range(n):
                u=i/(n-1);theta=1.70+(2*math.pi-3.40)*u
                fade=min(1,u/.10,(1-u)/.10)
                offset=11 if layer else 9+(depth-9)*fade
                verts.append(surface(theta,z*H,offset))
    count=n*len(zs);faces=[]
    for j in range(len(zs)-1):
        for i in range(n-1):
            q=(j*n+i,j*n+i+1,(j+1)*n+i+1,(j+1)*n+i)
            faces += [tuple(reversed(q)),tuple(v+count for v in q)]
    border=[(i,i+1) for i in range(n-1)]+[((len(zs)-1)*n+i+1,(len(zs)-1)*n+i) for i in range(n-1)]
    for j in range(len(zs)-1):border += [(j*n,(j+1)*n),((j+1)*n+n-1,j*n+n-1)]
    faces += [(a,b,b+count,a+count) for a,b in border]
    return new_mesh("Rear ribbon recessed V channel",verts,faces)


def lower_rim_tool():
    # Trim the front to the marked chevron edge, keeping the circular head fit.
    xs=[-500,-100,-75,-50,-25,0,25,50,75,100,500]
    ys=[-500,-150,-100,-75,-65,-30,0,65,140,500]
    n=len(xs);m=len(ys);count=n*m;verts=[]
    for layer in [0,1]:
        for y in ys:
            old=linear_sample(y,[(-500,0),(-(B-10),0),(-75,6),(-30,18),(0,27.5),(65,48.95),(140,55),(500,55)])
            fade=min(1,max(0,-y/65))
            for x in xs:
                front=FRONT_RIM_RISE_MM+18*min(1,abs(x)/75)
                z=max(old,old*(1-fade)+front*fade)*H if layer else -80
                verts.append((x,y,z))
    faces=[]
    for j in range(m-1):
        for i in range(n-1):
            q=(j*n+i,j*n+i+1,(j+1)*n+i+1,(j+1)*n+i)
            faces += [tuple(reversed(q)),tuple(k+count for k in q)]
    border=[(i,i+1) for i in range(n-1)]+[((m-1)*n+i+1,(m-1)*n+i) for i in range(n-1)]
    for j in range(m-1):border += [(j*n,(j+1)*n),((j+1)*n+n-1,j*n+n-1)]
    faces += [(a,b,b+count,a+count) for a,b in border]
    return new_mesh("Shortened V-shaped front and raised rear opening",verts,faces)


def rear_panel(name,outline,raised=7.0,ridge=3.0):
    """Folded rear ribbon solid, embedded into the curved shell to stay attached."""
    n=len(outline)
    cx=sum(x for x,z in outline)/n
    cz=sum(z for x,z in outline)/n
    def pt(x,z,offset):
        z*=H
        f=profile(z)
        y=B*f*math.sqrt(max(.001,1-(x/(A*f))**2))
        return (x,y+offset,z)
    verts=[pt(x,z,-2) for x,z in outline]+[pt(x,z,raised) for x,z in outline]
    faces=[tuple(reversed(range(n)))]
    faces += [(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
    if ridge!=0:
        verts.append(pt(cx,cz,raised+ridge))
        faces += [(n+i,n+(i+1)%n,2*n) for i in range(n)]
    else:
        faces.append(tuple(range(n,2*n)))
    return new_mesh(name,verts,faces)


def ribbon_strands():
    # Two broader folded strands: broad nearly straight long hem, and a longer
    # companion whose upper fold reaches above the knot, as in the rear photo.
    t=HATCH_TOP
    long=[(t+39,-8,9,10,12),(t+31,-14,16,12,15),(t+18,-13,19,13,17),
          (t+4,-8,15,10,12),(t-12,-10,19,9,6),(t-40,-15,28,9,6),
          (t-65,-18,35,9,6),(t-70,-16,33,8,6)]
    short=[(t+43,-8,6,11,13),(t+32,-18,10,16,19),(t+18,-23,4,17,20),
           (t+3,-20,-2,12,14),(t-12,-26,-5,10,7),
           (t-48,-29,-6,9,6),(t-58,-23,-3,8,6)]
    # Rear reference: shorter fold on the left, broad long tail on the right.
    return tuple([(z,-right,-left,edge,middle) for z,left,right,edge,middle in rows] for rows in [long,short])

def ribbon_outlines():
    # The same outlines control the hidden rear-panel clearance.
    return [[(left,z) for z,left,right,edge,middle in rows]+
            [(right,z) for z,left,right,edge,middle in reversed(rows)]
            for rows in ribbon_strands()]


def folded_strand(name, rows):
    us=[0,.18,.52,.82,1];n=len(us);count=len(rows)*n
    vertices=[]
    for side in [0,1]:
        for z,left,right,edge,middle in rows:
            for u in us:
                x=left+(right-left)*u;zz=z*H;f=profile(zz)
                y=B*f*math.sqrt(max(.001,1-(x/(A*f))**2))
                offset=-2 if not side else linear_sample(u,[(0,edge),(.18,edge+1),(.52,middle),(.82,edge+1),(1,edge)])
                vertices.append((x,y+offset,zz))
    faces=[]
    for j in range(len(rows)-1):
        for i in range(n-1):
            q=(j*n+i,j*n+i+1,(j+1)*n+i+1,(j+1)*n+i)
            faces += [tuple(reversed(q)),tuple(k+count for k in q)]
    border=[(i,i+1) for i in range(n-1)]+[((len(rows)-1)*n+i+1,(len(rows)-1)*n+i) for i in range(n-1)]
    for j in range(len(rows)-1):border += [(j*n,(j+1)*n),((j+1)*n+n-1,j*n+n-1)]
    faces += [(a,b,b+count,a+count) for a,b in border]
    return new_mesh(name,vertices,faces)


def upper_knot_cap(strands):
    """The fitted wrap's broad upper knot, tapered to the original tail seam.

    This is a solid part of the upper mask. It has no hollow repair socket,
    plate overhang or lip below the original cut. Lower tails are unchanged.
    """
    from mathutils.bvhtree import BVHTree
    original=boolean(copy_obj(strands[0],"Knot source"),copy_obj(strands[1],"Second strand"),"UNION")
    cropped=copy_obj(original,"Wrapped knot profile")
    floor=HATCH_TOP-12
    boolean(cropped,cube("Clip lower tails",(0,100,(floor-150)/2),(300,400,floor+150)))
    vv=[v.co.copy() for v in cropped.data.vertices]
    lo=Vector([min(v[i] for v in vv) for i in range(3)])
    hi=Vector([max(v[i] for v in vv) for i in range(3)])
    center=(lo+hi)/2
    bm=bmesh.new()
    for v in vv:
        q=center+(v-center)*1.05+Vector((0,4,0))
        q.x+=1.8*(1 if v.x>center.x else -1)
        if v.z>HATCH_TOP+20:q.z+=1.5*(v.z-HATCH_TOP-20)/(hi.z-HATCH_TOP-20)
        bm.verts.new(q)
        q=q.copy();q.y=85;bm.verts.new(q)
    bmesh.ops.convex_hull(bm,input=list(bm.verts),use_existing_faces=False)
    loose=[v for v in bm.verts if not v.link_faces]
    if loose:bmesh.ops.delete(bm,geom=loose,context="VERTS")
    bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
    cap=new_mesh("Upper knot with enclosed sides",[],[])
    bm.to_mesh(cap.data);bm.free();delete(cropped)
    fix_normals(cap)
    z0=FRONT_SEAM;z1=z0+14
    def section(ob,z):
        tv,tf=triangles(ob);points=[]
        for face in tf:
            poly=[Vector(tv[i]) for i in face]
            for a,b in zip(poly,poly[1:]+poly[:1]):
                if min(a.z,b.z)<z<max(a.z,b.z):
                    q=a.lerp(b,(z-a.z)/(b.z-a.z));points.append(q)
        return points
    # Add every section-corner direction, so the lower seam reproduces
    # the original folded streamers instead of an oversized cap perimeter.
    lower=section(original,z0);upper=section(cap,z1)
    center_xy=Vector((0,110,0))
    angles={math.atan2(v.y-110,v.x) for v in lower+upper}
    angles.update(i*2*math.pi/96-math.pi for i in range(96))
    ordered=sorted(angles);angles=[]
    for a in ordered:
        if not angles or a-angles[-1]>.0001:angles.append(a)
    def ring(ob,z):
        tv,tf=triangles(ob);tree=BVHTree.FromPolygons(tv,tf,all_triangles=True)
        result=[]
        for a in angles:
            d=Vector((math.cos(a+1e-8),math.sin(a+1e-8),0))
            hit=tree.ray_cast(Vector((0,110,z)),d,100)[0]
            if hit is None:raise RuntimeError("Missing upper knot section")
            result.append(tuple(hit))
        return result
    bottom=ring(original,z0);top=ring(cap,z1+.01)
    # Remove redundant collinear samples on both sections. Close angular
    # duplicates would create needle triangles in the printable STL.
    changed=True
    while changed and len(bottom)>8:
        changed=False
        for i in range(len(bottom)):
            def flat(points):
                a=Vector(points[i])-Vector(points[i-1])
                b=Vector(points[(i+1)%len(points)])-Vector(points[i])
                return a.cross(b).length<.0002
            if flat(bottom) and flat(top):
                bottom.pop(i);top.pop(i);changed=True;break
    n=len(bottom)
    faces=[tuple(reversed(range(n))),tuple(range(n,2*n))]
    faces += [(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
    transition=new_mesh("Knot meets streamers at original seam",bottom+top,faces)
    boolean(cap,cube("Upper cap trim",(0,100,(z1-150)/2),(300,400,z1+150)))
    boolean(cap,transition,"UNION")
    # Keep the original shell-side embed. The larger outer cap must not
    # replace the white inner wall or the white magnet-bearing ridge.
    rows=[(z,left,right,0,0) for z,left,right in
          [(HATCH_TOP+60,-50,50),(HATCH_TOP+40,-50,50),
           (HATCH_TOP+20,-50,50),(HATCH_TOP,-50,50)]]
    keep=folded_strand("Knot exterior-only color volume",rows)
    for v in list(keep.data.vertices)[len(rows)*5:]:v.co.y=500
    fix_normals(keep);boolean(cap,keep,"INTERSECT")
    delete(original)
    return cap


def bow_parts():
    strands=[folded_strand("Cyan ribbon long folded strand",ribbon_strands()[0]),
             folded_strand("Cyan ribbon short crossing strand",ribbon_strands()[1])]
    return strands+[upper_knot_cap(strands)]


def eye_cutter():
    # Several vertical columns attain exactly 35 mm clear height at defaults.
    w=EYE_WIDTH_MM/2
    top=EYE_TOP
    bot=EYE_BOTTOM
    shape=[(-w,top-3),(-.84*w,top),(-.59*w,top),(-.26*w,top-6),(0,top-10),
           (.26*w,top-6),(.59*w,top),(.84*w,top),(w,top-3),
           (.97*w,bot+12),(.84*w,bot),(.59*w,bot+7),(.25*w,bot+3),(0,bot),
           (-.25*w,bot+3),(-.59*w,bot+7),(-.84*w,bot),(-.97*w,bot+12)]
    n=len(shape)
    verts=[(x,y,z) for y in [-B-60,-10] for x,z in shape]
    faces=[tuple(reversed(range(n))),tuple(range(n,2*n))]
    faces += [(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
    return new_mesh("Actual eye through-opening",verts,faces)


def side_trailing_y(z):
    crossings=[]
    for polygon in side_detail_outlines():
        for (y0,z0),(y1,z1) in zip(polygon,polygon[1:]+polygon[:1]):
            if min(z0,z1)<=z<=max(z0,z1) and abs(z1-z0)>1e-9:
                crossings.append(y0+(y1-y0)*(z-z0)/(z1-z0))
    return max(crossings) if crossings else -50


def seam_y_at(z):
    # A conservative internal dividing surface. The actual side edge is set
    # by the swept cyan solid below, rather than a flat Y/Z outline prism.
    return min(0,side_trailing_y(z/H)-3)*H


def side_outline_hold(margin):
    # Project the real rear-facing triangles forward, including the folded
    # overhangs. The rear panel can then withdraw without catching beneath them.
    key=(A,B,H,margin)
    if key in SIDE_SHADOW_CACHE:
        return new_mesh("Cached conforming cyan side joint",*SIDE_SHADOW_CACHE[key],cleanup=False)
    patches=[]
    for sign in [-1,1]:
        for ob in cheek_parts(sign):
            ob.data.calc_loop_triangles()
            for tri in ob.data.loop_triangles:
                if tri.normal.y<=.01:continue
                cap=[ob.data.vertices[i].co.copy() for i in tri.vertices]
                points=[Vector((v.x,v.z)) for v in cap]
                area=sum(p.x*points[(i+1)%3].y-points[(i+1)%3].x*p.y for i,p in enumerate(points))
                orientation=1 if area>0 else -1
                for i,p in enumerate(points):
                    before=(p-points[i-1]).normalized();after=(points[(i+1)%3]-p).normalized()
                    na=orientation*Vector((before.y,-before.x));nb=orientation*Vector((after.y,-after.x))
                    shift=(na+nb)*margin/max(.05,1+na.dot(nb))
                    if shift.length>2*margin:shift=shift.normalized()*2*margin
                    cap[i].x+=shift.x;cap[i].z+=shift.y
                    cap[i].y+=margin-(tri.normal.x*shift.x+tri.normal.z*shift.y)/tri.normal.y
                vertices=[tuple(v) for v in cap]+[(v.x,-500,v.z) for v in cap]
                faces=[(0,1,2),(5,4,3),(0,3,4,1),(1,4,5,2),(2,5,3,0)]
                patches.append(new_mesh('Cyan conforming joint patch',vertices,faces))
            delete(ob)
    result=patches.pop()
    collection=bpy.data.collections.new('Complete cyan side joint')
    for ob in patches:collection.objects.link(ob)
    active(result)
    mod=result.modifiers.new('Unite conforming joint','BOOLEAN')
    mod.operation='UNION';mod.solver='MANIFOLD';mod.operand_type='COLLECTION';mod.collection=collection
    bpy.ops.object.modifier_apply(modifier=mod.name)
    for ob in patches:delete(ob)
    bpy.data.collections.remove(collection)
    if mesh_report(result)['nonmanifold_edges']:
        raise RuntimeError('The conforming cyan side joint is not closed')
    SIDE_SHADOW_CACHE[key]=([tuple(v.co) for v in result.data.vertices],
                            [tuple(p.vertices) for p in result.data.polygons])
    return result


def shell_x_at(z,y):
    t=min(max(z/(145*H),0),1);n=2.5-.5*t
    # Side seams are outside the localized nose projection.
    return A*profile(z)*max(0,1-abs(y/(B*profile(z)))**n)**(1/n)


def ribbon_hold_volume(margin):
    volumes=[]
    for outline in ribbon_outlines():
        points=[Vector((x,z*H)) for x,z in outline]
        area=sum(points[i].x*points[(i+1)%len(points)].y-points[(i+1)%len(points)].x*points[i].y for i in range(len(points)))
        sign=1 if area>0 else -1
        inflated=[]
        for i,p in enumerate(points):
            before=(p-points[i-1]).normalized();after=(points[(i+1)%len(points)]-p).normalized()
            na=sign*Vector((before.y,-before.x));nb=sign*Vector((after.y,-after.x))
            delta=(na+nb)*margin/max(.15,1+na.dot(nb))
            inflated.append(p+delta)
        n=len(inflated);vv=[(p.x,y,p.y) for y in [-500,500] for p in inflated]
        ff=[tuple(reversed(range(n))),tuple(range(n,2*n))]
        ff += [(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
        volumes.append(new_mesh("Preserved ribbon footprint",vv,ff))
    result=volumes.pop()
    for item in volumes:boolean(result,item,"UNION")
    return result


def hatch_volume(expanded):
    gap=SEAM_GAP_MM/2
    delta=-gap if expanded else gap
    top=HATCH_TOP+(gap if expanded else -gap)
    levels=sorted(set([-30,0,top,min(HATCH_TOP,top),132*H]+[z*H for z in range(1,133)]+[z*H for outline in side_detail_outlines() for y,z in outline if z<132]))
    yz=[(seam_y_at(z)+delta,z) for z in levels]+[(500,top),(500,-30)]
    n=len(yz);verts=[(x,y,z) for x in [-1000,1000] for y,z in yz]
    faces=[tuple(reversed(range(n))),tuple(range(n,2*n))]
    faces += [(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
    base=new_mesh("Rear hatch cutting volume",verts,faces)
    # V26: retain the exact top plane and conforming side cut. Do not subtract
    # the ribbon footprint: the tails below this plane now print with the rear.
    return boolean(base,side_outline_hold(.03 if expanded else .03+SEAM_GAP_MM))


def guide_seam_y(x,z):
    from mathutils.bvhtree import BVHTree
    hits=[]
    for expanded in [True,False]:
        tool=hatch_volume(expanded);tool.data.calc_loop_triangles()
        tree=BVHTree.FromPolygons([tuple(v.co) for v in tool.data.vertices],
             [tuple(t.vertices) for t in tool.data.loop_triangles],all_triangles=True)
        hit=tree.ray_cast(Vector((x,-400,z)),Vector((0,1,0)),900)[0]
        if hit is None:raise RuntimeError("No side joint at alignment pin")
        hits.append(hit.y);delete(tool)
    return sum(hits)/2


def split(obj,front,name):
    return boolean(copy_obj(obj,name),hatch_volume(front),"DIFFERENCE" if front else "INTERSECT")


def cylinder_z(name,x,y,z0,z1,radius):
    ob=cylinder_y(name,x,0,z0,z1,radius)
    for v in ob.data.vertices:
        xx,zz,yy=v.co
        v.co=(xx,y+yy,zz)
    fix_normals(ob)
    return ob


def material(name, color):
    m=bpy.data.materials.new(name)
    m.diffuse_color=(*color,1)
    m.use_nodes=True
    bs=m.node_tree.nodes.get("Principled BSDF")
    bs.inputs["Base Color"].default_value=(*color,1)
    bs.inputs["Roughness"].default_value=.32
    return m


def mesh_report(obj):
    bm=bmesh.new()
    bm.from_mesh(obj.data)
    bad=sum(not e.is_manifold for e in bm.edges)
    obj.data.calc_loop_triangles()
    degenerate=sum(t.area<1e-9 for t in obj.data.loop_triangles)
    volume=bm.calc_volume(signed=True)
    bm.free()
    verts=[obj.matrix_world@v.co for v in obj.data.vertices]
    bounds=[[min(v[i] for v in verts),max(v[i] for v in verts)] for i in range(3)]
    return {"object":obj.name,"vertices":len(verts),"faces":len(obj.data.polygons),
            "nonmanifold_edges":bad,"degenerate_faces":degenerate,
            "signed_volume_mm3":round(volume,3),"bounds_mm":bounds}


def repair_flat_cap_triangulation(obj):
    # Coplanar Boolean caps sometimes contain a cluster of very short boundary
    # edges. Choose a non-degenerate fan without moving any surface vertices.
    mesh=obj.data;mesh.calc_loop_triangles()
    bad={t.polygon_index for t in mesh.loop_triangles if t.area<1e-9}
    if not bad:return
    replacements={}
    for index in bad:
        face=mesh.polygons[index];ids=list(face.vertices)
        if len(ids)<4:continue
        def volume(tris):
            total=0.0
            for tri in tris:
                a,b,c=[tuple(mesh.vertices[i].co) for i in tri]
                total+=(a[0]*(b[1]*c[2]-b[2]*c[1])+a[1]*(b[2]*c[0]-b[0]*c[2])+a[2]*(b[0]*c[1]-b[1]*c[0]))/6
            return total
        original_volume=volume([t.vertices for t in mesh.loop_triangles if t.polygon_index==index])
        best=None
        for k in range(len(ids)):
            ring=ids[k:]+ids[:k];points=[mesh.vertices[i].co for i in ring]
            areas=[(points[i]-points[0]).cross(points[i+1]-points[0]).dot(face.normal)/2 for i in range(1,len(ids)-1)]
            fan=[(ring[0],ring[i],ring[i+1]) for i in range(1,len(ids)-1)]
            # Only retessellate flat caps: retain the existing triangulation
            # of non-planar sculpted faces if a fan changes their volume.
            if abs(volume(fan)-original_volume)>.01:continue
            if min(areas)>1e-9 and (best is None or min(areas)>best[0]):
                best=(min(areas),fan)
        if best:replacements[index]=best[1]
    if replacements:
        vertices=[tuple(v.co) for v in mesh.vertices];faces=[]
        for face in mesh.polygons:faces.extend(replacements.get(face.index,[tuple(face.vertices)]))
        mesh.clear_geometry();mesh.from_pydata(vertices,[],faces);mesh.update()


def repair_flat_triangle_slivers(obj):
    # Rotate only a local diagonal around a collapsed planar triangle.
    # This keeps all vertices and the enclosed volume, unlike a global weld.
    for _ in range(12):
        mesh=obj.data;mesh.calc_loop_triangles()
        bad={t.polygon_index for t in mesh.loop_triangles if t.area<1e-9}
        if not bad:return
        base=bmesh.new();base.from_mesh(mesh);base.faces.ensure_lookup_table()
        volume=base.calc_volume(signed=True);repaired=False
        for index in bad:
            if len(base.faces[index].verts)!=3:continue
            for edge_index in range(3):
                bm=base.copy();bm.faces.ensure_lookup_table()
                edge=list(bm.faces[index].edges)[edge_index]
                try:bmesh.ops.rotate_edges(bm,edges=[edge],use_ccw=False)
                except RuntimeError:
                    bm.free();continue
                bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
                if any(not e.is_manifold for e in bm.edges) or abs(bm.calc_volume(signed=True)-volume)>.01:
                    bm.free();continue
                trial=bpy.data.meshes.new("Planar socket-cap check");bm.to_mesh(trial);bm.free()
                trial.calc_loop_triangles()
                if sum(t.area<1e-9 for t in trial.loop_triangles)<len(bad):
                    obj.data=trial;bpy.data.meshes.remove(mesh);repaired=True;break
                bpy.data.meshes.remove(trial)
            if repaired:break
        base.free()
        if not repaired:return


def finalize_mesh(obj):
    """Resolve numerical slivers while keeping the original surface in place."""
    fix_normals(obj)
    repair_flat_cap_triangulation(obj)
    repair_flat_triangle_slivers(obj)
    report=mesh_report(obj)
    if not report['nonmanifold_edges'] and not report['degenerate_faces']:return report
    for tolerance in [.0001,.0002,.0005,.001,.002,.005,.01]:
        bm=bmesh.new();bm.from_mesh(obj.data)
        for _ in range(5):
            bmesh.ops.triangulate(bm,faces=list(bm.faces),quad_method="BEAUTY",ngon_method="BEAUTY")
            bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=tolerance)
            bmesh.ops.dissolve_degenerate(bm,edges=list(bm.edges),dist=tolerance)
        bmesh.ops.triangulate(bm,faces=list(bm.faces),quad_method="BEAUTY",ngon_method="BEAUTY")
        bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
        bad=sum(not e.is_manifold for e in bm.edges)
        degenerate=sum(f.calc_area()<1e-9 for f in bm.faces)
        if bad==0 and degenerate==0:
            bm.to_mesh(obj.data);obj.data.update();bm.free()
            return mesh_report(obj)
        bm.free()
    return report


def triangles(obj):
    obj.data.calc_loop_triangles()
    verts=[tuple(obj.matrix_world@v.co) for v in obj.data.vertices]
    return verts,[tuple(t.vertices) for t in obj.data.loop_triangles]


def write_stl(path,obj):
    verts,tris=triangles(obj)
    with open(path,"wb") as f:
        f.write(b"Ninjago costume mask | numeric units: millimetres".ljust(80,b"\0"))
        f.write(struct.pack("<I",len(tris)))
        for tri in tris:
            a,b,c=[Vector(verts[i]) for i in tri]
            n=(b-a).cross(c-a).normalized()
            f.write(struct.pack("<12fH",*n,*a,*b,*c,0))


def write_3mf(path,parts):
    """Core-spec 3MF: two named material meshes in a single component assembly."""
    def sub(parent,tag,attrs=None):
        return ET.SubElement(parent,"{"+NS+"}"+tag,attrs or {})
    root=ET.Element("{"+NS+"}model",{"unit":"millimeter","{http://www.w3.org/XML/1998/namespace}lang":"en-US"})
    sub(root,"metadata",{"name":"Title"}).text=path.stem
    resources=sub(root,"resources")
    materials=sub(resources,"basematerials",{"id":"1"})
    sub(materials,"base",{"name":"White filament","displaycolor":"#F2F2EFFF"})
    sub(materials,"base",{"name":"Cyan filament","displaycolor":"#00BBD9FF"})
    for i,obj in enumerate(parts):
        color=1 if "Cyan" in obj.name else 0
        resource=sub(resources,"object",{"id":str(i+2),"type":"model","name":obj.name,"pid":"1","pindex":str(color)})
        mesh=sub(resource,"mesh")
        vertices=sub(mesh,"vertices")
        verts,tris=triangles(obj)
        for x,y,z in verts:
            sub(vertices,"vertex",{"x":f"{x:.7f}","y":f"{y:.7f}","z":f"{z:.7f}"})
        ts=sub(mesh,"triangles")
        for a,b,c in tris:
            sub(ts,"triangle",{"v1":str(a),"v2":str(b),"v3":str(c)})
    assembly_id=len(parts)+2
    assembly=sub(resources,"object",{"id":str(assembly_id),"type":"model","name":path.stem})
    components=sub(assembly,"components")
    for i in range(len(parts)):
        sub(components,"component",{"objectid":str(i+2)})
    build=sub(root,"build")
    sub(build,"item",{"objectid":str(assembly_id)})
    types='<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>'
    rels='<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>'
    with zipfile.ZipFile(path,"w",zipfile.ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml",types)
        z.writestr("_rels/.rels",rels)
        z.writestr("3D/3dmodel.model",ET.tostring(root,encoding="utf-8",xml_declaration=True))


def output_dir():
    if OUTPUT_DIRECTORY:
        root=Path(bpy.path.abspath(OUTPUT_DIRECTORY)).expanduser()
    else:
        source=globals().get("__file__")
        if source and Path(source).exists():
            root=Path(source).resolve().parent
        elif bpy.context.space_data and bpy.context.space_data.type=="TEXT_EDITOR" and bpy.context.space_data.text and bpy.context.space_data.text.filepath:
            root=Path(bpy.path.abspath(bpy.context.space_data.text.filepath)).parent
        elif bpy.data.filepath:
            root=Path(bpy.data.filepath).parent
        else:
            root=Path(bpy.app.tempdir)
        root=root/("ninjago_mask_"+datetime.now().strftime("%Y%m%d_%H%M%S"))
    root.mkdir(parents=True,exist_ok=True)
    return root


def preserve_main_horn_crease(obj):
    """Keep the physical two-plane fold visible regardless of smoothing cutoff."""
    # The caller identifies the part by its role, never its Blender name.
    # Repeated runs add suffixes such as .001 to names across all scenes.
    ridge_vertices=set()
    tip_z=HORN_TIP_Z/H-7
    for vertex in obj.data.vertices:
        p=vertex.co;y=p.y/H
        if not -108.01<=y<=130.01:
            continue
        t=(y+34)/164
        z=(163+(tip_z-163)*t)*H
        x=(horn_base_x(p.y)+HORN_RIDGE_RELIEF_MM*(1-t)+HORN_TIP_RIDGE_MM*t)*X_SCALE
        if abs(p.z-z)<.002 and abs(abs(p.x)-x)<.002:
            ridge_vertices.add(vertex.index)
    # Boolean assembly gives the horn smooth faces. The fold near the root
    # is about 27.7 degrees, just below the general 28-degree cutoff. Explicit
    # design-edge tagging prevents that interval from blending into a bulge.
    count=0
    for edge in obj.data.edges:
        if all(i in ridge_vertices for i in edge.vertices):
            edge.use_edge_sharp=True
            count+=1
    obj["preserved_main_horn_ridge_edges"]=count
    obj.data.update()


def move_to(obj,collection,mat,color):
    for c in list(obj.users_collection):
        c.objects.unlink(obj)
    collection.objects.link(obj)
    obj.data.materials.clear()
    obj.data.materials.append(mat)
    obj.color=mat.diffuse_color
    # Smooth curved molded surfaces, retaining the larger sculpted creases.
    for p in obj.data.polygons:
        if color != "Cyan":p.use_smooth=p.center.y > -65
    obj.data.set_sharp_from_angle(angle=math.radians(28))


def horn_seat_x(y):
    # Recessed plane follows the direction of the blade while leaving a
    # substantial inner wall behind the glued attachment.
    return (A-3.7131868248055)+.235*y/H


def horn_outboard_window(sign, gap=0):
    y0=HORN_ROOT_RELEASE_Y_MM*H;y1=400;z0=0;z1=400
    vv=[]
    for far in [False,True]:
        for y,z in [(y0,z0),(y1,z0),(y1,z1),(y0,z1)]:
            x=500 if far else horn_seat_x(y)+gap
            vv.append((sign*x*X_SCALE,y,z))
    return new_mesh("Main horn recessed separation window",vv,
                    [(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)])


def horn_separation_tool(sign,gap=0):
    source=horn(sign)
    if gap:
        # The printed blade retains the original surfaces; only the hidden
        # seat and front release face receive assembly clearance.
        if X_SCALE!=1:
            for v in source.data.vertices:v.co.x*=X_SCALE
        window=horn_outboard_window(sign,gap)
        y0=HORN_ROOT_RELEASE_Y_MM*H
        for v in window.data.vertices:
            if abs(v.co.y-y0)<.001:v.co.y+=HORN_GLUE_CLEARANCE_MM
        boolean(source,window,"INTERSECT")
        return source
    # Sweep the blade silhouette outward along the insertion direction.
    # A simple imprint would leave an undercut under its sloping lower face.
    margin=.15
    mesh=source.data
    edges=[(mesh.vertices[e.vertices[0]].co,mesh.vertices[e.vertices[1]].co) for e in mesh.edges]
    ys=sorted(set(round(v.co.y,3) for v in mesh.vertices))
    low=[];high=[]
    for y in ys:
        zs=[]
        for a,b in edges:
            if min(a.y,b.y)-.001<=y<=max(a.y,b.y)+.001:
                if abs(a.y-b.y)<.0001:zs.extend([a.z,b.z])
                else:
                    t=max(0,min(1,(y-a.y)/(b.y-a.y)))
                    zs.append(a.z+(b.z-a.z)*t)
        low.append(Vector((y,min(zs))));high.append(Vector((y,max(zs))))
    # Drop redundant projected triangulation points, retaining the circular
    # root dip and the true blade perimeter to within 0.005 mm.
    def simplify(points):
        if len(points)<3:return points
        a,b=points[0],points[-1];d=b-a
        distances=[abs(d.x*(p.y-a.y)-d.y*(p.x-a.x))/max(d.length,1e-10) for p in points[1:-1]]
        greatest=max(distances)
        if greatest<=.005:return [a,b]
        i=distances.index(greatest)+1
        return simplify(points[:i+1])[:-1]+simplify(points[i:])
    points=simplify(low)+list(reversed(simplify(high)))
    area=sum(p.x*points[(i+1)%len(points)].y-points[(i+1)%len(points)].x*p.y for i,p in enumerate(points))
    orientation=1 if area>0 else -1;cap=[]
    for i,p in enumerate(points):
        before=(p-points[i-1]).normalized();after=(points[(i+1)%len(points)]-p).normalized()
        na=orientation*Vector((before.y,-before.x));nb=orientation*Vector((after.y,-after.x))
        shift=(na+nb)*margin/max(.05,1+na.dot(nb))
        if shift.length>2*margin:shift=shift.normalized()*2*margin
        cap.append(p+shift)
    n=len(cap)
    vv=[(sign*(horn_seat_x(p.x) if layer==0 else 500)*X_SCALE,p.x,p.y) for layer in [0,1] for p in cap]
    ff=[tuple(reversed(range(n))),tuple(range(n,2*n))]
    ff += [(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
    result=new_mesh("Horn open insertion pocket",vv,ff)
    delete(source)
    window=horn_outboard_window(sign)
    y0=HORN_ROOT_RELEASE_Y_MM*H
    for v in window.data.vertices:
        if abs(v.co.y-y0)<.001:v.co.y-=HORN_GLUE_CLEARANCE_MM
    boolean(result,window,"INTERSECT")
    return result


def horn_glue_tab(sign,y,z,socket=False):
    # Two chamfered rectangular keys prevent a glued horn rotating. The
    # matching blind sockets provide glue space and allow lateral insertion.
    clearance=HORN_GLUE_CLEARANCE_MM if socket else 0
    ry=4.0+clearance;rz=5.0+clearance;c=.6
    outline=[(-ry+c,-rz),(ry-c,-rz),(ry,-rz+c),(ry,rz-c),
             (ry-c,rz),(-ry+c,rz),(-ry,rz-c),(-ry,-rz+c)]
    stations=[(-HORN_GLUE_TAB_DEPTH_MM-clearance,.40 if not socket else 0),
              (-HORN_GLUE_TAB_DEPTH_MM+.55,0),(1.5,0)]
    vv=[]
    for d,tip in stations:
        for yy,zz in outline:
            yy=math.copysign(max(0,abs(yy)-tip),yy)
            zz=math.copysign(max(0,abs(zz)-tip),zz)
            y1=y+yy;z1=z+zz
            vv.append((sign*(horn_seat_x(y1)+d)*X_SCALE,y1,z1))
    n=len(outline);ff=[tuple(reversed(range(n)))]
    for j in range(len(stations)-1):
        ff += [(j*n+i,j*n+(i+1)%n,(j+1)*n+(i+1)%n,(j+1)*n+i) for i in range(n)]
    ff.append(tuple(range((len(stations)-1)*n,len(stations)*n)))
    return new_mesh("Horn blind glue socket" if socket else "Horn integral glue key",vv,ff)


def separate_main_horns(front_parts,front_whole):
    horns=[]
    for sign,name in [(-1,"Horn_Left_Cyan"),(1,"Horn_Right_Cyan")]:
        # Reuse the exact accepted parametric horn surfaces. This region is
        # above the eye opening and outside the head cavity; only its hidden
        # seating face changes, avoiding coincident-face extraction slivers.
        detachable=horn_separation_tool(sign,HORN_GLUE_CLEARANCE_MM)
        detachable.name=name
        cutter=horn_separation_tool(sign)
        for ob in front_parts+[front_whole]:boolean(ob,cutter,remove=False)
        delete(cutter)
        for y,z in [(-48*H,151*H),(-28*H,158*H)]:
            boolean(detachable,horn_glue_tab(sign,y,z),"UNION")
            socket=horn_glue_tab(sign,y,z,True)
            for ob in front_parts+[front_whole]:boolean(ob,socket,remove=False)
            delete(socket)
        detachable["horn_side"]="Left" if sign<0 else "Right"
        detachable["assembly_direction"]="Press inward along X into the two keyed glue sockets"
        horns.append(detachable)
    return horns


def add_coupon():
    """Separate 28 x 18 x 5 mm coupon; use the mask's intended pocket orientation."""
    coupon=cube("Magnet fit coupon",(0,0,9),(28,5,18))
    for x,clearance in [(-8,.10),(0,.20),(8,.30)]:
        cutter=cylinder_y("Test recess",x,9,-2.7,-2.5+MAGNET_THICKNESS_MM+POCKET_GLUE_ALLOWANCE_MM,
                          (MAGNET_DIAMETER_MM+clearance)/2)
        boolean(coupon,cutter)
    return coupon


def main():
    global TMP, SCENE, X_SCALE
    if bpy.app.version < (4,5,0):
        raise RuntimeError("This revision needs Blender 4.5 or newer for the Manifold solver.")
    log("Creating a new scene; existing scenes and objects are preserved.")
    SCENE=bpy.data.scenes.new("Ninja Mask V28 — upper knot and separate lower streamers")
    bpy.context.window.scene=SCENE
    SCENE.unit_settings.system="METRIC"
    SCENE.unit_settings.scale_length=.001
    SCENE.unit_settings.length_unit="MILLIMETERS"
    TMP=bpy.data.collections.new("Construction")
    SCENE.collection.children.link(TMP)
    white_mat=material("01 White",(.89,.89,.86))
    cyan_mat=material("02 Cyan",(.0,.52,.70))

    outer=hull("White shell")
    inner=hull("Head cavity",WALL_MM)
    boolean(outer,inner,remove=False)
    blue_parts=[brow(),crest(),front_brow_peak(),horn(-1,False),horn(1,False)]+cheek_parts(-1)+cheek_parts(1)+bow_parts()
    blue=blue_parts.pop(0)
    for item in blue_parts:
        boolean(blue,item,"UNION")
    # Cut the circular dip after joining band and horns, so there is a single
    # continuous arc rather than coincident cut surfaces at the overlap.
    for sign in [-1,1]:boolean(blue,horn_notch_tool(sign))
    # Build the single-color solid from overlapping source volumes, before
    # carving the color interface. Re-unioning touching inlays is less robust.
    whole=hull("Whole mask before color separation")
    boolean(whole,blue,"UNION",remove=False)
    boolean(whole,inner,remove=False)

    if SIZE_MODE=="LITERAL_WIDTH":
        xs=[v.co.x for ob in [outer,blue] for v in ob.data.vertices]
        X_SCALE=LITERAL_OVERALL_WIDTH_MM/(max(xs)-min(xs))
        for obj in [outer,blue,inner,whole]:
            for v in obj.data.vertices:
                v.co.x*=X_SCALE
        log("Literal side-to-side width selected; this is an unusually wide costume.")
    else:
        log(f"Head circumference: {HEAD_CIRCUMFERENCE_MM:g} mm before clearance.")

    # Preserve the original six centers and add two beside the ribbon center.
    # These eight top-edge pairs retain the original horizontal joint height.
    magnet_sites=[]
    for th in [2.27,2.52,2.74,-2.27,-2.52,-2.74,math.pi-math.asin(12/(A-6)),-math.pi+math.asin(12/(A-6))]:
        x=(A-6)*math.sin(th);y=-(B-6)*math.cos(th)
        magnet_sites.append((x,y))
        boss=cylinder_z("Under-ribbon magnet backing",x,y,HATCH_TOP-6,HATCH_TOP+6,5.3)
        boolean(outer,boss,"UNION",remove=False)
        boolean(whole,boss,"UNION",remove=False)
        delete(boss)
    guide_sites=[]
    for sign in [-1,1]:
        z=70*H;y=side_trailing_y(z/H)*H;x=sign*(shell_x_at(z,y)-6)
        y=guide_seam_y(x,z)
        guide_sites.append((x,y,z))
        boss=cylinder_y("Guide backing",x,z,y-6,y+6,4.8)
        boolean(outer,boss,"UNION",remove=False)
        boolean(whole,boss,"UNION",remove=False)
        delete(boss)


    # Use the untrimmed cyan solid as the inlay cutter. Cropping it to the
    # cavity/apertures first would make its cut faces coincide with the white
    # shell's faces, which destabilizes subsequent Boolean operations.
    boolean(outer,blue,remove=False)
    boolean(blue,inner,remove=False)
    delete(inner)

    # Cut genuine apertures through both finished material regions.
    eye=eye_cutter()
    boolean(outer,eye,remove=False)
    boolean(blue,eye,remove=False)
    boolean(whole,eye,remove=False)
    delete(eye)
    for x,z in [(-17,43*H),(17,43*H),(-14,72*H),(14,72*H)]:
        vent=cylinder_y("Breathing through-hole",x,z,-B-90,-10,VENT_DIAMETER_MM/2)
        boolean(outer,vent,remove=False)
        boolean(blue,vent,remove=False)
        boolean(whole,vent,remove=False)
        delete(vent)


    rim=lower_rim_tool()
    for ob in [outer,blue,whole]:boolean(ob,rim,remove=False)
    delete(rim)

    # Partition the existing white/cyan design with the unchanged main joint.
    # The rear's cyan material is now the hanging tails, bonded in the same print.
    front_white=split(outer,True,"Front_White")
    front_cyan=split(blue,True,"Front_Cyan")
    back_white=split(outer,False,"Back_White")
    back_cyan=split(blue,False,"Back_Cyan")
    parts={"Front":[front_white,front_cyan],"Back":[back_white,back_cyan]}
    single_parts={"Front":split(whole,True,"Front_single_color"),
                  "Back":split(whole,False,"Back_single_color")}
    delete(outer)
    delete(blue)
    delete(whole)
    pocket_r=(MAGNET_DIAMETER_MM+POCKET_DIAMETRAL_CLEARANCE_MM)/2
    pocket_d=MAGNET_THICKNESS_MM+POCKET_GLUE_ALLOWANCE_MM
    for x,y in magnet_sites:
        for name,z0,z1 in [("Front",FRONT_SEAM-.25,FRONT_SEAM+pocket_d),
                           ("Back",BACK_SEAM-pocket_d,BACK_SEAM+.25)]:
            tool=cylinder_z("Blind under-ribbon magnet recess",x,y,z0,z1,pocket_r)
            for ob in parts[name]+[single_parts[name]]:boolean(ob,tool,remove=False)
            delete(tool)
    for x,y,z in guide_sites:
        front_y=y-SEAM_GAP_MM/2;back_y=y+SEAM_GAP_MM/2
        peg=cylinder_y("Integral alignment peg",x,z,y-4.0,back_y+3,1.8,1.55)
        boolean(single_parts["Front"],peg,"UNION",remove=False)
        # The folded cyan side may cross the end of a guide. Partition the pin
        # before adding its white region, so material volumes never overlap.
        boolean(peg,parts["Front"][1],remove=False)
        boolean(parts["Front"][0],peg,"UNION")
        tool=cylinder_y("Guide socket",x,z,y-4.0,back_y+5.0,1.8+ALIGNMENT_CLEARANCE_MM)
        for ob in parts["Back"]+[single_parts["Back"]]:boolean(ob,tool,remove=False)
        delete(tool)

    # Four matching pairs on each sloped leading edge, placed per the overlay.
    # Seat faces follow the actual seam planes; pocket axes are perpendicular
    # to those planes, so disk magnets sit flush without changing the joint.
    from mathutils.bvhtree import BVHTree
    def part_tree(ob):
        vv,ff=triangles(ob)
        return BVHTree.FromPolygons(vv,ff,all_triangles=True)
    rear_tree=part_tree(single_parts["Back"])
    front_tree=part_tree(single_parts["Front"])
    side_magnet_sites=[]
    side_magnet_details=[]
    for sign in [-1,1]:
        for k,(xx,z) in enumerate([(83.75,32.0),(86.0,35.0),(87.25,47.0),(87.75,57.0)],1):
            rear,n,_,_=rear_tree.ray_cast(Vector((sign*xx,-300,z)),Vector((0,1,0)),600)
            assert rear is not None and n.y<-.1 and abs(n.x)<.05
            front,_,_,_=front_tree.ray_cast(rear+n*.001,n,3)
            assert front is not None
            side_magnet_sites.append(tuple((rear+front)/2))
            side_magnet_details.append(dict(id=("L" if sign<0 else "R")+str(k),
                rear_opening=list(rear),front_opening=list(front),axis_into_rear=list(-n),
                normal_gap_mm=(rear-front).length))
            for name,opening,direction in [("Back",rear,-n),("Front",front,n)]:
                tool=cylinder_z("Sloped edge 6x3 magnet pocket",0,0,-.25,pocket_d,pocket_r)
                rotation=Vector((0,0,1)).rotation_difference(direction)
                for v in tool.data.vertices:v.co=rotation@v.co+opening
                for ob in parts[name]+[single_parts[name]]:boolean(ob,tool,remove=False)
                delete(tool)


    detached_horns=separate_main_horns(parts["Front"],single_parts["Front"])
    reports=[]
    for name,objects in parts.items():
        collection=bpy.data.collections.new(name+" — one physical printed piece")
        SCENE.collection.children.link(collection)
        for obj,mat,color in zip(objects,[white_mat,cyan_mat],["White","Cyan"]):
            report=finalize_mesh(obj)
            move_to(obj,collection,mat,color)
            if name == "Front" and color == "Cyan":
                preserve_main_horn_crease(obj)
            obj["physical_piece"]=name
            obj["export_name"]=name+"_"+color
            obj["units"]="millimeter"
            obj["magnet_pairs_on_physical_piece"]=16
            reports.append(report)
    for obj in detached_horns:
        reports.append(finalize_mesh(obj))
        collection=bpy.data.collections.new(obj["horn_side"]+" main horn — glue in after printing")
        SCENE.collection.children.link(collection)
        move_to(obj,collection,cyan_mat,"Cyan")
        preserve_main_horn_crease(obj)
        obj["physical_piece"]="Horn_"+obj["horn_side"]
        obj["export_name"]="Horn_"+obj["horn_side"]+"_Cyan"
        obj["units"]="millimeter"
    for obj in single_parts.values():
        reports.append(finalize_mesh(obj))
    for r in reports:
        log(f"{r['object']}: {r['nonmanifold_edges']} nonmanifold edges; "
            f"{r['degenerate_faces']} degenerate faces; volume {r['signed_volume_mm3']} mm3")
    out=output_dir()
    (out/"mesh_diagnostics.json").write_text(json.dumps(reports,indent=2))
    failures=[r["object"] for r in reports if r["nonmanifold_edges"] or r["degenerate_faces"] or r["signed_volume_mm3"]<=0]
    if failures:
        raise RuntimeError("Mesh validation failed; exports stopped: "+", ".join(failures)+
                           ". Details saved to "+str(out/"mesh_diagnostics.json"))

    if EXPORT_FILES:
        for name,objects in parts.items():
            for ob in objects:
                write_stl(out/(ob["export_name"]+".stl"),ob)
            write_3mf(out/(name+"_two_color.3mf"),objects)
            write_stl(out/(name+"_single_color.stl"),single_parts[name])
    if EXPORT_FILES:
        for ob in detached_horns:
            write_stl(out/(ob["export_name"]+".stl"),ob)
            write_3mf(out/("Horn_"+ob["horn_side"]+".3mf"),[ob])
    for obj in single_parts.values():
        delete(obj)
    if MAKE_FIT_COUPON:
        coupon=add_coupon()
        if EXPORT_FILES:
            write_stl(out/"Magnet_fit_coupon.stl",coupon)
        delete(coupon)

    measurements={
        "script_version":SCRIPT_VERSION,
        "size_mode":SIZE_MODE,"head_circumference_mm":HEAD_CIRCUMFERENCE_MM,
        "unscaled_head_ellipse_width_depth_mm":[2*HEAD_A,2*HEAD_B],
        "cavity_width_depth_at_forehead_mm":[2*(A-WALL_MM)*X_SCALE,2*(B-WALL_MM)],
        "design_envelope_mm":DESIGN_ENVELOPE_MM,
        "eye_top_from_horn_tip_mm":EYE_TOP_FROM_TOP_MM,"eye_top_z_mm":EYE_TOP,
        "main_horn_tip_z_mm":HORN_TIP_Z,"highest_crown_point_z_mm":MODEL_TOP_Z,
        "eye_opening_max_height_mm":EYE_MAX_HEIGHT_MM,"eye_opening_width_mm":EYE_WIDTH_MM,
        "magnet_pairs":16,"magnets_required":32,"top_magnet_pairs":8,"side_magnet_pairs":8,
        "side_magnet_details":side_magnet_details,
        "side_magnet_centers_xyz_mm":side_magnet_sites,
        "magnet_diameter_thickness_mm":[MAGNET_DIAMETER_MM,MAGNET_THICKNESS_MM],
        "pocket_diameter_depth_mm":[pocket_r*2,pocket_d],"seam_gap_mm":SEAM_GAP_MM,
        "magnet_centers_xy_mm":magnet_sites,"front_seam_z_mm":FRONT_SEAM,"back_seam_z_mm":BACK_SEAM,
        "hatch_top_mm":HATCH_TOP,"horn_rake_degrees_above_horizontal":HORN_RAKE_DEG,"horn_splay_degrees":HORN_SPLAY_DEG,
        "crest_nominal_width_mm":CREST_WIDTH_MM,
        "brow_front_height_addition_mm":BROW_FRONT_HEIGHT_ADDITION_MM,"horn_root_width_factor":HORN_ROOT_WIDTH_FACTOR,
        "main_horn_axis":"Straight; taper local to attachment",
        "horn_and_band_detail":"Short front band flares outward and stops at closed angled ends ahead of the notches; horn blades continue behind", 
        "horn_ridge_relief_mm":HORN_RIDGE_RELIEF_MM,
        "secondary_detail":"Compact folded wedge with a ridge continuing into the short cheek blade",
        "horn_root_setback_mm":HORN_ROOT_SETBACK_MM,"horn_root_edge_trim_mm":HORN_ROOT_EDGE_TRIM_MM,
        "headband_join_points_mm":[band_join_point(-1),band_join_point(1)],"front_band_end_y_mm":BROW_END_Y_MM*H,"headband_surface":"Closed front rim ending at y=-82 mm; no band continuation along horn attachment; separate rear ribbon",
        "front_diamond_primary_faces":4,
        "diamond_outline_mm":diamond_outline(),
        "diamond_front_setback_from_visor_mm":BROW_DIAMOND_SETBACK_MM,
        "diamond_upper_extension_vs_cover_mm":18.0,
        "diamond_lower_extension_vs_cover_mm":14.0,
        "diamond_side_corner_lowering_vs_cover_mm":5.0,
        "knot_on_upper_half":True,
        "horn_notch_radius_mm":HORN_NOTCH_RADIUS_MM,
        "diamond_front_setback_mm":BROW_DIAMOND_SETBACK_MM,"diamond_relief_scale":DIAMOND_RELIEF_SCALE,
        "brow_forward_relief_mm":BROW_FORWARD_MM,"front_brow_peak_above_eye_mm":BROW_PEAK_HEIGHT_MM,
        "guide_centers_xyz_mm":guide_sites,"vent_count":4,"vent_diameter_mm":VENT_DIAMETER_MM,
        "wall_nominal_mm":WALL_MM,"fit_clearance_radial_mm":FIT_CLEARANCE_MM,
        "nose_cavity_forward_extension_mm":NOSE_CLEARANCE_MM,
        "nose_ridge_additional_projection_mm":FACE_RELIEF_MM,
        "mouth_valley_offset_mm":MOUTH_VALLEY_DEPTH_MM,"lower_edge_setback_mm":LOWER_EDGE_SETBACK_MM,"rear_rim_rise_setting_mm":REAR_RIM_RISE_MM,
        "front_profile_nominal_z_mm":[FRONT_RIM_RISE_MM*H,34*H,39*H,42*H,82*H,110*H],
        "mouth_chevron_width_mm":MOUTH_HALF_WIDTH_MM*2,"front_rim_rise_mm":FRONT_RIM_RISE_MM,
        "side_joint":"Actual cyan side geometry swept along the removal direction; no flat outline step in the white panel",
        "rounded_front_rim_radius_mm":BROW_UPPER_EDGE_RADIUS_MM,
        "front_rim_underside_extension_mm":BROW_UNDERSIDE_DROP_MM,
        "main_horn_tip_ridge_mm":HORN_TIP_RIDGE_MM,
        "main_horn_ridge_shading":"Explicit sharp design edge across both horns, including the shallow root section",
        "preserved_horn_ridge_edges":sum(o.get("preserved_main_horn_ridge_edges",0) for o in [front_cyan]+detached_horns),
        "physical_printed_pieces":4,"main_horns_separate":True,
        "horn_glue_tab_depth_mm":HORN_GLUE_TAB_DEPTH_MM,
        "horn_glue_clearance_per_side_mm":HORN_GLUE_CLEARANCE_MM,
        "horn_separation_front_y_mm":HORN_ROOT_RELEASE_Y_MM*H,
        "horn_tab_centers_yz_mm":[[-48*H,151*H],[-28*H,158*H]],
        "ridge_part_selection":"Logical Front/Cyan role; independent of Blender object name or numeric suffix",
        "side_joint_edge_clearance_mm":.03,"side_joint_method":"Conforming joint beneath actual cyan inner faces",
        "back_cyan_regions":"Hanging ribbon tails below the original top cut",
        "ribbon_folded_strands":2,"ribbon_knot_vertical_span_mm":[(HATCH_TOP+3)*H,(HATCH_TOP+43)*H],
        "vent_centers_xz_mm":[[-17,43*H],[17,43*H],[-14,72*H],[14,72*H]],
        "ribbon_tail_joint":"Upper wrapped knot ends at original mating seam; lower streamers remain on unchanged rear panel","crown_and_crest":"Crown, center crest and four-face diamond retained; short forehead band with outward flares and closed ends",
        "blender_version":bpy.app.version_string,"meshes":reports,
        "limitations":["Unmeasured fit: head shape, padding and eye alignment require a physical fit check.",
                       "Magnet holding force, adhesive retention, printability and comfort are not validated by manifold checks.",
                       "3MF color metadata does not choose a printer, filament slot, supports or print settings."]}
    allv=[ob.matrix_world@v.co for values in list(parts.values())+[detached_horns] for ob in values for v in ob.data.vertices]
    measurements["overall_dimensions_xyz_mm"]=[max(v[i] for v in allv)-min(v[i] for v in allv) for i in range(3)]
    measurements["overall_height_mm"]=measurements["overall_dimensions_xyz_mm"][2]
    (out/"dimensions_and_mesh_checks.json").write_text(json.dumps(measurements,indent=2))
    bpy.data.collections.remove(TMP)
    SCENE["Read me"]="Four physical pieces: front, rear, left main horn and right main horn. Horns glue into blind keyed sockets. Front=-Y. Rear hatch includes lower cyan ribbon tails. Original main cut retained; eight top and eight sloped-edge 6x3 mm magnet pairs. Dimensions are mm. Check child fit before printing."
    SCENE["export_folder"]="Design_Files beside the generator"
    SCENE["script_version"]=SCRIPT_VERSION
    SCENE["sizing_mode"]=SIZE_MODE
    for obj in bpy.context.selected_objects:
        obj.select_set(False)
    for obj in parts["Front"]:
        obj.select_set(True)
    bpy.context.view_layer.objects.active=parts["Front"][0]
    # A sensible inspection view without adding anything to the print geometry.
    for screen in bpy.data.screens:
        for area in screen.areas:
            if area.type=="VIEW_3D":
                area.spaces.active.clip_end=10000
                area.spaces.active.shading.color_type="MATERIAL"
                rv=area.spaces.active.region_3d
                rv.view_distance=460
                rv.view_location=(0,0,125)
                rv.view_rotation=Vector((.38,-1,.2)).to_track_quat("Z","Y")
    if SAVE_BLEND:
        # save_as_mainfile(copy=True) writes a deliverable without changing the open file path.
        bpy.ops.wm.save_as_mainfile(filepath=str(out/"Ninja_Mask_V28.blend"),copy=True)
    log("DONE. Files: "+str(out))
    log("Fit coupon holes, left to right: 6.10 / 6.20 / 6.30 mm diameter at default settings.")
    log("Use 32 magnets for 16 pairs: eight top and eight sloped-edge. Check polarity before bonding.")
    parts["Horns"]=detached_horns
    return parts,out


if __name__=="__main__":
    main()
