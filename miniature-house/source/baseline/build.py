#!/usr/bin/env python3
"""miniature-house v05 parametric solid CAD. Units mm; architectural inputs feet.
Run using Python 3.9+ with manifold3d, trimesh, numpy, matplotlib, pillow, shapely.
All generated meshes use the same CSG solids as the CAD review renders.
Local part STLs are translated to a flat z=0 minimum; assembly poses in manifest.json.
No printer connection, upload, or purchases are performed by this script.
"""
import json, math, os, csv
from pathlib import Path
import numpy as np
import manifold3d as md
import trimesh
from shapely.geometry import Polygon
os.environ.setdefault('MPLCONFIGDIR',str(ROOT if False else Path(__file__).resolve().parent / '.matplotlib'))
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
ROOT=Path(__file__).resolve().parent
P=json.loads((ROOT/'parameters.json').read_text());F=304.8/P['scale_denominator']; B=P['border_mm'];H=P['wall_height_ft']*F; W=P['wall_mm'];Z=4.6
parts=[]; checks=[]
def cube(x,y,z,dx,dy,dz): return md.Manifold.cube([dx,dy,dz]).translate([x,y,z])
def union(a): return md.Manifold.batch_boolean(a,md.OpType.Add)
def prism(poly,h,z=0): return md.CrossSection([list(poly)],md.FillRule.NonZero).extrude(h).translate([0,0,z])
def mesh(s):
 m=s.to_mesh64();return trimesh.Trimesh(vertices=np.asarray(m.vert_properties)[:,:3],faces=np.asarray(m.tri_verts),process=True)
from surface_details import roof_relief, stone_relief, DETAIL_LOG
def add(name,s,color,category='print',qty=1):
 if name.startswith('roof-'):s=roof_relief(s,name,P)
 if name in ['front-stone-inserts','pool-stone-piers','coupon-stone-relief']:s=stone_relief(s,name,P)
 if s.is_empty(): raise ValueError('Empty '+name)
 m=mesh(s);mn=m.bounds[0];local=m.copy();local.apply_translation(-mn)
 if category=='print':local.export(ROOT/'parts'/f'{name}.stl')
 m.export(ROOT/'parts'/f'{name}-assembly.obj') if category=='reference' else None
 d=dict(name=name,category=category,color=color,qty=qty,assembly_translation_mm=mn.tolist(),bounds_mm=m.bounds.tolist(),size_mm=m.extents.tolist(),watertight=bool(m.is_watertight),winding_consistent=bool(m.is_winding_consistent),volume_mm3=float(m.volume),components=len(m.split()),triangles=len(m.faces))
 parts.append((d,m,s));return s
hx=B+P['house_offset_x_ft']*F;hy=B+P['house_offset_y_ft']*F
def point(p):return (hx+p[0]*F,hy+p[1]*F)
# Exterior outline digitized from the assessor's labelled lengths; y=0 is street-facing front.
outline_ft=[(0,0),(26,0),(26,17),(19,17),(19,30.5),(23.5,30.5),(23.5,34),(34,34),(34,4.5),(45,4.5),(45,2),(64,2),(64,74),(44,74),(44,67),(40,67),(40,64),(19.5,64),(19.5,80),(0,80)]
poly=Polygon([point(p) for p in outline_ft]);inner=poly.buffer(-W,join_style=2)
shell=prism(poly.exterior.coords,H,Z)-prism(inner.exterior.coords,H+1,Z)
# Opening dimensions are candidates, not dimensions on the county sketch. Rebates face inside.
windows=[];opening_specs=[]
def front_open(label,x,y,width,height,sill,kind='screen'):
 global shell
 xx,yy=point((x,y));ww=width*F;hh=height*F;zz=Z+sill*F
 shell=shell-cube(xx,yy-2,zz,ww,4,hh)
 opening_specs.append(dict(name=label,axis='y',x=xx,y=yy,width=ww,head=zz+hh))
 # Inside-facing rebate with 0.75-mm edge lip around aperture.
 shell=shell-cube(xx-.75,yy+.65,zz-.75,ww+1.5,.65,hh+1.5)
 windows.append(dict(name=label,width_mm=ww+1.1,height_mm=hh+1.1,depth_candidate_mm=P['glazing_pocket_candidate_mm'],material=kind))
 # Nominal sheet/backing shown as separate reference geometry; omit when printing.
 insert=cube(xx-.4,yy+.83,zz-.4,ww+.8,1.0 if kind=='door' else .25,hh+.8)
 if label.startswith('garage'):
  cols=2 if label=='garage-single' else 4
  for row in range(5):
   for col in range(cols):
    cw=ww/cols;ch=hh/5
    insert=insert-cube(xx+col*cw+.6,yy+.7,zz+row*ch+.6,cw-1.2,.45,ch-1.2)
 color='#343c3c' if kind=='screen' else ('#514e46' if label=='entry-door' else '#ac9a77' if kind=='door' else '#6e929b')
 add(label+'-insert',insert,color,'print' if kind=='door' else 'reference')
