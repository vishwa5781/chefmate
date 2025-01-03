import streamlit as st
import base64
import pandas as pd
from sqlalchemy import create_engine
import pandas as pd
import requests
import os
from dotenv import load_dotenv


def get_location():
    load_dotenv()
    token = os.getenv("token")
    url = f"https://ipinfo.io/json?token={token}"
    response = requests.get(url)
    data = response.json()
    city = data['city']
    return city

city = get_location()

def image_to_base64(image_path):
    try:
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode()
    except FileNotFoundError:
        st.error(f"File not found: {image_path}")
        return None

left_image = "logo/left.png"
right_image = "logo/right.jpg"
left_img_base64 = image_to_base64(left_image)
right_img_base64 = image_to_base64(right_image)

if left_img_base64 and right_img_base64:
    header_html = f"""
    <div style="display: flex; align-items: center; justify-content: space-between; 
                background-color: white; padding: 10px; border-radius: 5px; box-shadow: 0 4px 8px rgba(0,0,0,0.1);">
        <img src="data:image/png;base64,{left_img_base64}" alt="Left Image" style="height: 100px;">
        <h1 style="font-size: 50px; font-weight: bold; color:#FF0000; margin: 0;">ZOMATO</h1>
        <img src="data:image/jpeg;base64,{right_img_base64}" alt="Right Image" style="height: 100px;">
    </div>
    """
    st.markdown(header_html, unsafe_allow_html=True)



def get_database_connection():
    engine = create_engine('yourengine')
    return engine

def fetch_data_from_db():
    engine = get_database_connection()
    query = "SELECT * FROM zomato;"
    df = pd.read_sql(query, engine)
    return df

def main_page():
    if 'show_chatbot' not in st.session_state:
        st.session_state.show_chatbot = False

    if "data" not in st.session_state:
        st.session_state.data = fetch_data_from_db()
    st.session_state.data.to_csv('full_data.csv',index=False)

    col1, col2, col3 = st.columns([2, 2, 1])

    with col1:
        with open('models/unique_cuisines.txt', 'r') as file:
            items = [line.strip() for line in file.readlines()]
        selected_item = st.selectbox("Select Cuisine", options=['Please select'] + items, index=0)
        st.session_state.selected_item = selected_item  

    with col2:
        with open('models/unique_cities.txt', 'r') as file:
            locs = [line.strip() for line in file.readlines()]
        if city in locs:
            locs.remove(city) 
            locs.insert(0, city)  
        else:
            locs.insert(0, city)
        location = st.selectbox("Select Location", options= locs, index=0)
        st.session_state.location = location  

    if st.session_state.selected_item =='Please select' and st.session_state.location:
        filtered_data = st.session_state.data[st.session_state.data['city'] == st.session_state.location]
    elif st.session_state.selected_item !='Please select' and st.session_state.location:
        filtered_data_1 = st.session_state.data[st.session_state.data['cuisines'].str.contains(st.session_state.selected_item, case=False, na=False)]
        filtered_data = filtered_data_1[filtered_data_1['city'] == st.session_state.location]
        
    if not filtered_data.empty:
            for _, row in filtered_data.iterrows():
                with st.container():
                    aggregate_rating = float(row['aggregate_rating'])
                    if row['has_table_booking'] =='Yes':
                       table_booking= f'<a href="{row["url"]}" target="_blank" style="padding: 10px 20px; font-size: 16px; color: #fff; background-color: #007bff; border-radius: 5px; text-decoration: none;">Table Booking</a>'
                    else:
                        table_booking='<span style="padding: 10px 20px; font-size: 16px; color: #fff; background-color: #ddd; border-radius: 5px; text-decoration: none;">Table booking not avaliable</span>'

                    if row['has_online_delivery'] == 'Yes':
                        navigate_button = f'<a href="navigation?id={row["id"]}" target="_self" style="padding: 10px 20px; font-size: 16px; color: #fff; background-color: #007bff; border-radius: 5px; text-decoration: none;">order</a>'
                    else:
                        navigate_button = '<span style="padding: 10px 20px; font-size: 16px; color: #fff; background-color: #ddd; border-radius: 5px; text-decoration: none;">Navigate (not deliviring now)</span>'
                    st.markdown(
                        f"""
                        <div style="background-color: #FFFFFF; padding: 20px; margin-bottom: 20px; border-radius: 10px; border: 2px solid #ddd; box-shadow: 0 12px 12px rgba(0,0,0,0.1); width: 800px;max-height:600px;height: 50%; margin-left: auto; margin-right: auto;">
                        <p style="font-size: 24px; font-weight: bold; color: #333; text-align: center; margin-bottom: 20px;">{row['name']}</p>
                        <p> <strong>Cuisines available:</strong> {row['cuisines']}</p>
                        <p> <strong>Average_cost_for_two:</strong>{row['average_cost_for_two']} {row['currency']}</p>
                        <p><strong>Table Booking: {row['has_table_booking']}</p> 
                        <p><strong>Online Delivery: {row['has_online_delivery']}</p>
                        <p><strong>Delivery Now: {row['is_delivering_now']}</p>
                        <p><strong>Address:</strong> {row['address']} </p>
                        <p><strong>Price Range:</strong> {row['price_range']}</p>
                        <p><strong>Location:</strong> Latitude: {row['latitude']}, Longitude: {row['longitude']}</p>
                        <p><strong>Rating:</strong></p>
                        <div style="display: inline-block; background-color: #{row['rating_color']}; padding: 10px 20px; border-radius: 25px; font-size: 24px; color: white;">
                            <span style="font-size: 20px;">
                                {"★" * int(aggregate_rating)} <!-- Full stars -->
                                {"☆" * (5 - int(aggregate_rating))} <!-- Empty stars -->
                            </span>
                            <span style="font-size: 18px; margin-left: 10px;">({aggregate_rating}/5 based on {row['rating_votes']} votes)</span>
                        </div>
                        <div style="display: flex; justify-content: center; gap: 10px; margin-top: 20px;">
                                    {table_booking}                          
                                    {navigate_button}
                                    </div>
                    </div>""", unsafe_allow_html=True)
                    st.markdown("<br>", unsafe_allow_html=True)
    else:
            st.write("No data found for the selected filters.")

st.markdown('<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css">', unsafe_allow_html=True)

st.markdown(""" 
    <style>
        .chatbot-button {
            position: fixed;
            bottom: 20px;
            right: 20px;
            background-color: #0099FF;
            color: white;
            width: 60px;
            height: 60px;
            border-radius: 50%;
            display: flex;
            justify-content: center;
            align-items: center;
            font-size: 24px;
            border: none;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            z-index: 1000;
            cursor: pointer;
        }
    </style>
""", unsafe_allow_html=True)

def display_chatbot_button():
    st.markdown("""
        <a href="/chatbot" target="_self">
            <div class="chatbot-button">
                <i class="fas fa-comments"></i>
            </div>
        </a>
    """, unsafe_allow_html=True)

def main():
    main_page()
    display_chatbot_button() 

if __name__ == "__main__":
    main()
