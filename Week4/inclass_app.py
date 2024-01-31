import streamlit as st
import datetime 
import pytz
import time
from zoneinfo import ZoneInfo

def get_time_from_timezone():# List of time zones or cities you want to display
    time_zones = ['UTC', 'America/New_York', 'Asia/Tokyo', 'Australia/Sydney', 'Europe/London']
    times = {}
    for zone in time_zones:
            tz = pytz.timezone(zone)
            time_now = datetime.datetime.now(tz)
            st.write(f"Time in {zone}: {time_now.strftime('%Y-%m-%d %H:%M:%S')}")
    return times

st.title('World Clock')


times = get_time_from_timezone() 

for zone, time in times.items():
    st.write(f"Time in {zone}: {time}")

# JavaScript to trigger page refresh
refresh_time = 1000  # Refresh every 1000 milliseconds (1 second)
st.markdown(
    f"""
    <script>
    setTimeout(function() {{
        window.location.reload();
    }}, {refresh_time});
    </script>
    """,
    unsafe_allow_html=True
)