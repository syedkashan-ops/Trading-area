import json, math, uuid
from pathlib import Path
import pandas as pd
import streamlit as st
import folium
from streamlit_folium import st_folium

st.set_page_config(page_title='Trading Area Mapper V1', page_icon='🗺️', layout='wide')
DATA=Path('data'); DATA.mkdir(exist_ok=True)
PROJECTS=DATA/'projects.json'

FIELDS=['id','name','omc','category','mogas','hsd','lube','lat','lon','location_method','reference_id','distance_km','road_relation','direction','verified','notes']

def load_projects():
    if PROJECTS.exists():
        try: return json.loads(PROJECTS.read_text(encoding='utf-8'))
        except: pass
    return {}
def save_projects(x): PROJECTS.write_text(json.dumps(x,indent=2),encoding='utf-8')
def hav(a,b,c,d):
    R=6371; p1,p2=map(math.radians,[a,c]); dp=math.radians(c-a); dl=math.radians(d-b)
    q=math.sin(dp/2)**2+math.cos(p1)*math.cos(p2)*math.sin(dl/2)**2
    return 2*R*math.asin(math.sqrt(q))
def destination(lat,lon,km,bearing):
    R=6371; br=math.radians(bearing); p1=math.radians(lat); l1=math.radians(lon); d=km/R
    p2=math.asin(math.sin(p1)*math.cos(d)+math.cos(p1)*math.sin(d)*math.cos(br))
    l2=l1+math.atan2(math.sin(br)*math.sin(d)*math.cos(p1),math.cos(d)-math.sin(p1)*math.sin(p2))
    return math.degrees(p2),math.degrees(l2)
def bearing_from_text(s):
    s=s.lower().strip(); m={'north':0,'n':0,'northeast':45,'ne':45,'east':90,'e':90,'southeast':135,'se':135,'south':180,'s':180,'southwest':225,'sw':225,'west':270,'w':270,'northwest':315,'nw':315}
    return m.get(s)

def new_project(name,radius): return {'name':name,'radius':radius,'outlets':[]}

projects=load_projects()
st.title('Trading Area Mapper — V1')
st.caption('Build a proposed retail outlet trading area with PSO/competitor sales, relative locations and 3/5/10 km analysis.')

with st.sidebar:
    st.header('Project')
    names=list(projects)
    choice=st.selectbox('Open saved project',['New project']+names)
    if choice=='New project':
        pname=st.text_input('Project name','New Trading Area')
        radius=st.selectbox('Trading radius (km)',[3,5,10],index=1)
        if st.button('Create project',type='primary'):
            key=pname.strip() or f'Project {len(projects)+1}'
            projects[key]=new_project(key,radius); save_projects(projects); st.session_state.project=key; st.rerun()
    else: st.session_state.project=choice

key=st.session_state.get('project')
if not key or key not in projects:
    st.info('Create or open a project from the sidebar to begin.')
    st.stop()
p=projects[key]

c1,c2,c3=st.columns([2,1,1])
c1.subheader(p['name']); c2.metric('Radius',f"{p['radius']} km"); c3.metric('Outlets',len(p['outlets']))

