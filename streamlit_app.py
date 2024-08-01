import os
from PIL import Image, ImageChops
import streamlit as st
from io import BytesIO

# Default parameters
default_target_size = (450, 300)  # Set a standard size for all logos (width, height)
default_padding = 50  # Padding between logos and around the entire collage
default_padding_top_bottom = -50  # Padding specifically for top and bottom between rows
default_padding_outer_top_bottom = 0  # Padding on top and bottom of the entire logo palette
default_rows = 2  # Number of rows in the collage

def trim(image):
    bg = Image.new('RGBA', image.size, (255, 255, 255, 0))  # Create a background with white or transparent
    diff = ImageChops.difference(image.convert('RGBA'), bg)
    bbox = diff.getbbox()
    if bbox:
        return image.crop(bbox)
    return image

def create_logo_grid(logos, target_size, padding, rows, padding_top_bottom, padding_outer_top_bottom):
    # Resize logos to fit within the target dimensions while maintaining aspect ratio
    resized_logos = []
    for logo in logos:
        logo = trim(logo)

        # Calculate the scale factor to maintain aspect ratio
        scale_factor = min(target_size[0] / logo.width, target_size[1] / logo.height)

        # Resize the logo
        new_size = (int(logo.width * scale_factor), int(logo.height * scale_factor))
        logo = logo.resize(new_size, Image.LANCZOS)

        # Ensure the image has an alpha channel
        if logo.mode != 'RGBA':
            logo = logo.convert('RGBA')

        # Create a new image with a transparent background
        new_logo = Image.new('RGBA', target_size, (255, 255, 255, 0))

        # Calculate position to paste the resized logo so it is centered
        paste_position = (
            (target_size[0] - logo.size[0]) // 2,
            (target_size[1] - logo.size[1]) // 2
        )
        new_logo.paste(logo, paste_position, logo)
        resized_logos.append(new_logo)

    # Calculate the number of columns needed
    num_logos = len(resized_logos)
    cols = (num_logos + rows - 1) // rows  # Ceiling division to ensure all logos fit

    # Calculate the total width and height, including padding
    total_width = (target_size[0] * cols) + (padding * (cols - 1)) + 2 * padding
    total_height = (target_size[1] * rows) + (padding_top_bottom * (rows - 1)) + 2 * padding_outer_top_bottom

    # Create a new image with a white background
    result = Image.new('RGB', (total_width, total_height), (255, 255, 255))

    # Calculate the positions to paste the logos so they are centered with padding
    for i, logo in enumerate(resized_logos):
        row = i // cols
        col = i % cols
        x = col * (target_size[0] + padding) + padding
        y = row * (target_size[1] + padding_top_bottom) + padding_outer_top_bottom
        
        # Convert the logo back to RGB before pasting
        logo_rgb = logo.convert('RGB')
        result.paste(logo_rgb, (x, y))

    return result

# Streamlit UI
st.title("Logo Grid Generator")

st.write("Hey designers 👋 Tired of wasting time aligning sponsor logos? The Logo Grid Generator is your new BFF. Just upload your logos, drag and drop to reorder, tweak the grid with easy sliders, and boom – a perfect logo collage ready to download. Save time, keep your creative mojo, and let this tool handle the boring stuff. 🎨✨")

st.markdown("---")
st.write("")

uploaded_files = st.file_uploader("Upload multiple images", type=["png", "jpg", "jpeg"], accept_multiple_files=True)

if uploaded_files:
    # Create a list of file names
    file_names = [file.name for file in uploaded_files]
    # Create a list to hold the reordered file names
    reordered_files = file_names.copy()

    # Display the select boxes to reorder the files
    st.markdown("---")

    for i in range(len(file_names)):
        selected_file = st.selectbox(f"Select image for position {i+1}", file_names, index=i, key=f"select_{i}")
        reordered_files[i] = selected_file

    # Reorder the uploaded files based on the selected order
    reordered_uploaded_files = [file for file_name in reordered_files for file in uploaded_files if file.name == file_name]
    
    st.markdown("---")

    # Use columns to arrange sliders and grid side by side
    col1, col2 = st.columns(2)

    with col1:
        grid_width = st.slider("Grid Width in px.", 100, 1000, default_target_size[0])
        grid_height = st.slider("Grid Height in px", 100, 1000, default_target_size[1])
        space_around_grid = st.slider("Space around Grid in px", 0, 100, default_padding)
    with col2:
        number_of_rows = st.slider("Number of Rows", 1, 10, default_rows)
        space_between_rows = st.slider("Space between Rows in px", -100, 100, default_padding_top_bottom)
        add_space_to_top_bottom = st.slider("Add Space to Top & Bottom in px", -100, 100, default_padding_outer_top_bottom)

    # Load images
    logos = [Image.open(file) for file in reordered_uploaded_files]

    # Process images
    with st.spinner('Processing...'):
        result_image = create_logo_grid(logos, (grid_width, grid_height), space_around_grid, number_of_rows, space_between_rows, add_space_to_top_bottom)

    st.image(result_image, caption='Generated Logo Grid')

    # Text input for the final file name after the image is displayed
    file_name = st.text_input("Rename your file", value="logo_grid")

    if not file_name:
        st.error("Please provide a valid file name.")
    else:
        # Ensure the filename ends with .png
        if not file_name.endswith(".png"):
            file_name += ".png"

        # Save the result image to a BytesIO object
        img_buffer = BytesIO()
        result_image.save(img_buffer, format="PNG")
        img_buffer.seek(0)

        # Provide download link
        btn = st.download_button(label="Download Image", data=img_buffer, file_name=file_name, mime="image/png")


# Custom CSS
st.markdown(
    """
    <style>
            @import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&display=swap');
            @import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=Inter:ital,opsz,wght@0,14..32,100..900;1,14..32,100..900&display=swap');
    
            .appview-container {
            }
            
            h1 {
                font-family: "DM Serif Display", serif;
                color: #000;
                font-weight: 500;
                font-size: calc(1.475rem + 3vw);
                max-font-size: 3rem;
                margin-top: 80px;
                margin-bottom: 20px;
            }
    
            @media (min-width: 1320px) {
                h1 {
                    font-size: 4rem;
                }
            }
    
            p {
                font-family: "Inter", sans-serif;
            }
    
            header{
            background: transparent!important;
            pointer-events: none; /* Allow clicks to pass through */
            }
    
            header * {
            pointer-events: initial;
            }
    
            #navbar {
                position: fixed;
                top: 0;
                left: 0;
                width: 100vw;
                padding-top: 0rem;
                background:white;
                z-index: 100;
            }
    
            #logocontainer {
                max-width: 1320px;
                margin: auto;
                padding: 8px 20px 8px 20px;
            }
    
            #logo {
                box-shadow: none !important;
                height: 55px;
                z-index: 1000000000;
                margin-top: .40625rem;
                margin-bottom: .40625rem;
            }
    
            .element-container div div:has(> img) {
                width: 100%;
                display: flex;
            }
    
            .element-container div div img {
                box-shadow: 0px 0px 10px rgba(0, 0, 0, 0.5);
                margin: auto;
            }
            
            @keyframes fadeInSlideUp {
                0% {
                    opacity: 0;
                }
                100% {
                    opacity: 1;
            }
    </style>
    <div id="navbar">
        <div id="logocontainer">
            <a href="https://xn--gbs-qla.com/" target="_blank">
                <img src="https://xn--gbs-qla.com/assets/images/logo/logo-dark.svg" class="logo" id="logo">
            </a>
        </div>
    </div>
    """, unsafe_allow_html=True
)