for arg in [('left-front-1',4,0,3.5,5,3),('left-front-2',14,0,9,7,1.5),('entry-door',27.2,34,3.5,8.2,0.2,'door'),('entry-sidelight-L',25.2,34,1.6,7.8,.4,'clear'),('entry-sidelight-R',31.1,34,1.6,7.8,.4,'clear'),('garage-single',35.1,4.5,8.8,8,.2,'door'),('garage-double',46,2,17,8,.2,'door')]: front_open(*arg)
# Wide front stone-bay window has a central divider visible in the listing.
xx,yy=point((18.5,0));add('front-window-divider',cube(xx-.3,yy-.2,Z+1.5*F,.6,1,7*F),'#c4baa2')
# Rear opening x20.5..38.5 at y64: four-panel patio glazed opening.
def rear_open(label,x,y,width,height,sill,kind='screen'):
 global shell
 xx,yy=point((x,y));ww=width*F;hh=height*F;zz=Z+sill*F
 shell=shell-cube(xx,yy-2,zz,ww,4,hh)
 opening_specs.append(dict(name=label,axis='y',x=xx,y=yy,width=ww,head=zz+hh))
 shell=shell-cube(xx-.75,yy-1.3,zz-.75,ww+1.5,.65,hh+1.5)
 windows.append(dict(name=label,width_mm=ww+1.1,height_mm=hh+1.1,depth_candidate_mm=.55,material=kind))
 add(label+'-insert',cube(xx-.4,yy-1.08,zz-.4,ww+.8,.25,hh+.8),'#343c3c' if kind=='screen' else ('#74614d' if kind=='door' else '#6e929b'),'print' if kind=='door' else 'reference')
rear_open('rear-four-panel',21,64,14.5,8,.2,'clear')
rear_open('rear-hinged-door',36.8,64,2.6,8,.2,'clear')
rear_open('rear-left',3,80,13,5,2)
rear_open('rear-dining',47,74,12,5,2)
# Four-panel muntins are separate thickened removable bars, not unsupported thin trim.
xx,yy=point((21,64))
frame=union([cube(xx+i*(14.5/4)*F-.25,yy-1,Z+.2*F,.65,1,8*F) for i in range(1,4)])
add('patio-mullions',frame,'#4b4941')
xx,yy=point((19,21));shell=shell-cube(xx-2,yy,Z+3*F,4,5*F,5*F)
shell=shell-cube(xx-1.3,yy-.75,Z+3*F-.75,.65,5*F+1.5,5*F+1.5)
add('courtyard-side-screen-insert',cube(xx-1.08,yy-.4,Z+3*F-.4,.25,5*F+.8,5*F+.8),'#343c3c','reference')
windows.append(dict(name='courtyard-side-screen',width_mm=5*F+1.1,height_mm=5*F+1.1,depth_candidate_mm=.55,material='screen'))
opening_specs.append(dict(name='courtyard-side-screen',axis='x',x=xx,y=yy,width=5*F,head=Z+8*F))
# The illustrative slicer did not generate support under long shell lintels.
# Separate head strips retain the assembled silhouette but print flat with no long bridge.
full_shell=shell
for op in opening_specs:
 h=op['head'];height=Z+H-h+.02
 if op['axis']=='y':region=cube(op['x'],op['y']-2,h-.01,op['width'],4,height)
 else:region=cube(op['x']-2,op['y'],h-.01,4,op['width'],height)
 cap=shell^region
 if not cap.is_empty():
  add('lintel-'+op['name'],cap,'#d3c3a7');shell=shell-region
