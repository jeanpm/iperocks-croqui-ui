import json
import os

import streamlit as st
from unidecode import unidecode

from iperocks_croqui_ui.export_pdf import export_to_pdf


# Load JSON data
def load_data(json_file):
    with open(json_file, "r", encoding="utf-8") as file:
        data = json.load(file)
    return data


# Normalize names by converting to lowercase and removing accents
def normalize_name(name):
    return unidecode(name).strip().lower() if name else ""


# Load and filter routes based on normalized selections
def get_filtered_routes(data, grade, block, sector):
    filtered_routes = []
    by_grade = data.get("by_grade", {})

    # Normalize grade
    if grade:
        filtered_routes.extend(by_grade.get(grade, []))
    else:
        for routes in by_grade.values():
            filtered_routes.extend(routes)

    # Normalize block and sector
    if block:
        block = normalize_name(block)
        filtered_routes = [
            route
            for route in filtered_routes
            if normalize_name(route.get("block")) == block
        ]
    if sector:
        sector = normalize_name(sector)
        filtered_routes = [
            route
            for route in filtered_routes
            if normalize_name(route.get("sector")) == sector
        ]

    return filtered_routes


# Streamlit App
# st.title("Climbing Routes Viewer")

st.set_page_config(layout="wide")

# Load data
data = load_data("output/consolidated_routes.json")
image_folder = "output/Croqui_Iperocks_v4-3"  # Replace with your image folder path

# Extract unique values for filters, normalize them for uniformity
sectors = sorted(
    set(
        normalize_name(route["sector"])
        for grade_routes in data["by_grade"].values()
        for route in grade_routes
    )
)

st.sidebar.divider()
st.sidebar.caption("Filters")

with st.sidebar:
    # Sidebar filters
    selected_sector = st.selectbox("Select Sector", ["All"] + sectors)

    # Filter blocks based on selected sector
    if selected_sector != "All":
        filtered_blocks = sorted(
            set(
                normalize_name(route["block"])
                for grade_routes in data["by_grade"].values()
                for route in grade_routes
                if normalize_name(route["sector"]) == selected_sector
            )
        )
    else:
        filtered_blocks = sorted(
            set(
                normalize_name(route["block"])
                for grade_routes in data["by_grade"].values()
                for route in grade_routes
            )
        )

    selected_block = st.selectbox("Select Block", ["All"] + filtered_blocks)

    # Filter grades based on selected block
    if selected_block != "All":
        filtered_grades = sorted(
            set(
                route["grade"]
                for grade_routes in data["by_grade"].values()
                for route in grade_routes
                if normalize_name(route["block"]) == selected_block
            )
        )
    else:
        filtered_grades = sorted(data["by_grade"].keys())

    selected_grade = st.selectbox("Select Grade", ["All"] + filtered_grades)

    # Filter routes based on normalized selections
    filtered_routes = get_filtered_routes(
        data,
        selected_grade if selected_grade != "All" else None,
        selected_block if selected_block != "All" else None,
        selected_sector if selected_sector != "All" else None,
    )

    if not filtered_routes:
        st.warning("No routes match the selected criteria. Please adjust your filters.")
    else:
        # Display filtered routes
        route_options = [
            f"{route['name']} ({route['grade']})" for route in filtered_routes
        ]
        route_page_numbers = [route["page_number"] for route in filtered_routes]

        st.divider()
        st.caption(f"Filtered results ({len(filtered_routes)} routes found)")

        # Initialize session state for current route index
        if "current_route_index" not in st.session_state:
            st.session_state.current_route_index = 0

        # Ensure current route index is within range
        if st.session_state.current_route_index >= len(filtered_routes):
            st.session_state.current_route_index = 0

        # Display navigation buttons
        # prev_disabled = st.session_state.current_route_index == 1
        # next_disabled = st.session_state.current_route_index == len(route_options) - 2

        # col2, col2 = st.columns([1, 1])
        # with col2:
        #     if st.button("Previous", disabled=prev_disabled, use_container_width=True):
        #         if st.session_state.current_route_index > 1:
        #             st.session_state.current_route_index -= 2
        # with col3:
        #     if st.button("Next", disabled=next_disabled, use_container_width=True):
        #         if st.session_state.current_route_index < len(route_options) - 2:
        #             st.session_state.current_route_index += 1

        # Update selected route based on button navigation
        selected_route = route_options[st.session_state.current_route_index]

        # Select route from dropdown
        selected_route = st.selectbox(
            "Select Route",
            route_options,
            label_visibility="collapsed",
            index=st.session_state.current_route_index,
        )
        st.session_state.current_route_index = route_options.index(selected_route)

        st.divider()
        st.caption("Export as PDF")
        exp1, exp2 = st.columns([1, 1])
        with exp1:
            export_pdf = st.button("Export PDF", use_container_width=True)

        with exp2:
            if export_pdf:
                pdf_path = export_to_pdf(
                    filtered_routes,
                    image_folder,
                    "output",
                    selected_sector,
                    selected_block,
                    selected_grade,
                )
                # Provide download link for the generated PDF
                with open(pdf_path, "rb") as file:
                    st.download_button(
                        label="Download PDF",
                        data=file,
                        file_name=os.path.basename(pdf_path),
                        mime="application/pdf",
                        use_container_width=True,
                    )

# Display route information
current_route = filtered_routes[st.session_state.current_route_index]
st.subheader(
    f"{current_route['sector']} / {current_route['block']} / {current_route['name']} - {current_route['grade']}"
)
st.text(current_route["description"])

# Display route image if available
image_filename = f"page_{current_route['page_number']}.png"  # Assuming image filenames follow this pattern
image_path = os.path.join(image_folder, image_filename)

if os.path.exists(image_path):
    st.image(image_path, caption=f"Page {current_route['page_number']}")

    # Display navigation buttons below the image
    prev_disabled = st.session_state.current_route_index == 0
    next_disabled = st.session_state.current_route_index == len(route_options) - 1

    col1, col2, rempty = st.columns([1, 1, 3])
    rempty.empty()
    with col1:
        if st.button("Previous", disabled=prev_disabled, use_container_width=True):
            if st.session_state.current_route_index > 0:
                st.session_state.current_route_index -= 1
    with col2:
        if st.button("Next", disabled=next_disabled, use_container_width=True):
            if st.session_state.current_route_index < len(route_options) - 1:
                st.session_state.current_route_index += 1
else:
    st.text("Image not available")
