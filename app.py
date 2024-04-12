import dash
import dash_bootstrap_components as dbc
from dash import dcc, html, Input, Output
import dash_leaflet as dl
import pandas as pd


# Read in the CSV files into a pandas DataFrame
df = pd.read_csv("db.csv")
minerals_df = pd.read_csv("minerals.csv")


# Use a Bootswatch theme
app = dash.Dash(
    __name__,
    external_stylesheets=[
        dbc.themes.LUX,
        "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/leaflet.css",
    ],
    suppress_callback_exceptions=True,
)

server = app.server

# Navbar with logo and always-visible hamburger menu
navbar = dbc.Navbar(
    dbc.Container(
        [
            dbc.Row(
                [
                    dbc.Col(
                        html.Img(
                            src=app.get_asset_url("mars-logo.png"), height="100rem"
                        )
                    ),
                    dbc.Col(
                        dbc.NavbarBrand("TerraMars AI Explorer", className="ml-2")
                    ),
                ],
                align="center",
                className="g-0",
            ),
            dbc.Row(
                dbc.Col(
                    dbc.DropdownMenu(
                        children=[
                            dbc.DropdownMenuItem("Home", href="/"),
                            dbc.DropdownMenuItem("Map", href="/mars-map"),
                            # Add more DropdownMenuItem's if needed
                        ],
                        nav=True,
                        in_navbar=True,
                        label="Menu",  # This is the label for the hamburger menu
                    ),
                    width="auto",
                    align="center",
                ),
                className="ml-auto flex-nowrap mt-3 mt-md-0",
                align="center",
            ),
        ]
    ),
    color="primary",
    dark=True,
    className="mb-4",
    sticky="top",
)


# Dropdown within a card component

dropdown_card = dbc.Card(
    [
        dbc.CardHeader("Choose a Mineral"),
        dbc.CardBody(
            [
                dcc.Dropdown(
                    id="mineral-dropdown",
                    options=[
                        {"label": mineral, "value": mineral}
                        for mineral in df.columns[5:]
                    ],  # Adjusted to skip 'Region'
                    value=df.columns[2],
                ),
                html.Div(
                    id="mineral-description", style={"marginTop": "20px"}
                ),  # Placeholder for mineral description
            ]
        ),
    ],
    style={"margin": "20px"},
)


# Image container layout
image_container = html.Div(id="image-container", style={"margin": "20px"})

# Add dcc.Location and a method to switch between pages
app.layout = dbc.Container(
    [
        dcc.Location(id="url", refresh=False),  # This tracks the URL
        navbar,  # This is your existing navbar
        html.Div(id="page-content"),  # Placeholder for dynamic page content
    ],
    fluid=True,
)


# Callback to update minerals & images
@app.callback(
    [Output("mineral-description", "children"), Output("image-container", "children")],
    [Input("mineral-dropdown", "value")],
)
def update_content_and_images(selected_mineral):
    # Default values
    description = "Description not available."
    no_images_alert = dbc.Alert("No images found for this mineral.", color="warning")

    # Fetching the description
    description_row = minerals_df[minerals_df["Mineral"] == selected_mineral]
    if not description_row.empty:
        description_text = description_row["Description"].iloc[0]
        # Append the hyperlink to the description
        description = html.Div(
            [
                description_text,
                " ",
                html.A(
                    "[↗]",
                    href="https://en.wikipedia.org/wiki/Mineralogy_of_Mars",
                    target="_blank",
                ),
            ]
        )
    else:
        description = html.Div(
            [
                "Description not available.",
                " ",
                html.A(
                    "[↗]",
                    href="https://en.wikipedia.org/wiki/Mineralogy_of_Mars",
                    target="_blank",
                ),
            ]
        )

    # Updating the image list
    filtered_df = df[df[selected_mineral] == 1]
    if not filtered_df.empty:
        # Use dbc.Row and dbc.Col to create a responsive grid
        row = dbc.Row(
            [
                dbc.Col(
                    dbc.Card(
                        [
                            dbc.CardHeader(
                                f"ID: {row['ImageID']} - Description: {row['Region']}"
                            ),
                            # Use object-fit 'contain' to ensure images are resized, not cropped
                            dbc.CardImg(
                                src=app.get_asset_url(f'images/{row["ImageFilename"]}'),
                                top=True,
                                style={
                                    "height": "200px",
                                    "object-fit": "contain",
                                    "width": "100%",
                                },
                            ),
                            dbc.CardBody(
                                [
                                    html.P(
                                        f"Mineral: {selected_mineral}",
                                        className="card-text",
                                    )
                                ]
                            ),
                        ],
                        className="mb-3 h-100",  # Use 'h-100' to make cards of equal height
                    ),
                    md=4,  # With 'md=4', you get 3 images per row on medium to large screens
                )
                for _, row in filtered_df.iterrows()
            ],
            className="mb-4",
        )
        return description, row  # Return the description and the row of image cards
    else:
        return description, no_images_alert  # Return the description and the alert


