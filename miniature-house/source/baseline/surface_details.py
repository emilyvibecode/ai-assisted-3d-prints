"""Bounded photo-informed relief; changes finish geometry, never architectural topology."""
import math,hashlib
import numpy as np,trimesh,manifold3d as md
from shapely.geometry import Polygon,box
from shapely.geometry.polygon import orient
from shapely.ops import unary_union
DETAIL_LOG=[]
def mesh(s):
 m=s.to_mesh64();return trimesh.Trimesh(vertices=np.asarray(m.vert_properties)[:,:3],faces=np.asarray(m.tri_verts),process=True)
def polygons(g):
 if g.is_empty:return []
 if g.geom_type=='Polygon':return [g]
 return [p for a in getattr(g,'geoms',[]) for p in polygons(a)]
def extruded(g,height,matrix):
 contours=[]
 for p in polygons(g):
  p=orient(p,sign=1);contours.append(list(p.exterior.coords));contours.extend(list(h.coords) for h in p.interiors)
 if not contours:return md.Manifold()
 return md.CrossSection(contours,md.FillRule.NonZero).extrude(height).transform(matrix)
def union(a):return md.Manifold.batch_boolean(a,md.OpType.Add)
def roof_relief(s,name,P):
 original=s.volume();m=mesh(s);groups={}
 for face,n in zip(m.faces,m.face_normals):
  if n[2]<.65:continue
  v=m.vertices[face];a=-n[0]/n[2];b=-n[1]/n[2];c=float(v[0,2]-a*v[0,0]-b*v[0,1]);key=(round(a,5),round(b,5),round(c,4));groups.setdefault(key,[]).append(Polygon(v[:,:2]))
 additions=[];tiles=0
 for (a,b,c),triangles in groups.items():
  mask=unary_union(triangles).buffer(-.9,join_style=2)
  if mask.is_empty or mask.area<6:continue
  gradient=math.hypot(a,b);u=np.array([a,b])/gradient if gradient>.001 else np.array([0.,1.]);v=np.array([-u[1],u[0]])
  # Transform face mask into across-slope/along-row coordinates.
  uv=[]
  for poly in polygons(mask):
   ex=[(float(np.sum(np.array(xy)*u)),float(np.sum(np.array(xy)*v))) for xy in poly.exterior.coords]
   hs=[[(float(np.sum(np.array(xy)*u)),float(np.sum(np.array(xy)*v))) for xy in h.coords] for h in poly.interiors];uv.append(Polygon(ex,hs))
  maskuv=unary_union(uv);mnx,mny,mxx,mxy=maskuv.bounds;pitch=P['roof_tile_pitch_mm'];tw=P['roof_tile_width_mm'];gap=P['roof_tile_joint_mm'];rects=[]
  for row in range(math.floor(mnx/pitch),math.ceil(mxx/pitch)+1):
   x0=row*pitch+gap/2;x1=(row+1)*pitch-gap/2;offset=tw/2 if row%2 else 0
   for col in range(math.floor((mny-offset)/tw)-1,math.ceil((mxy-offset)/tw)+1):
    y0=col*tw+offset+gap/2;y1=(col+1)*tw+offset-gap/2
    q=box(x0,y0,x1,y1).intersection(maskuv)
    # Reject edge fragments too small for a .4-mm nozzle; roof body remains underneath.
    for g in polygons(q):
     bx=g.bounds
     if g.area>=.45 and min(bx[2]-bx[0],bx[3]-bx[1])>=.6:rects.append(g);tiles+=1
  if not rects:continue
  pattern=unary_union(rects);mat=[[u[0],v[0],0,0],[u[1],v[1],0,0],[a*u[0]+b*u[1],a*v[0]+b*v[1],1,c-.03]]
  additions.append(extruded(pattern,P['roof_tile_relief_mm']+.03,mat))
 if additions:s=s+union(additions)
 DETAIL_LOG.append(dict(part=name,style='staggered low-profile tile joints; stylized, not measured',tile_patches=tiles,relief_mm=P['roof_tile_relief_mm'],pitch_mm=P['roof_tile_pitch_mm'],width_mm=P['roof_tile_width_mm'],joint_mm=P['roof_tile_joint_mm'],added_volume_mm3=float(s.volume()-original)))
 print(name,'tile patches',tiles,flush=True);return s
def stone_relief(s,name,P):
 original=s.volume();m=mesh(s);groups={}
 for f,n in zip(m.faces,m.face_normals):
  if abs(n[2])>.01 or max(abs(n[0]),abs(n[1]))<.99:continue
  if name in ['front-stone-inserts','coupon-stone-relief'] and n[1]>-.99:continue
  vv=m.vertices[f];normal=np.array([round(n[0]),round(n[1]),0.]);d=float(np.sum(normal*vv[0]));key=(int(normal[0]),int(normal[1]),round(d,4));u=np.array([-normal[1],normal[0],0.]);face=Polygon([(float(np.sum(x*u)),float(x[2])) for x in vv]);groups.setdefault(key,[]).append(face)
 additions=[];blocks=0
 for index,((nx,ny,d),triangles) in enumerate(groups.items()):
  face=unary_union(triangles).buffer(-.18,join_style=2)
  if face.is_empty:continue
  mnx,mnz,mxx,mxz=face.bounds
  # Very thin veneer cut edges/cap bands deliberately stay smooth; no fragile fins.
  if mxx-mnx<3 or mxz-mnz<1.8:continue
  rng=np.random.default_rng(int(hashlib.sha256((name+str(index)).encode()).hexdigest()[:8],16));rows=[[],[],[]];z=math.floor(mnz/1.25)*1.25
  while z<mxz:
   rh=float(rng.uniform(1.0,1.5));x=mnx-float(rng.uniform(0,3))
   while x<mxx:
    w=float(rng.uniform(2.0,4.8));j=P['stone_joint_mm'];q=Polygon([(x+j/2,z+j/2),(x+w-j/2,z+j/2+.07),(x+w-j/2,z+rh-j/2),(x+w*.6,z+rh-j/2-.08),(x+j/2,z+rh-j/2+.02)]).intersection(face)
    for poly in polygons(q):
     b=poly.bounds
     if poly.area>=.45 and min(b[2]-b[0],b[3]-b[1])>=.55:rows[int(rng.integers(0,3))].append(poly);blocks+=1
    x+=w
   z+=rh
  ux,uy=-ny,nx
  for k,stones in enumerate(rows):
   if not stones:continue
   depth=P['stone_relief_min_mm']+(P['stone_relief_max_mm']-P['stone_relief_min_mm'])*k/2
   mat=[[ux,0,nx,nx*(d-.03)],[uy,0,ny,ny*(d-.03)],[0,1,0,0]];additions.append(extruded(unary_union(stones),depth+.03,mat))
 if additions:s=s+union(additions)
 DETAIL_LOG.append(dict(part=name,style='photo-informed irregular coursed ledgestone relief; not traced individual stones',blocks=blocks,relief_range_mm=[P['stone_relief_min_mm'],P['stone_relief_max_mm']],joint_mm=P['stone_joint_mm'],added_volume_mm3=float(s.volume()-original)))
 print(name,'stone blocks',blocks,flush=True);return s
