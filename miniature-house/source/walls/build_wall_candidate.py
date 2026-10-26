"""Editable v06 wall candidate using preserved v05 base wall frame and explicit new opening parameters.
No printer operations. Retains v05 front/rear/courtyard geometry and existing printed interfaces.
"""
from pathlib import Path
import json,hashlib,csv,shutil
import numpy as np,trimesh,manifold3d as md
R=Path(__file__).resolve().parent;P=json.loads((R/'wall-parameters.json').read_text());M=json.loads((R/'reference-inputs/v05-manifest.json').read_text());meta={d['name']:d for d in M['parts']};F=304.8/P['scale_denominator'];hx=P['border_mm']+P['house_offset_x_ft']*F;hy=P['border_mm']+P['house_offset_y_ft']*F;Z=P['assembly_floor_z_mm'];W=P['wall_mm'];checks=[];rows=[]
def solid(m):return md.Manifold(md.Mesh64(np.asarray(m.vertices,dtype=np.float64),np.asarray(m.faces,dtype=np.uint64)))
def mesh(s):
 m=s.to_mesh64();return trimesh.Trimesh(vertices=np.asarray(m.vert_properties)[:,:3],faces=np.asarray(m.tri_verts),process=True)
def cube(x,y,z,w,d,h):return md.Manifold.cube([w,d,h]).translate([x,y,z])
def export(name,s,kind,rotation):
 m=mesh(s);mn=m.bounds[0];local=m.copy();local.apply_translation(-mn);path=R/'parts'/(name+'.stl');local.export(path);reload=trimesh.load(path,force='mesh');ok=bool(reload.is_watertight and reload.is_winding_consistent and reload.volume>0)
 row=dict(name=name,kind=kind,assembly_translation_mm=mn.tolist(),size_mm=local.extents.tolist(),rotation_xyz_deg=rotation,watertight=bool(reload.is_watertight),winding_consistent=bool(reload.is_winding_consistent),positive_volume=bool(reload.volume>0),components=len(reload.split()),sha256=hashlib.sha256(path.read_bytes()).hexdigest());rows.append(row);checks.append(dict(check='export '+name,pass_check=ok));return s
base=trimesh.load(R/'reference-inputs/v05-stucco-shell.stl',force='mesh');base.apply_translation(meta['stucco-shell']['assembly_translation_mm']);original=solid(base);wall=original;heads=[];glazing=[]
for side in ['left','right']:
 for o in P[side]:
  y=hy+o['station']*F;z=Z+o['sill']*F;wid=o['width']*F;height=o['height']*F;x=hx if side=='left' else hx+64*F
  wall=wall-cube(x-2,y,z,4,wid,height)
  # Inside-facing pocket: preserve 0.65 mm outer lip; compatible with v05 pocket method.
  start=x+P['rebate_start_from_outer_face_mm'] if side=='left' else x-P['rebate_start_from_outer_face_mm']-P['rebate_depth_mm']
  margin=P['rebate_margin_mm'];wall=wall-cube(start,y-margin,z-margin,P['rebate_depth_mm'],wid+2*margin,height+2*margin)
  heads.append(dict(side=side,ID=o['ID'].replace('?',''),y=y,width=wid,head=z+height,x=x))
  glazing.append(dict(ID=o['ID'],side=side,aperture_width_mm=wid,aperture_height_mm=height,reference_insert_width_mm=wid+1.1,reference_insert_height_mm=height+1.1,nominal_sheet_mm=.25,pocket_depth_candidate_mm=.55,material='frosted' if o['ID']=='L04' else 'dark screen / clear sheet per finish',dimension_basis='estimated approved review candidate; measure real sheet and coupon fit before cutting'))
with_pockets=wall
# Split every new head upward to wall top. No printed bridge is left spanning a side window.
newheads=[]
for o in heads:
 region=cube(o['x']-2,o['y'],o['head']-.01,4,o['width'],Z+P['wall_height_ft']*F-o['head']+.02);head=wall^region
 if head.is_empty():raise RuntimeError('Empty head '+str(o))
 wall=wall-region;name='lintel-side-'+o['side']+'-'+o['ID'];rotation=[0,-90 if o['side']=='left' else 90,0];export(name,head,'new side head',rotation);newheads.append(head)
export('miniature-house-v06-wall-frame',wall,'main wall frame',[0,0,0])
reconstructed=wall+md.Manifold.batch_boolean(newheads,md.OpType.Add);difference=(reconstructed-with_pockets).volume()+(with_pockets-reconstructed).volume();checks.append(dict(check='frame plus twelve new heads reconstructs intended pocketed side geometry',symmetric_difference_mm3=float(difference),pass_check=abs(difference)<.001))
for p in sorted((R/'reference-inputs').glob('lintel-*.stl')):
 name=p.stem;m=trimesh.load(p,force='mesh');m.apply_translation(meta[name]['assembly_translation_mm']);rotation=[0,90,0] if name=='lintel-courtyard-side-screen' else [-90,0,0] if name.startswith('lintel-rear-') else [90,0,0];s=solid(m)
 # Preserve original triangle bytes for the twelve existing head parts.
 shutil.copy2(p,R/'parts'/p.name);rows.append(dict(name=name,kind='preserved v05 head',assembly_translation_mm=meta[name]['assembly_translation_mm'],size_mm=meta[name]['size_mm'],rotation_xyz_deg=rotation,watertight=bool(m.is_watertight),winding_consistent=bool(m.is_winding_consistent),positive_volume=bool(m.volume>0),components=len(m.split()),sha256=hashlib.sha256(p.read_bytes()).hexdigest()))
 checks.append(dict(check='preserved '+name,pass_check=hashlib.sha256((R/'parts'/p.name).read_bytes()).hexdigest()==hashlib.sha256(p.read_bytes()).hexdigest()))
# Verify aperture interiors and retained bearing band. New work removes material only above sills.
for o in heads:
 q=next(a for a in P[o['side']] if a['ID'].replace('?','')==o['ID']);test=cube(o['x']-1,o['y']+.05,Z+q['sill']*F+.05,W+2,o['width']-.1,q['height']*F-.1);v=float((reconstructed^test).volume());checks.append(dict(check='clear side aperture '+o['ID'],remaining_solid_mm3=v,pass_check=abs(v)<.001))
band=cube(hx-1,hy-1,Z-.01,64*F+2,80*F+2,1.0);delta=((original^band)-(with_pockets^band)).volume()+((with_pockets^band)-(original^band)).volume();checks.append(dict(check='foundation-contact band unchanged',symmetric_difference_mm3=float(delta),pass_check=abs(delta)<.001))
checks.append(dict(check='outer wall envelope unchanged',pass_check=bool(np.allclose(mesh(reconstructed).bounds,base.bounds,atol=.001)),expected_mm=[162.56,203.2,25.4]))
(R/'candidate-manifest.json').write_text(json.dumps(dict(version='v06 production candidate v01',units='mm',scale='1:120',parts=rows,glazing=glazing,status='digitally verified only after slicing; not physically tested'),indent=2));(R/'geometry-checks.json').write_text(json.dumps(checks,indent=2))
with (R/'parts.csv').open('w') as f:
 w=csv.writer(f);w.writerow(['name','kind','x_mm','y_mm','z_mm','components']);[w.writerow([d['name'],d['kind'],*d['size_mm'],d['components']]) for d in rows]
fail=[c for c in checks if not c['pass_check']];print('Candidate parts',len(rows),'new side windows',len(heads),'failures',fail,flush=True)
if fail:raise RuntimeError('Geometry checks failed')
