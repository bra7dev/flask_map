# -*- coding: utf-8 -*-
"""
Created on Tue Mar 28 15:35:13 2023

@author: cogan
"""

import os
import pandas as pd
from flask import Flask, render_template, request, send_file
import folium
from werkzeug.utils import secure_filename
import folium.plugins as plugins

# SET WORKING DIRECTORY
# os.chdir(r'C:\Users\cogan\Desktop\HCmap')
# cwd = os.getcwd()

# Set up the Flask app and configuration
application = Flask(__name__)
application.config["UPLOAD_FOLDER"] = "uploads/"
application.config["ALLOWED_EXTENSIONS"] = {"csv"}


# Create helper functions for the map and allowed file types
def allowed_file(filename):
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower()
        in application.config["ALLOWED_EXTENSIONS"]
    )


def create_map(df):
    # Initialize the map
    m = folium.Map(
        location=[df["Latitude"].mean(), df["Longitude"].mean()], zoom_start=10
    )

    # Define the color scheme
    # colormap = folium.LinearColormap(['purple', 'yellow', 'red'], vmin=df['MW Available'].min(), vmax=df['MW Available'].max())
    colormap = folium.LinearColormap(
        ["White", "Purple"],
        vmin=df["MW Available"].min(),
        vmax=df["MW Available"].max(),
    )

    # Add markers to the map
    locations = []
    feature_group = folium.FeatureGroup(name="Substations")
    for index, row in df.iterrows():
        popup_text = f"Substation Name: {row['Substation Name']}<br>MW Available: {row['MW Available']}<br>Constraint: {row['Constraint']}"
        marker = folium.CircleMarker(
            location=[row["Latitude"], row["Longitude"]],
            radius=8,
            popup=folium.Popup(popup_text, max_width=300),
            color=colormap(row["MW Available"]),
            fill=True,
            fill_color=colormap(row["MW Available"]),
            fill_opacity=1,
        )
        marker.add_child(folium.Tooltip(row["Substation Name"]))
        locations.append([row["Latitude"], row["Longitude"]])
        feature_group.add_child(marker)

    # Fit map to bounds
    m.fit_bounds(locations)

    # Add the color legend
    colormap.caption = "MW Available"
    colormap.add_to(m)

    # Add the search functionality
    # search = plugins.Search(
    #     layer=feature_group, search_label="tooltip", geom_type="Point"
    # ).add_to(m)

    # Add the feature group to the map
    m.add_child(feature_group)
    search_css = """
    <style>
        .leaflet-top {
            right: 0 !important;
            left: initial !important;
        }
        .leaflet-top .leaflet-control-search {
        
            display: none;
            position: absolute !important;
            right: 54px !important;
            top: 40px !important;
        }
        .leaflet-top .leaflet-control-zoom {
            display: none;
            position: absolute !important;
            top: 40px !important;
            right: 10px !important;
            float: none !important;
            flex-direction: column;
        }
        .leaflet-control-search .search-exp .leaflet-control {
            position: absolute !important;
            top: 12px !important;
            right: 10px !important;
            float: none !important;
            display: flex !important;
        }
        .leaflet-control-zoom .leaflet-bar .leaflet-control {
            position: absolute !important;
            right: 10px !important;
            top: 103px !important;
        }
    </style>
    """
    m.get_root().html.add_child(folium.Element(search_css))

    return m


# create initial map
df = pd.read_csv(r"FCITCresults.csv", header=0)
df = df.dropna(subset=["Latitude", "Longitude"])
# Initialize map centered at the first data point
m = create_map(df)
# Save map to an HTML file
m.save("templates/maps/dendrite_map_base.html")

# create initial retirement map
df = pd.read_csv(r"FCITCresults_retired.csv", header=0)
df = df.dropna(subset=["Latitude", "Longitude"])
# Initialize map centered at the first data point
m = create_map(df)
# Save map to an HTML file
m.save("templates/maps/dendrite_map_retirements.html")

