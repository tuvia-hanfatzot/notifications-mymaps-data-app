import pandas as pd
import streamlit as st
from io import BytesIO

st.title("Upload Excel File and Process Coordinates for My Maps")

# File uploader for Excel file
uploaded_file = st.file_uploader("Choose an Excel file", type=["xlsx"])

if uploaded_file is not None:
    # Read the uploaded file into a DataFrame
    df = pd.read_excel(uploaded_file)

    # Find lat and log columns
    lat_columns = [col for col in df.columns if col.lower().startswith('lat')]
    log_columns = [col for col in df.columns if col.lower().startswith('log')]
    point_columns = [col for col in df.columns if col.lower().startswith('point')]

    # Remove "Start Time" and "End Time" columns
    time_columns = ['Start Time', 'End Time']

    if len(lat_columns) != len(log_columns):
        st.error("Mismatched lat and log columns. Please check the file.")
    else:
        # Create a new DataFrame for My Maps format
        new_rows = []
        for index, row in df.iterrows():
            for lat_col, log_col in zip(lat_columns, log_columns):
                lat = row[lat_col]
                log = row[log_col]
                if pd.notnull(lat) and pd.notnull(log):
                    # Add a row with the coordinate and other info
                    new_row = row.to_dict()  # Copy other columns
                    new_row['Latitude'] = lat
                    new_row['Longitude'] = log
                    new_rows.append(new_row)

        # Create a new DataFrame with the expanded rows
        my_maps_df = pd.DataFrame(new_rows)

        # Drop "Point", "lat", "log", "Start Time", and "End Time" columns
        columns_to_remove = point_columns + lat_columns + log_columns + time_columns
        my_maps_df = my_maps_df.drop(columns=columns_to_remove, errors='ignore')

        # Display a preview of the table on the website
        st.write("Preview of Processed Data:")
        st.dataframe(my_maps_df.head(10))  # Show the first 10 rows as a preview

        # Save the new DataFrame to an Excel file
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            my_maps_df.to_excel(writer, index=False, sheet_name='My Maps Data')
        processed_file = output.getvalue()

        # Add a download button for the new file
        st.download_button(
            label="Download My Maps-Compatible File",
            data=processed_file,
            file_name="my_maps_data.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
