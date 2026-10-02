# Trading Area Mapper V1

## Deploy on Streamlit Community Cloud
1. Create a GitHub repository.
2. Upload `app.py`, `requirements.txt`, and the empty `data` folder (or add `data/.gitkeep`).
3. In Streamlit Community Cloud choose the repository and `app.py`.

## V1 features
- 3/5/10 km trading radius
- Exact coordinate anchor
- Relative outlet placement from a known outlet
- Same road/same side, same road/opposite side, connecting road
- MOGAS/HSD/LUBE and OMC/category fields
- Interactive OpenStreetMap
- Straight-line distances
- OMC sales/market-share summary
- JSON project persistence while the deployment filesystem persists

## Important
Streamlit Community Cloud local files are not durable storage across all redeploys/reboots. V2 should move projects/outlet master to Google Sheets, Supabase, or another persistent database.