T1,T2,T3=st.tabs(['📍 Add / Edit Outlets','🗺️ Trading Area Map','📊 Analysis'])
with T1:
    st.markdown('### Add outlet')
    a,b,c,d=st.columns(4)
    name=a.text_input('Outlet name')
    omc=b.selectbox('OMC',['PSO','SHELL','TOTALENERGIES','ATTOCK','GO','HASCOL','PARCO','BYCO','ASKARI','OTHER'])
    cat=c.text_input('Category','NV')
    kind=d.selectbox('Role',['Existing outlet','Proposed outlet'])
    s1,s2,s3=st.columns(3)
    mg=s1.number_input('MOGAS (KL)',min_value=0.0,step=1.0)
    hsd=s2.number_input('HSD (KL)',min_value=0.0,step=1.0)
    lube=s3.number_input('LUBE (KL)',min_value=0.0,step=0.1)
    method=st.radio('Location method',['Exact coordinates','Relative to an outlet'],horizontal=True)
    lat=lon=None; refid=''; dist=0.; relation=''; direction=''; verified=False
    if method=='Exact coordinates':
        x,y=st.columns(2); lat=x.number_input('Latitude',format='%.7f',value=0.0); lon=y.number_input('Longitude',format='%.7f',value=0.0)
        verified=st.checkbox('Coordinates verified',value=True)
    else:
        valid=[o for o in p['outlets'] if o.get('lat') is not None and o.get('lon') is not None]
        if not valid: st.warning('Add at least one outlet with exact coordinates first. It becomes the anchor for relative locations.')
        else:
            labels={f"{o['name']} — {o['omc']}":o for o in valid}; sel=st.selectbox('Reference outlet',list(labels)); ref=labels[sel]; refid=ref['id']
            x,y,z=st.columns(3); dist=x.number_input('Distance from reference (km)',min_value=0.01,step=0.1); relation=y.selectbox('Road relation',['Same road — same side','Same road — opposite side','Connecting road','Unknown']); direction=z.text_input('Direction / road leading towards','North')
            st.caption('For V1, enter a compass direction (N, NE, E, SE, S, SW, W, NW) to estimate the point. You can keep the commercial direction wording in Notes. Map-click/road-following placement comes next.')
            br=bearing_from_text(direction)
            if br is not None: lat,lon=destination(ref['lat'],ref['lon'],dist,br)
    notes=st.text_input('Notes / road direction / landmark')
    if st.button('Add outlet',type='primary',disabled=(method!='Exact coordinates' and not [o for o in p['outlets'] if o.get('lat') is not None])):
        if not name.strip(): st.error('Outlet name is required.')
        elif lat is None or lon is None or (method=='Exact coordinates' and lat==0 and lon==0): st.error('A usable location is required.')
        else:
            p['outlets'].append(dict(id=str(uuid.uuid4()),name=name.strip(),omc=omc,category=cat,mogas=mg,hsd=hsd,lube=lube,lat=lat,lon=lon,location_method=method,reference_id=refid,distance_km=dist,road_relation=relation,direction=direction,verified=verified,notes=(('PROPOSED | ' if kind=='Proposed outlet' else '')+notes)))
            projects[key]=p; save_projects(projects); st.success('Outlet saved.'); st.rerun()
    if p['outlets']:
        st.markdown('### Saved outlets')
        df=pd.DataFrame(p['outlets']); show=df[['name','omc','category','mogas','hsd','lube','location_method','distance_km','road_relation','direction','verified']]
        st.dataframe(show,use_container_width=True,hide_index=True)
        delname=st.selectbox('Delete outlet',['—']+[o['name'] for o in p['outlets']])
        if delname!='—' and st.button('Delete selected outlet'):
            p['outlets']=[o for o in p['outlets'] if o['name']!=delname]; projects[key]=p; save_projects(projects); st.rerun()

with T2:
    located=[o for o in p['outlets'] if o.get('lat') is not None and o.get('lon') is not None]
    if not located: st.info('Add an outlet with coordinates to initialize the map.')
    else:
        proposed=next((o for o in located if str(o.get('notes','')).startswith('PROPOSED')),located[0])
        m=folium.Map(location=[proposed['lat'],proposed['lon']],zoom_start=13,tiles='OpenStreetMap')
        for r in sorted(set([1,3,5,p['radius']])):
            folium.Circle([proposed['lat'],proposed['lon']],radius=r*1000,fill=False,weight=2,tooltip=f'{r} km radius').add_to(m)
        for o in located:
            distance=hav(proposed['lat'],proposed['lon'],o['lat'],o['lon'])
            popup=f"<b>{o['name']}</b><br>{o['omc']}<br>MOGAS: {o['mogas']} KL<br>HSD: {o['hsd']} KL<br>LUBE: {o['lube']} KL<br>Straight distance: {distance:.2f} km<br>{o.get('road_relation','')}<br>{o.get('notes','')}"
            icon='star' if o['id']==proposed['id'] else 'info-sign'
            folium.Marker([o['lat'],o['lon']],tooltip=f"{o['name']} | {distance:.2f} km",popup=popup,icon=folium.Icon(icon=icon)).add_to(m)
        st_folium(m,width=None,height=650,use_container_width=True)
        st.caption('V1 distances on the map are straight-line distances. Road-following distance and draggable placement are planned for V2.')

with T3:
    located=[o for o in p['outlets'] if o.get('lat') is not None and o.get('lon') is not None]
    if not located: st.info('No located outlets yet.')
    else:
        proposed=next((o for o in located if str(o.get('notes','')).startswith('PROPOSED')),located[0])
        rows=[]
        for o in located:
            d=hav(proposed['lat'],proposed['lon'],o['lat'],o['lon'])
            if d<=p['radius']+1e-9: rows.append({**o,'distance_km_calc':round(d,2)})
        df=pd.DataFrame(rows)
        st.markdown(f"### Outlets within {p['radius']} km")
        st.dataframe(df[['name','omc','category','mogas','hsd','lube','distance_km_calc','road_relation']],use_container_width=True,hide_index=True)
        summary=df.groupby('omc',as_index=False).agg(Sites=('id','count'),MOGAS_KL=('mogas','sum'),HSD_KL=('hsd','sum'),LUBE_KL=('lube','sum'))
        for col in ['MOGAS_KL','HSD_KL','LUBE_KL']:
            total=summary[col].sum(); summary[col.replace('_KL','_Share_%')]=(summary[col]/total*100).round(1) if total else 0
        st.markdown('### OMC market summary'); st.dataframe(summary,use_container_width=True,hide_index=True)
        st.download_button('Download trading-area CSV',df.to_csv(index=False).encode(),file_name=f"{p['name'].replace(' ','_')}_outlets.csv",mime='text/csv')
