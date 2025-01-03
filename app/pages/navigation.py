import streamlit as st
import folium
import pandas as pd
from streamlit_folium import st_folium
import requests
from dotenv import load_dotenv
import os

def navigation_page():
    query_params = st.query_params
    id = int(query_params.get("id"))
    def get_location():
        token = "your_token"
        url = f"https://ipinfo.io/json?token={token}"
        response = requests.get(url)
        data = response.json()
        latitude, longitude = data['loc'].split(',')
        return latitude, longitude

    latitude, longitude = get_location()
    
    if id == 0:
        st.error("No hotel location found. Navigate from main page")
        return
    
    if "df" not in st.session_state:
        st.session_state.df = pd.read_csv(r'C:\Users\Admin\Desktop\final_project\app\full_data.csv')
    
    if "data" not in st.session_state:
        st.session_state.data = st.session_state.df[st.session_state.df['id'] == id]

    lat = float(st.session_state.data['latitude'].iloc[0])
    lon = float(st.session_state.data['longitude'].iloc[0])

    st.title("Navigation Page")

    st.info("📍 Drag the blue marker to set your current location")

    if 'route_info' not in st.session_state:
        st.session_state.route_info = None

    m = folium.Map(location=[lat, lon], zoom_start=15)

    folium.Marker([lat, lon], tooltip="Hotel Location", icon=folium.Icon(color="red")).add_to(m)

    user_marker = folium.Marker(
        location=[latitude, longitude], 
        tooltip="Drag me to your location",
        draggable=True,
        icon=folium.Icon(color="blue"),
    )
    m.add_child(user_marker)

    map_output = st_folium(m, width=700, height=500)


    # user_lat = map_output["last_clicked"]["lat"]
    # user_lon = map_output["last_clicked"]["lng"]
    
    if map_output.get("last_object_clicked_tooltip") == "Drag me to your location":
        if map_output.get("last_object_clicked"):
            user_lat = map_output["last_object_clicked"]["lat"]
            user_lon = map_output["last_object_clicked"]["lng"]
    else:
        user_lat = latitude
        user_lon = longitude

    get_route_button = st.button("Get Route")

    if get_route_button:
        if user_lat is not None and user_lon is not None:
            try:
                load_dotenv()
                key = os.getenv("API_KEY_1")
                base_url = "https://api.openrouteservice.org/v2/directions/driving-car"
                params = {
                    "api_key": key,
                    "start": f"{lon},{lat}", 
                    "end": f"{user_lon},{user_lat}",
                }
                
                response = requests.get(base_url, params=params)

                if response.status_code == 200:
                    data = response.json()
                    route_geometry = data["features"][0]["geometry"]["coordinates"]
                    route_distance = data["features"][0]["properties"]["segments"][0]["distance"]
                    route_duration = data["features"][0]["properties"]["segments"][0]["duration"]

                    # Store route information in session state
                    st.session_state.route_info = {
                        'route_geometry': route_geometry,
                        'route_distance': route_distance,
                        'route_duration': route_duration,
                        'user_lat': user_lat,
                        'user_lon': user_lon
                    }
                else:
                    st.error("Failed to fetch route. Check your API key or internet connection or don't keep the marker far away")
            
            except Exception as e:
                st.error(f"An error occurred: {e}")
        else:
            st.error("Please drag the blue marker to your location or click on the map to set your location.")

    if st.session_state.route_info:
        route_info = st.session_state.route_info
        
        route_map = folium.Map(location=[lat, lon], zoom_start=15)

        folium.Marker([lat, lon], tooltip="Hotel Location", icon=folium.Icon(color="red")).add_to(route_map)

        folium.Marker(
            [route_info['user_lat'], route_info['user_lon']], 
            tooltip="Your Location", 
            icon=folium.Icon(color="blue")
        ).add_to(route_map)

        folium.PolyLine(
            locations=[[route_point[1], route_point[0]] for route_point in route_info['route_geometry']],
            color="blue",
            weight=5,
            opacity=0.7,
        ).add_to(route_map)

        st_folium(route_map, width=700, height=500)
        url = st.session_state.data["url"].iloc[0].split('?')[0]
        st.write(f"Route Distance: {route_info['route_distance'] / 1000:.2f} km")
        st.write(f"Expected Route Duration: {route_info['route_duration'] / 60:.2f} minutes")
        if (route_info['route_distance'] / 1000) < 20:
            table_booking= f'<a href="{url}" target="_blank" style="padding: 10px 20px; font-size: 16px; color: #fff; background-color: #007bff; border-radius: 5px; text-decoration: none;">Order</a>'
        else:
            table_booking='<span style="padding: 10px 20px; font-size: 16px; color: #fff; background-color: #ddd; border-radius: 5px; text-decoration: none;">Order not avaliable</span>'
        st.markdown(f"""
        <div style="display: flex; justify-content: center; gap: 10px; margin-top: 20px;">
                                    {table_booking}
                                    </div>""", unsafe_allow_html=True)

navigation_page()