add('stucco-shell',shell,'#d3c3a7')
# Footing tray with concealed locator holes; open interior for glazing access.
foot=prism(poly.exterior.coords,1.6,Z-1.6)
locs=[point((3,5)),point((59,8)),point((4,74)),point((58,69))]
for x,y in locs:foot=foot-cube(x,y,Z-2,2.5,2.5,3)
add('foundation-tray',foot,'#c1b094')
# Separate low stone skirts; appearance block-outs, no invented stone texture.
stone=[cube(hx,hy-.65,Z,12*F,.7,2.6*F)]
# Full-height stone bay, with the tall paired screened aperture preserved.
face=cube(hx+12*F,hy-.7,Z,14*F,.75,9.4*F)-cube(hx+14*F-.1,hy-1,Z+1.5*F-.1,9*F+.2,2,7*F+.2)
stone.append(face)
for x,y,dx in [(34,4.5,1.1),(44,4.5,1.0),(45,2,1.0),(63,2,1.0)]:
 xx,yy=point((x,y));stone.append(cube(xx-.25,yy-.65,Z,dx*F+.5,.7,2.7*F))
add('front-stone-inserts',union(stone),'#a38e70')
# Photo correction: one lower passage and THREE SMALL UPPER decorative apertures.
# V02's three full-height passages were wrong. Courtyard behind remains open to sky.
px,py=point((26,5));pw=8*F;ph=13.5*F
portal=cube(px,py,Z,pw,2,ph)-cube(px+.8*F,py-1,Z,6.4*F,4,9.3*F)
for i in range(3):portal=portal-cube(px+(1.5+2*i)*F,py-1,Z+11.0*F,.75*F,4,1.7*F)
portal=portal+cube(px,py,Z,.8*F,4*F,ph)+cube(px+pw-.8*F,py,Z,.8*F,4*F,ph)
add('three-opening-portal',portal,'#d3c3a7')
# Fine grille is a separate flat reference insert; keep fragile bars separate from the print.
grille=[]
for i in range(3):
 for shift in [.21,.51]:grille.append(cube(px+(1.5+2*i+shift)*F,py+.8,Z+11*F,.20,.3,1.7*F))
add('portal-grille-reference',union(grille),'#dedfd5','reference')
# Hip roofs built as solid convex hip caps; topology provisional, separated to preserve open courtyard.
placed_roofs=[]
def hip(name,x,y,dx,dy,eave_ft=10,rise_ft=None):
 if rise_ft is None:rise_ft=P['roof_rise_ft']
 x,y=point((x,y));dx*=F;dy*=F;e=.8;z=Z+eave_ft*F+.9
 # solid flat undersurface 1.0 mm; rise is provisional architectural value
 pts=[[x-e,y-e,z],[x+dx+e,y-e,z],[x+dx+e,y+dy+e,z],[x-e,y+dy+e,z]]
 if dy>=dx:pts += [[x+dx/2,y+dx/2,z+rise_ft*F],[x+dx/2,y+dy-dx/2,z+rise_ft*F]]
 else:pts += [[x+dy/2,y+dy/2,z+rise_ft*F],[x+dx-dy/2,y+dy/2,z+rise_ft*F]]
 roof=md.Manifold.hull_points(pts+[[p[0],p[1],p[2]-.9] for p in pts[:4]])
 if name!='roof-portal':roof=roof-portal
 # Remove any shared eave interference from later parts; first part owns overlap.
 if placed_roofs: roof=roof-union(placed_roofs)
 placed_roofs.append(roof)
 return add(name,roof,'#9c7960')
