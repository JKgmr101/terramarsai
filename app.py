import dash
import dash_bootstrap_components as dbc
from dash import dcc, html
from dash.dependencies import Input, Output
import pandas as pd

# Read in the CSV file into a pandas DataFrame
df = pd.read_csv("db.csv")

# Use a Bootswatch theme
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.LUX])

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
                        dbc.NavbarBrand("Mars Mineral Image Finder", className="ml-2")
                    ),
                ],
                align="center",
                className="g-0",
            ),
            dbc.Row(
                dbc.Col(
                    dbc.DropdownMenu(
                        children=[
                            dbc.DropdownMenuItem("Home", href="#"),
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
            dcc.Dropdown(
                id="mineral-dropdown",
                options=[
                    {"label": mineral, "value": mineral} for mineral in df.columns[3:]
                ],  # Adjusted to skip 'Region'
                value=df.columns[3],
            )
        ),
    ],
    style={"margin": "20px"},
)

# Image container layout
image_container = html.Div(id="image-container", style={"margin": "20px"})

app.layout = dbc.Container([navbar, dropdown_card, image_container], fluid=True)


# Callback to update images
@app.callback(
    Output("image-container", "children"), [Input("mineral-dropdown", "value")]
)
def update_image_list(selected_mineral):
    filtered_df = df[df[selected_mineral] == 1]
    if not filtered_df.empty:
        # Use dbc.Row and dbc.Col to create a responsive grid
        row = dbc.Row(
            [
                dbc.Col(
                    dbc.Card(
                        [
                            dbc.CardHeader(
                                f"ID: {row['ImageID']} - Region: {row['Region']}"
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
        return row
    else:
        return dbc.Alert("No images found for this mineral.", color="warning")


if __name__ == "__main__":
    app.run_server(debug=False)