def create_map_STP(df_tra, df_sta, df_pow):
    # Initialize the map
    m = folium.Map((0, 0), zoom_start=10)

    # Drawing substation.
    # Define the color scheme
    colormap = folium.LinearColormap(
        ["White", "Purple"],
        vmin=df_sta["MW Available"].min(),
        vmax=df_sta["MW Available"].max(),
    )

    # Add markers to the map
    locations = []
    sta_group = folium.FeatureGroup(name="Substations")
    for index, row in df_sta.iterrows():
        popup_text = f"Substation Name: {row['Substation Name']}<br>MW Available: {row['MW Available']}<br>Constraint: {row['Constraint']}"
        marker = folium.Marker(
            location=[row["Latitude"], row["Longitude"]],
            icon=folium.DivIcon(
                html=f"""
                <div style="display: flex; align-items: center; justify-content: center; text-align: center; font-weight: bold; color: black; background-color: {colormap(row['MW Available'])};border-radius: 50%;  width: 16px; height: 16px;" ></div>
            """
            ),
            popup=folium.Popup(popup_text, max_width=300),
            color=colormap(row["MW Available"]),
            fill=True,
            fill_color=colormap(row["MW Available"]),
            fill_opacity=1,
            prefer_canvas=True,
        )
        marker.add_child(folium.Tooltip(row["Substation Name"]))
        locations.append([row["Latitude"], row["Longitude"]])
        sta_group.add_child(marker)

    m.fit_bounds(locations)
    search = plugins.Search(
        layer=sta_group, search_label="tooltip", geom_type="Point"
    ).add_to(m)
    m.add_child(sta_group)

    # Add the color legend
    colormap.caption = "MW Available"
    colormap.add_to(m)
    search_css = """
    <style>
        .leaflet-top {
            right: 0 !important;
            left: initial !important;
        }
        .leaflet-top .leaflet-control-search {
            display: flex;
            position: absolute !important;
            right: 72px !important;
            top: 51px !important;
        }
        .leaflet-top .leaflet-control-zoom {
            position: absolute !important;
            top: 110px !important;
            right: 10px !important;
            float: none !important;
            display: flex !important;
            flex-direction: column;
        }
        .leaflet-control-search .search-exp .leaflet-control {
            position: absolute !important;
            top: 12px !important;
            right: 10px !important;
            float: none !important;
            display: flex !important;
        }
        .leaflet-control-zoom .leaflet-bar .leaflet-control {
            position: absolute !important;
            right: 10px !important;
            top: 103px !important;
        }
    </style>
    """
    m.get_root().html.add_child(folium.Element(search_css))
    # Add the feature group to the map

    popup_html = ""
    # Define the HTML template for the marker icon
    marker_html = """
    <div id="marker" class="marker" style="display: flex; align-items: center; justify-content: center; text-align: center; font-weight: bold; color: white; background-color: green; border: 2px solid blue; width: 16px; height: 16px;" onclick="toggleMarkerColor(event)"></div>
    """
    # Define the JavaScript code for handling marker click events
    marker_js = """
    <script>
    var global_marker = ""
    var markers = document.getElementsByClassName("marker");
    console.log("start...", markers)
    function toggleMarkerColor(e) {
        var marker = e.target;
        global_marker = marker
        console.log("clicked!", e)
        if (marker.style.backgroundColor === "green") {
            marker.style.backgroundColor = "gray";
        } else {
            marker.style.backgroundColor = "green";
        }
    }

    function changeMarkerColor(e) {
        var selectTag = e.target;
        console.log("e-target", e)
        var marker = selectTag.parentNode;
        var color = selectTag.value;
        global_marker.style.backgroundColor = color;
    }
    </script>
    """

    # power station Icon
    pow_group = folium.FeatureGroup(name="Generator")
    for index, row in df_pow.iterrows():
        popup_html = f"""<h4>Generator Info</h4>
                        <table>
                            <tr>
                                <th>Name</th>
                                <th>Content</th>
                            </tr>
                            <tr>
                                <td>Generator Name</td>
                                <td>{row['Name of Bus']}</td>
                            </tr>
                            <tr>
                                <td>ID</td>
                                <td>{row['ID']}</td>
                            </tr>
                            <tr>
                                <td>Max MW</td>
                                <td>{row['Max MW']}</td>
                            </tr>
                            <tr>
                                <td>Gen MW</td>
                                <td>{row['Gen MW']}</td>
                            </tr>
                            <tr>
                                <td>Status</td>
                                <td>
                                <select id="colorSelect" onchange="changeMarkerColor(event)">
                                    <option value="gray">Off</option>
                                    <option value="green">On</option>
                                </select>
                                </td>
                            </tr>
                        </table> """

        marker = folium.Marker(
            location=[row["Latitude of Bus"], row["Longitude of Bus"]],
            icon=folium.DivIcon(html=marker_html),
            popup=folium.Popup(popup_html, max_width=300),
            prefer_canvas=True,
        )

        marker.add_child(folium.Tooltip(row["Name of Bus"]))
        locations.append([row["Latitude of Bus"], row["Longitude of Bus"]])
        pow_group.add_child(marker)

    # Fit map to bounds
    m.fit_bounds(locations)
    m.add_child(pow_group)
    m.get_root().html.add_child(folium.Element(marker_js))
    # def style_function(feature):
    #     voltage = feature['properties']['voltage']
    #     thickness = 1 + (voltage - 110) / 110  # Adjust the scaling factor as per your requirement
    #     return {
    #         'color': 'blue',
    #         'weight': thickness
    #     }

    # # Create a GeoJson layer with the data and style
    # folium.GeoJson(
    #     geojson_data,
    #     style_function=style_function
    # ).add_to(m)
    # Drawing transmission
    folium.GeoJson(
        df_tra, name="Transmission", style_function=lambda feature: {"color": "orange"}
    ).add_to(m)
    folium.LayerControl().add_to(m)

    return m