hip('roof-left-front',0,0,26,17)
hip('roof-left-mid',0,17,19,47)
# Rear projecting owner's wing is a GABLE in the photos, not a hip.
def rear_gable():
 x,y=point((0,64));dx=19.5*F;dy=16*F;z=Z+H;rise=3.0*F;e=.8
 outer=md.Manifold.hull_points([[xx,yy,zz] for yy in [y-e,y+dy+e] for xx,zz in [(x-e,z),(x+dx+e,z),(x-e,z+.9),(x+dx+e,z+.9),(x+dx/2,z+.9+rise)]])
 inner=md.Manifold.hull_points([[xx,yy,zz] for yy in [y-e-1,y+dy+e+1] for xx,zz in [(x+1.2,z-2),(x+dx-1.2,z-2),(x+dx/2,z+rise-.3)]])
 cap=outer-inner
 if placed_roofs:cap=cap-union(placed_roofs)
 placed_roofs.append(cap);cap=add('roof-left-rear-gable',cap,'#a18b72')
 add('coupon-gable-roof-edge',cap^cube(x-1,y+dy*.5,z-1,dx+2,10,rise+3),'#a18b72')
 tri=md.Manifold.hull_points([[xx,yy,zz] for yy in [y+dy-W,y+dy] for xx,zz in [(x,z),(x+dx,z),(x+dx/2,z+rise-.6)]])
 add('rear-gable-stucco-infill',tri,'#d3c3a7')
rear_gable()
hip('roof-main',19,34,45,30)
hip('roof-right-mid',34,26,30,8)
hip('roof-garage',34,4.5,30,21.5)
hip('roof-rear-right',44,64,20,10)
hip('roof-portal',26,4.7,8,4.2,13.5,.9)
# Covered rear patio footprint from assessor, connected roof remains a provisional separate cap.
hip('roof-covered-patio',19.5,64,24.5,10,10,2)
patposts=[]
for x in [20,42.5]:
 xx,yy=point((x,73.5));patposts.append(cube(xx,yy,3.8,2,2,Z+H-3.8))
add('patio-posts',union(patposts),'#d3c3a7')
# Site: rectangular planning envelope, NOT the exact curved lot perimeter from the plat.
sitew=P['lot_width_ft']*F+2*B;sited=P['lot_depth_ft']*F+2*B
# Removable shallow basin with rounded/inset outline, 1.2 floor and 1.2-mm walls.
pl=P['pool_length_ft']*F;pd=P['pool_width_ft']*F
# Photo-informed oblong shape: rounded left end, angular right end and front tanning shelf.
# NOT a traced/measured pool survey. All absolute dimensions/positions remain candidates.
poolpts=[(pl*.22,0),(pl*.82,0),(pl*.95,pd*.07),(pl,pd*.20),(pl,pd*.82),(pl*.91,pd),(pl*.22,pd)]
for angle in np.linspace(90,270,15):
 a=math.radians(angle);poolpts.append((pl*.22+pl*.22*math.cos(a),pd/2+pd/2*math.sin(a)))
poolpoly=Polygon(poolpts).buffer(2,join_style=1).buffer(-2,join_style=1)
px=B+P['pool_x_ft']*F;py=B+P['pool_y_ft']*F
outer=prism(poolpoly.exterior.coords,5).translate([px,py,0]);ip=poolpoly.buffer(-1.2)
basin=outer-prism(ip.exterior.coords,5,1.2).translate([px,py,0])
shelf=cube(px+pl*.64,py+1.2,1.2,pl*.32,pd*.34,2.0)^outer
basin=basin+shelf
add('pool-basin',basin,'#69b8b4')
# Pool deck opening is genuine through-cut, not a blue solid on top of a base.
poolcut=prism(poolpoly.buffer(.4).exterior.coords,8,-1).translate([px,py,0])
base=cube(0,0,0,sitew,sited,3)-poolcut
for x,y in locs:base=base-cube(x,y,1,2.5,2.5,3)
# Modular split across front/house/rear for unknown printer bed. Exact seam connectors not locked.
for n,y0,y1 in [('base-front',0,85),('base-middle',85,230),('base-rear',230,sited)]:
 add(n,base^cube(-1,y0,-1,sitew+2,y1-y0,6),'#c5b89a')
