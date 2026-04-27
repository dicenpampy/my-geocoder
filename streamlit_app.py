import streamlit as st
import pandas as pd
import requests
import time

# 1. Setup API (Get your free key at geoapify.com)
API_KEY = "1bcf9dab19834e40bc03f706b0f87f8d"

st.title("Pam's Geocoder")
uploaded_file = st.file_uploader("Upload Excel file", type=["xlsx"])

if uploaded_file:
    try:
        df = pd.read_excel(uploaded_file, engine="openpyxl")
    except ImportError:
        st.error("Missing dependency: install openpyxl to read Excel files. Run `pip install openpyxl`.")
        st.stop()
    except Exception as e:
        st.error(f"Unable to read the uploaded Excel file: {e}")
        st.stop()

    address_column = st.selectbox("Select the Address column", df.columns)
    
    if st.button("Start Geocoding"):
        results = []
        progress_bar = st.progress(0)
        total = len(df)

        for i, addr in enumerate(df[address_column]):
            try:
                # API Call to Geoapify
                url = f"https://api.geoapify.com/v1/geocode/search?text={addr}&apiKey={API_KEY}"
                response = requests.get(url).json()
                
                if response['features']:
                    lon = response['features'][0]['geometry']['coordinates'][0]
                    lat = response['features'][0]['geometry']['coordinates'][1]
                else:
                    lat, lon = None, None
            except:
                lat, lon = "Error", "Error"

            results.append({"lat": lat, "lon": lon})
            progress_bar.progress((i + 1) / total)
            
            # Respect rate limits (Geoapify free is 5 requests/sec)
            time.sleep(0.2) 

        # Add results to original dataframe
        res_df = pd.DataFrame(results)
        df['Latitude'] = res_df['lat']
        df['Longitude'] = res_df['lon']

        st.success("Finished!")
        st.dataframe(df.head())
        
        # Download Button
        st.download_button(
            label="Download Geocoded Excel",
            data=df.to_csv(index=False).encode('utf-8'),
            file_name="geocoded_properties.csv",
            mime="text/csv"
        )