df = pd.read_csv(r"FCITCresults.csv", header=0)
df_sta = df.dropna(subset=["Latitude", "Longitude"])
df = pd.read_csv(r"Generators.csv", header=0)
df_pow = df.dropna(subset=["Latitude of Bus", "Longitude of Bus"])
df_tra = "https://webapp-public-resources.s3.us-west-1.amazonaws.com/Electric__Power_Transmission_Lines.geojson"

m = create_map_STP(df_tra, df_sta, df_pow)


m.save("templates/maps/test20.html")


# Create the main route for your Flask app
@application.route("/", methods=["GET", "POST"])
def index():
    map_filenames = []
    for file in os.listdir("templates/maps"):
        if file.endswith(".html"):
            map_filenames.append(file)
    map_filenames.sort(reverse=True)
    selected_map = request.args.get(
        "map", map_filenames[0]
    )  # Add this line to set the default selected_map
    return render_template(
        "index.html", map_filenames=map_filenames, selected_map=selected_map
    )  # Add selected_map=selected_map here


@application.route("/upload", methods=["POST"])
def upload():
    if request.method == "POST":
        csv_file = request.files.get("csv_file")
        if csv_file and allowed_file(csv_file.filename):
            filename = secure_filename(csv_file.filename)
            csv_file.save(os.path.join(application.config["UPLOAD_FOLDER"], filename))
            df = pd.read_csv(os.path.join(application.config["UPLOAD_FOLDER"], filename))
            m = create_map(df)
            map_filename_base = os.path.splitext(filename)[0]
            new_map_filename = f"{map_filename_base}_map.html"
            m.save(os.path.join("templates", "maps", new_map_filename))
            return "File uploaded and map created."
    return "Failed to upload file."


# Add routes for downloading and uploading CSV files
@application.route("/download")
def download():
    df.to_csv("data.csv", index=False)
    return send_file("data.csv", as_attachment=True, attachment_filename="data.csv")


@application.route("/download_generator_list")
def download_generator_list():
    generator_list = "generator_list.csv"  # Replace this with the path to your generator list CSV file
    return send_file(generator_list, as_attachment=True)


# @app.route('/map/<filename>')
# def map(filename):
#     return render_template(f'maps/{filename}')


@application.route("/map/<filename>")
def map(filename):
    map_filenames = []
    for file in os.listdir("templates/maps"):
        if file.endswith(".html"):
            map_filenames.append(file)
    map_filenames.sort(reverse=True)
    return render_template(
        "index.html", map_filenames=map_filenames, selected_map=filename
    )


if __name__ == "__main__":
    application.run(port=8000)