# A loose, removable paver patio/deck; seam at pool opening.
deck=cube(B+5*F,B+105*F,3,70*F,35*F,.8)-poolcut
# Accessory attachment holes: candidate 1-mm diameter, later coupon fit required.
proppts=[(58,126),(69,126),(63,121),(63,131),(14,118),(14,125)]
for x,y in proppts:deck=deck-md.Manifold.cylinder(2,.5,.5,16).translate([B+x*F,B+y*F,2.5])
add('rear-paver-deck',deck,'#b9a38b')
add('driveway-paver-insert',cube(B+42*F,B,3,30*F,25*F,.7),'#b9a38b')
add('courtyard-floor',cube(hx+26*F,hy+5*F,3,8*F,29*F,.7)+cube(hx+23.5*F,hy+30.5*F,3,2.7*F,3.5*F,.7),'#b9a38b')
add('courtyard-gravel-bed',cube(hx+19*F,hy+17*F,3,7*F,13.5*F,.5),'#afa38d')
from shapely.geometry import LineString
curve=[(px+pl*(.35+.30*t),py+pd+1+2.4*math.sin(math.pi*t)) for t in np.linspace(0,1,21)]
wallpoly=LineString(curve).buffer(.8,cap_style=2)
add('raised-pool-tile-wall',prism(wallpoly.exterior.coords,5.5,3.8),'#40b0b6')
piers=[]
for x,y in [curve[0],curve[-1]]:
 pier=cube(x-2,y-2,3.8,4,4,7)+cube(x-2.3,y-2.3,10.6,4.6,4.6,.6)
 pier=pier-md.Manifold.cylinder(2,.5,.5,16).translate([x,y,10])
 piers.append(pier)
add('pool-stone-piers',union(piers),'#a38e70')
# Flat removable pergola lattice and four robust separate posts.
gx=B+P['pergola_x_ft']*F;gy=B+P['pergola_y_ft']*F;gw=P['pergola_width_ft']*F;gd=P['pergola_depth_ft']*F;gh=9*F
for i,(a,b) in enumerate([(0,0),(gw-1.5,0),(0,gd-1.5),(gw-1.5,gd-1.5)]):
 post=cube(gx+a,gy+b,3.8,1.5,1.5,gh)
 # Notched top seat for lattice rail.
 # Flat top supports the lowest cross member; no undersized notch.
 add(f'pergola-post-{i+1}',post,'#665747')
lat=[cube(gx,gy,3.8+gh,gw,1.4,1.4),cube(gx,gy+gd-1.4,3.8+gh,gw,1.4,1.4)]
for i in range(28):lat.append(cube(gx+i*(gw-.9)/27,gy,3.8+gh+1.1,.9,gd,1.1))
for i in range(6):lat.append(cube(gx,gy+i*(gd-1.2)/5,3.8+gh-.3,gw,1.2,1.6))
lattice=union(lat).translate([0,0,.3])
add('pergola-flat-lattice',lattice,'#665747')
add('coupon-pergola-flat-lattice',lattice^cube(gx+4*(gw-.9)/27,gy+6,3.8+gh-1,14*(gw-.9)/27+.9,20,5),'#665747')
add('coupon-pergola-bearing-post',cube(0,0,0,1.5,1.5,8),'#665747')
# A removable positioning jig is a candidate only; holes are .2 mm clearance per side.
jig=cube(0,0,0,gw+6,gd+6,1.5)-cube(6,6,-1,gw-6,gd-6,4)
for a,b in [(0,0),(gw-1.5,0),(0,gd-1.5),(gw-1.5,gd-1.5)]:jig=jig-cube(a+2.8,b+2.8,-1,1.9,1.9,4)
add('pergola-positioning-jig',jig,'#c5b89a')
# Furniture prototypes: filled slat regions, strengthened 0.8-mm legs, flat print soles.
def chair(style):
 r=125/P['scale_denominator'];w=6.4*r if style=='adirondack' else 5.5;d=(7*r if style=='adirondack' else 5.7);h=6.8*r if style=='adirondack' else 8
 seat=2.1
 a=[cube(.3,.3,seat,w-.6,d-1,.8)]
 # Leaning, broad upper Adirondack back silhouette; slat gaps deliberately filled.
 if style=='adirondack':
  back=md.Manifold.hull_points([[x,y,z] for x,y,z in [(0,d-.5,h),(w,d-.5,h),(.5,d-2,seat),(w-.5,d-2,seat),(0,d+.3,h),(w,d+.3,h),(.5,d-1.2,seat),(w-.5,d-1.2,seat)]])
 else:back=cube(0,d-.8,seat,w,.8,h-seat)
 a.append(back)
 for x in [.2,w-1]:
  for y in [.5,d-1.5]:a.append(cube(x,y,0,.8,.8,seat+.3))
 if style=='adirondack':
  for x in [0,w-.9]:a.extend([cube(x,.8,4,.9,d-1,.8),cube(x,.8,seat,.8,.8,2.1)])
 return union(a)