# _____________________


# Define layout for the Mars map page
mars_map_layout = html.Div(
    [
        dbc.Card(
            dbc.CardBody(
                [
                    dcc.Dropdown(
                        id="mineral-map-dropdown",
                        options=[
                            {"label": mineral, "value": mineral}
                            for mineral in df.columns[5:]
                        ],
                        value=df.columns[5],  # Default value, adjust as needed
                    ),
                    # Define the map component with an open Mars tile layer
                    dl.Map(
                        [
                            # Specify the OpenPlanetaryMap Mars basemap tile layer URL
                            dl.TileLayer(
                                url="https://cartocdn-gusc.global.ssl.fastly.net/opmbuilder/api/v1/map/named/opm-mars-basemap-v0-1/all/{z}/{x}/{y}.png",
                                maxZoom=10,
                                noWrap=True,
                                attribution="&copy; OpenPlanetaryMap",
                            ),
                            dl.LayerGroup(id="map-layer"),
                        ],
                        id="mars-map",
                        style={
                            "width": "100%",
                            "height": "70vh",
                            "margin": "auto",
                            "display": "block",
                        },
                        center=(
                            0,
                            0,
                        ),  # Mars map center coordinates, adjust as necessary
                        # maxBounds=[
                        #     [-90, -100],
                        #     [90, 100],
                        # ],  # Set max bounds (southwest to northeast) based on map projection
                        worldCopyJump=False,
                        zoom=4,  # Initial zoom level, adjust as necessary
                    ),
                ]
            )
        )
    ]
)


# Callback to update page content based on URL
@app.callback(Output("page-content", "children"), [Input("url", "pathname")])
def display_page(pathname):
    if pathname == "/mars-map":
        return mars_map_layout
    else:
        return [dropdown_card, image_container]  # Your home page content


# Callback to update the Mars map with mineral locations
@app.callback(Output("map-layer", "children"), [Input("mineral-map-dropdown", "value")])
def update_map(selected_mineral):
    # Filter DataFrame based on selected mineral
    filtered_df = df[df[selected_mineral] == 1]

    markers = [
        dl.Marker(
            position=[row["Latitude"], row["Longtitude"]],
            children=[
                dl.Popup(
                    children=[
                        html.Img(
                            src=app.get_asset_url(f'images/{row["ImageFilename"]}'),
                            style={"width": "auto", "height": "25rem"},
                        ),  #'max-height': '100%', 'cursor': 'zoom-in'
                    ],
                    maxWidth=200,
                    closeButton=False,
                )
            ],
            riseOnHover=True,  # Popup will appear above other markers when hovered
        )
        for _, row in filtered_df.iterrows()
    ]
    return markers


# ________________________________________


if __name__ == "__main__":
    app.run_server(debug=True)