def lounger():
 # Monotone curved centerline with a .9-mm structural skin; avoids isolated thin tips.
 from shapely.geometry import LineString
 r=125/P['scale_denominator'];center=[(y*r,z*r) for y,z in [(0,.45),(2,.45),(6,.45),(9,.7),(11,2),(13,4.2),(15,4.7)]]
 thick=LineString(center).buffer(.45,cap_style=1,join_style=1)
 return md.CrossSection([list(thick.exterior.coords)],md.FillRule.NonZero).extrude(5.2*r).transform([[0,0,1,0],[1,0,0,0],[0,1,0,0]])

def table():
 return union([md.Manifold.cylinder(.8,5,5,48).translate([5,5,6])]+[cube(x,y,0,.8,.8,6.2) for x in [1.5,7.7] for y in [1.5,7.7]])
propdefs=[('adirondack-chair',chair('adirondack'),2),('pool-lounger',lounger(),2),('patio-chair',chair('patio'),4),('patio-table',table(),1)]
for name,s,q in propdefs:add(name,s,'#f0eee2' if name=='pool-lounger' or name=='patio-table' else '#42aeb3' if name=='adirondack-chair' else '#4e4940','print',q)
sceneprops=[];placements=[]
def place_prop(name,x,y,angle=0,z=3.8):
 s=next(s for n,s,q in propdefs if n==name).rotate([0,0,angle]);mm=mesh(s);mn=mm.bounds[0];s=s.translate([-mn[0]+B+x*F,-mn[1]+B+y*F,z-mn[2]])
 color='#f0eee2' if name in ['pool-lounger','patio-table'] else '#42aeb3' if name=='adirondack-chair' else '#4e4940'
 sceneprops.append((mesh(s),color));placements.append(dict(name=name,x_ft=x,y_ft=y,angle_deg=angle,z_mm=z,status='photo-informed arrangement, estimated coordinates'))
for y in [118,125]:place_prop('adirondack-chair',14,y,90)
for x in [41.5,47]:place_prop('pool-lounger',x,115.6,180,z=3.2)
place_prop('patio-table',62,124)
for x,y,a in [(59,125,90),(67.5,125,-90),(63.2,121,180),(63.2,130,0)]:place_prop('patio-chair',x,y,a)
# Dedicated furniture test uses actual representative part, not promise of print success.
add('coupon-furniture-adirondack',chair('adirondack'),'#42aeb3')
# Window rebate coupon, including deliberately oversize back access.
coupon=cube(0,0,0,24,2,18)-cube(5,-1,4,12,4,10)-cube(4.3,1.3,3.3,13.4,1,11.4)
add('coupon-window-pocket',coupon,'#d3c3a7')
# Ladder of test slots matching glazing + finish tolerances, physically untested.
ladder=cube(0,0,0,32,10,3)
for i,slot in enumerate([.35,.45,.55,.65]):ladder=ladder-cube(3+i*7,2,1,slot,7,3)
add('coupon-glazing-clearance-ladder',ladder,'#d3c3a7')
# Pergola 30-mm span + joint, roof edge and locator dry-fit coupons.
span=union([cube(0,0,0,1.5,3,8),cube(28.5,0,0,1.5,3,8),cube(0,0,7,30,1.4,1.4),cube(0,0,8.1,.9,12,1.1),cube(29.1,0,8.1,.9,12,1.1)])
add('coupon-pergola-span-joint',span,'#665747')
roofcoupon=md.Manifold.hull_points([[0,0,0],[25,0,0],[25,12,0],[0,12,0],[0,12,4],[25,12,4]])
add('coupon-roof-edge',roofcoupon,'#9c7960')
add('coupon-pool-finish-well',cube(0,0,0,20,15,5)-cube(1.2,1.2,1.2,17.6,12.6,5),'#69b8b4')
locator=cube(0,0,0,18,12,2)
for i,gap in enumerate([.15,.25,.35]):locator=locator-cube(2+i*5,3,-1,2+gap*2,2+gap*2,4)
add('coupon-locator-sockets',locator,'#c1b094')
add('coupon-locator-pin',cube(0,0,0,5,5,1)+cube(1.5,1.5,.9,2,2,3),'#c1b094')
# Four foundation alignment plugs; unglued mechanical fit candidate.
add('foundation-locator-plug',cube(0,0,0,2,2,3),'#c1b094',qty=4)
# Actual surface coupons: a cropped finished roof face, plus the same stone generator on a flat panel.
roof_sample=next(s for d,m,s in parts if d['name']=='roof-left-front')
add('coupon-roof-tile-relief',roof_sample^cube(hx+13*F-10,hy+2,Z+H-.2,20,15,12),'#c8c8c0')
add('coupon-stone-relief',cube(0,0,0,22,.8,14),'#c8c8c0')
(ROOT/'surface-detail-log.json').write_text(json.dumps(DETAIL_LOG,indent=2))
# Case only as reference envelope, excluded from printing. Nominal 5-mm clearance all around.
case=dict(internal_width_min_mm=sitew+10,internal_depth_min_mm=sited+10,internal_height_min_mm=75,acrylic_candidate_mm=3,exterior_width_candidate_mm=sitew+16,exterior_depth_candidate_mm=sited+16,status='PLANNING ONLY: measure actual internal case dimensions before finalizing scenic base')
# Save dimension and mesh results, retaining actual global mesh for review.
manifest = {'version': P['version'], 'units': 'mm', 'scale': f"1:{P['scale_denominator']} WORKING STANDARD", 'front': 'y=0; x left-to-right viewed from street; +y toward backyard; +z up; geographic north not assigned', 'site_planning_size_mm': [sitew, sited, 3], 'case': case, 'parts': [p[0] for p in parts], 'glazing_cut_candidates': windows, 'furniture_placements': placements}
(ROOT/'manifest.json').write_text(json.dumps(manifest,indent=2))
with (ROOT/'parts.csv').open('w') as f:
 wr=csv.writer(f);wr.writerow(['part','type','qty','X_mm','Y_mm','Z_mm','watertight','components','triangles'])
 for d,_,_ in parts:wr.writerow([d['name'],d['category'],d['qty'],*[round(v,3) for v in d['size_mm']],d['watertight'],d['components'],d['triangles']])
# Actual geometry audit, independent opening probes and courtyard roof exclusion.
for d,m,s in parts:checks.append(dict(part=d['name'],pass_mesh=d['watertight'] and d['winding_consistent'] and d['volume_mm3']>0,**{k:d[k] for k in ['triangles','components','size_mm']}))
roofsolids=union([s for d,m,s in parts if d['name'].startswith('roof-')])
probe=cube(hx+27*F,hy+10*F,Z+H-1,6*F,20*F,20)
checks.append({'check':'open-to-sky-courtyard central 6x20ft column','pass':(roofsolids^probe).is_empty()})
checks.append({'check':'shell rear glazed opening through-wall probe','pass':(shell^cube(hx+25*F,hy+64*F-1,Z+3*F,3*F,2,2*F)).is_empty()})
checks.append({'check':'portal central lower pedestrian opening','pass':(portal^cube(hx+29*F,hy+5*F-1,Z+F,2*F,4,6*F)).is_empty()})
checks.append({'check':'shell entry through-wall probe','pass':(shell^cube(hx+28*F,hy+34*F-1,Z+3*F,1*F,2,2*F)).is_empty()})
(ROOT/'mesh-checks.json').write_text(json.dumps(checks,indent=2))
print("Baseline geometry exported; current walls are generated separately.")
