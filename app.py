import os
import io
import uuid
import sys
import flet as ft
import yaml
import traceback
import cv2
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from PIL import Image
import shutil
import threading

# Load configuration
with open('./config.yaml', 'r') as fd:
    opts = yaml.safe_load(fd)

# Import cartoonizer
sys.path.insert(0, './white_box_cartoonizer/')
from white_box_cartoonizer.cartoonize import WB_Cartoonize

# Initialize cartoonizer
wb_cartoonizer = WB_Cartoonize(os.path.abspath("white_box_cartoonizer/saved_models/"), opts['gpu'])

# Create directories
UPLOAD_FOLDER_IMAGES = 'static/uploaded_images'
CARTOONIZED_FOLDER = 'static/cartoonized_images'

for folder in [UPLOAD_FOLDER_IMAGES, CARTOONIZED_FOLDER]:
    os.makedirs(folder, exist_ok=True)

# Helper functions
def generate_histogram(image, img_name, mode="original"):
    """Generate and save a histogram for RGB channels."""
    plt.figure(figsize=(8, 4))
    colors = ('r', 'g', 'b')
    for i, col in enumerate(colors):
        hist = cv2.calcHist([image], [i], None, [256], [0, 256])
        plt.plot(hist, color=col)
        plt.xlim([0, 256])
    plt.title(f"{mode.capitalize()} Image Histogram")
    plt.xlabel("Pixel Value")
    plt.ylabel("Frequency")
    hist_path = os.path.join(CARTOONIZED_FOLDER, f"{img_name}_{mode}_hist.jpg")
    plt.savefig(hist_path)
    plt.close()
    return hist_path

def generate_pie_chart(image, img_name, mode="original"):
    """Generate and save a pie chart showing the average color distribution."""
    avg_colors = np.mean(image, axis=(0, 1))
    labels = ['Red', 'Green', 'Blue']
    colors = ['red', 'green', 'blue']
    plt.figure(figsize=(5, 5))
    plt.pie(avg_colors, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
    plt.title(f"{mode.capitalize()} Image Color Distribution")
    pie_chart_path = os.path.join(CARTOONIZED_FOLDER, f"{img_name}_{mode}_pie.jpg")
    plt.savefig(pie_chart_path)
    plt.close()
    return pie_chart_path

def generate_bar_graph(image, img_name, mode="original"):
    """Generate and save a bar graph of the average RGB intensities."""
    avg_colors = np.mean(image, axis=(0, 1))
    labels = ['Red', 'Green', 'Blue']
    colors = ['red', 'green', 'blue']
    plt.figure(figsize=(6, 4))
    sns.barplot(x=labels, y=avg_colors, hue=labels, palette=colors, legend=False)
    plt.ylim(0, 255)
    plt.title(f"{mode.capitalize()} Image Average RGB Intensity")
    plt.xlabel("Color Channel")
    plt.ylabel("Intensity")
    bar_graph_path = os.path.join(CARTOONIZED_FOLDER, f"{img_name}_{mode}_bar.jpg")
    plt.savefig(bar_graph_path)
    plt.close()
    return bar_graph_path



# Main app function
def main(page: ft.Page):
    cartoonized_img_path = ft.Ref[str]()
   

    page.title = "ZappyToon"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.bgcolor = "#9B1DA2"  # The same background color as in the HTML
    page.padding = 20
    page.scroll = ft.ScrollMode.AUTO
    
    # Status message display
    status_message = ft.Text(
        size=18,
        color="white",
        text_align=ft.TextAlign.CENTER,
        visible=False
    )
    
    # Loading indicator
    loading = ft.ProgressRing(
        width=40, 
        height=40, 
        stroke_width=4, 
        color="white",
        visible=False
    )
    
    # Results containers
    cartoonized_result = ft.Container(visible=False)
    visualization_buttons = ft.Container(visible=False)
    
    # Graph containers
    histogram_container = ft.Container(visible=False)
    pie_chart_container = ft.Container(visible=False)
    bar_graph_container = ft.Container(visible=False)
    
    # Create header
    header = ft.Column([
         ft.Container(
    content=ft.Text(
        "ZappyToon",
        size=40,
        weight="bold",
        color="white",
        text_align=ft.TextAlign.CENTER,
    ),
    alignment=ft.alignment.center,
),
        ft.Container(
    content=ft.Text(
        "Make Every Memory a Masterpiece in Toon Form",
        size=30,
        weight="bolder",
        color="white",
        text_align=ft.TextAlign.CENTER,
    ),
    alignment=ft.alignment.center,
),
            ft.Container(
        content=ft.Text(
            "Transform Your Favourite ImaSges",
            size=20,
            color="#E3F2FD",
            text_align=ft.TextAlign.CENTER,
        ),
        # margin=ft.margin.only(left=95),
        alignment=ft.alignment.center,
            ),
       ft.Container(
        content=ft.Image(
        src="images/img.jpg",
        width=350,
        height=350,
        fit=ft.ImageFit.CONTAIN
        ),
        alignment=ft.alignment.center,
         margin=ft.margin.only(top=0,bottom=0)
        )
        ], alignment="center")
    
   
    
    # Function to show histogram
    def show_histogram(e):
        histogram_container.visible = True
        pie_chart_container.visible = False
        bar_graph_container.visible = False
        page.update()
    
    # Function to show pie chart
    def show_pie_chart(e):
        histogram_container.visible = False
        pie_chart_container.visible = True
        bar_graph_container.visible = False
        page.update()
    
    # Function to show bar graph
    def show_bar_graph(e):
        histogram_container.visible = False
        pie_chart_container.visible = False
        bar_graph_container.visible = True
        page.update()
    
    
    def hide_cartoon_image():
        cartoonized_result.visible = False
        visualization_buttons.visible = False
        histogram_container.visible = False
        pie_chart_container.visible = False
        bar_graph_container.visible = False
        status_message.value = "Cartoon expired. Please upload again."
        status_message.color = "red"
        status_message.visible = True
        page.update()

# Schedule to run after 5 minutes (300 seconds)
   


    # Function to handle image processing
    def process_image(e: ft.FilePickerResultEvent):
        if not e.files or len(e.files) == 0:
            color="red"
            status_message.value = "No file selected"
            status_message.visible = True
            page.update()
            return
        
        try:
            # Show loading
            loading.visible = True
            status_message.value = "Processing your image..."
            status_message.visible = True
            page.update()
            
            # Reset all visualization containers
            histogram_container.visible = False
            pie_chart_container.visible = False
            bar_graph_container.visible = False
            page.update()
            
            # For mobile compatibility, save to a temporary file first
            file_path = e.files[0].path
            
            if not file_path:
                raise Exception("Failed to get image file path")
                
            # Create a temporary file path in our uploaded_images folder
            img_filename = str(uuid.uuid4()) + os.path.splitext(file_path)[1]
            temp_path = os.path.join(UPLOAD_FOLDER_IMAGES, img_filename)
            
            # Copy the file to our temporary location where we can access it
            shutil.copy2(file_path, temp_path)
            
            # Now read the image from our temporary location
            image = cv2.imread(temp_path)
            if image is None:
                # If still can't read, try with PIL as a fallback
                try:
                    pil_image = Image.open(temp_path)
                    image = np.array(pil_image)
                    if len(image.shape) == 3 and image.shape[2] == 3:
                        # Already RGB
                        pass
                    elif len(image.shape) == 3 and image.shape[2] == 4:
                        # Convert RGBA to RGB
                        pil_image = Image.open(temp_path).convert('RGB')
                        image = np.array(pil_image)
                    else:
                        # Convert grayscale to RGB
                        pil_image = Image.open(temp_path).convert('RGB')
                        image = np.array(pil_image)
                except Exception as pil_err:
                    raise Exception(f"Failed to read image with both OpenCV and PIL: {str(pil_err)}")
            else:
                # Convert BGR to RGB
                image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            cartoon_image = wb_cartoonizer.infer(image)
            img_name = str(uuid.uuid4())
            cartoonized_img_name = os.path.join(CARTOONIZED_FOLDER, img_name + ".jpg")
            cv2.imwrite(cartoonized_img_name, cv2.cvtColor(cartoon_image, cv2.COLOR_RGB2BGR))
            cartoonized_img_path.current = cartoonized_img_name
           
            
            # Generate original analysis
            orig_hist_path = generate_histogram(image, img_name, "original")
            orig_pie_path = generate_pie_chart(image, img_name, "original")
            orig_bar_path = generate_bar_graph(image, img_name, "original")
            
            # Cartoonize the image
            cartoon_image = wb_cartoonizer.infer(image)
            cartoonized_img_name = os.path.join(CARTOONIZED_FOLDER, img_name + ".jpg")
            cv2.imwrite(cartoonized_img_name, cv2.cvtColor(cartoon_image, cv2.COLOR_RGB2BGR))
            
            # Generate cartoonized analysis
            cartoon_hist_path = generate_histogram(cartoon_image, img_name, "cartoonized")
            cartoon_pie_path = generate_pie_chart(cartoon_image, img_name, "cartoonized")
            cartoon_bar_path = generate_bar_graph(cartoon_image, img_name, "cartoonized")
            
            # Update the UI with the results
            cartoonized_result.content = ft.Column([
                ft.Image(
                    src=cartoonized_img_name,
                    width=500,
                    fit="contain",
                    border_radius=10
                ),
                ft.FilledButton(
                text="Download",
                icon="download",
                on_click=lambda _: save_dialog.save_file(file_name="cartoonized.jpg")
                ),

                ft.Text(
                    "(Valid for 5 minutes only!)",
                    size=16,
                    weight=ft.FontWeight.BOLD,
                    color="#FF0000",
                    text_align=ft.TextAlign.CENTER,
                )
            ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER)
            cartoonized_result.visible = True
            
            # Setup visualization buttons
            visualization_buttons.content = ft.Column([
                ft.Text(
                    "Color Distribution & Intensity Analysis",
                    size=26,
                    weight="bold",
                    color="white",
                    text_align="center"
                ),
                ft.Row([
                    ft.ElevatedButton(
                        text="Histogram",
                        icon="bar_chart",
                        style=ft.ButtonStyle(
                            color="white",
                            bgcolor="blue",
                            shape=ft.RoundedRectangleBorder(radius=8)
                        ),
                        on_click=show_histogram
                    ),
                    ft.ElevatedButton(
                        text="Pie Chart",
                        icon="pie_chart",
                        style=ft.ButtonStyle(
                            color="white",
                            bgcolor="green",
                            shape=ft.RoundedRectangleBorder(radius=8)
                        ),
                        on_click=show_pie_chart
                    ),
                    ft.ElevatedButton(
                        text="Bar Graph",
                        icon="analytics",
                        style=ft.ButtonStyle(
                            color="white",
                            bgcolor="orange",
                            shape=ft.RoundedRectangleBorder(radius=8)
                        ),
                        on_click=show_bar_graph
                    )
                ], alignment=ft.MainAxisAlignment.CENTER, spacing=10, wrap=True)
            ], alignment=ft.MainAxisAlignment.CENTER)
            visualization_buttons.visible = True
            
            # Setup the graph containers
            histogram_container.content = ft.ResponsiveRow([
                ft.Column([
                    ft.Text("Original Image", size=18, color="white"),
                    ft.Image(src=orig_hist_path, width=350, fit="contain", border_radius=10)
                ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER, col={"sm": 12, "md": 6}),
                ft.Column([
                    ft.Text("Cartoonized Image", size=18, color="white"),
                    ft.Image(src=cartoon_hist_path, width=350, fit="contain", border_radius=10)
                ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER, col={"sm": 12, "md": 6})
            ])
            
            pie_chart_container.content = ft.ResponsiveRow([
                ft.Column([
                    ft.Text("Original Image", size=18, color="white"),
                    ft.Image(src=orig_pie_path, width=350, fit="contain", border_radius=10)
                ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER, col={"sm": 12, "md": 6}),
                ft.Column([
                    ft.Text("Cartoonized Image", size=18, color="white"),
                    ft.Image(src=cartoon_pie_path, width=350, fit="contain", border_radius=10)
                ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER, col={"sm": 12, "md": 6})
            ])
            
            bar_graph_container.content = ft.ResponsiveRow([
                ft.Column([
                    ft.Text("Original Image", size=18, color="white"),
                    ft.Image(src=orig_bar_path, width=350, fit="contain", border_radius=10)
                ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER, col={"sm": 12, "md": 6}),
                ft.Column([
                    ft.Text("Cartoonized Image", size=18, color="white"),
                    ft.Image(src=cartoon_bar_path, width=350, fit="contain", border_radius=10)
                ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER, col={"sm": 12, "md": 6})
            ])
            
            # # Hide loading and update message
            # loading.visible = False
            # status_message.value = "Your cartoon is ready!"
            # page.update()
            
            # Hide loading and update message
            loading.visible = False
            status_message.value = "Your cartoon is ready!"
            status_message.color = "green"
            page.update()

            # Start 5-minute countdown to clear the cartoon
            threading.Timer(300, hide_cartoon_image).start()


        except Exception as e:
            # Handle errors
            loading.visible = False
            status_message.value = f"Error: {str(e)}"
            status_message.color = "redAccent"
            status_message.visible = True
            print(traceback.format_exc())
            page.update()
    
    # Set up file picker for mobile compatibility
    image_picker = ft.FilePicker(on_result=process_image)
    page.overlay.extend([image_picker])
    # Define on_save FIRST
    def on_save(e: ft.FilePickerResultEvent):
        if e.path and cartoonized_img_path.current:
            shutil.copy(cartoonized_img_path.current, e.path)
            status_message.value = "Image downloaded successfully!"
            status_message.color = "green"
            status_message.visible = True
            page.update()

    # Then assign it to FilePicker
    save_dialog = ft.FilePicker(on_result=on_save)
    page.overlay.append(save_dialog)



    # Create upload button
    upload_container = ft.Column([
        ft.ElevatedButton(
            content=ft.Row([
                ft.Icon("image"),
                ft.Text("Get Cartoon Magic!", size=18)
            ], alignment=ft.MainAxisAlignment.CENTER, spacing=10),
            style=ft.ButtonStyle(
                color="white",
                bgcolor="blue",
                shape=ft.RoundedRectangleBorder(radius=12),
                padding=20
            ),
            on_click=lambda _: image_picker.pick_files(
                allow_multiple=False,
                file_type=ft.FilePickerFileType.IMAGE
            )
        )
    ], alignment=ft.MainAxisAlignment.CENTER)
    
    # Create sample images section
    sample_section = ft.Column([
        ft.Divider(height=2, color="white"),
        ft.Text("", size=24, color="white", text_align=ft.TextAlign.CENTER),
        ft.ResponsiveRow([
            ft.Column([
                ft.Image(
                    src="/static/sample_images/emma2.jpg",
                    width=300,
                    fit=ft.ImageFit.CONTAIN,
                    border_radius=10
                )
            ], col={"sm": 12, "md": 6}, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            ft.Column([
                ft.Image(
                    src="/static/sample_images/emma2_cartoonized.jpg",
                    width=300,
                    fit=ft.ImageFit.CONTAIN,
                    border_radius=10
                )
            ], col={"sm": 12, "md": 6}, horizontal_alignment=ft.CrossAxisAlignment.CENTER)
        ]),
        ft.ResponsiveRow([
            ft.Column([
                ft.Image(
                    src="/static/sample_images/spice.jpeg",
                    width=300,
                    fit="contain",
                    border_radius=10
                )
            ], col={"sm": 12, "md": 6}, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            ft.Column([
                ft.Image(
                    src="/static/sample_images/spice_cartoonized.jpeg",
                    width=300,
                    fit="contain",
                    border_radius=10
                )
            ], col={"sm": 12, "md": 6}, horizontal_alignment=ft.CrossAxisAlignment.CENTER)
        ]),
        ft.ResponsiveRow([
            ft.Column([
                ft.Image(
                    src="/static/sample_images/cake.jpeg",
                    width=300,
                    fit="contain",
                    border_radius=10
                )
            ], col={"sm": 12, "md": 6}, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            ft.Column([
                ft.Image(
                    src="/static/sample_images/cake_cartoonized.jpeg",
                    width=300,
                    fit="contain",
                    border_radius=10
                )
            ], col={"sm": 12, "md": 6}, horizontal_alignment=ft.CrossAxisAlignment.CENTER)
        ])
    ], scroll=ft.ScrollMode.AUTO)
    
    # Footer
    footer = ft.Container(
        content=ft.Row([
            ft.Icon("copyright_outlined", color="amber"),
            ft.Text(" 2025-26 - Made by Chidhesh", color="white", size=18)
        ], alignment=ft.MainAxisAlignment.CENTER),
        padding=ft.padding.only(top=20, bottom=20)
    )
    
    # Add all components to the page
    page.add(
        header,
        ft.Container(height=20),
        status_message,
        ft.Container(
            content=loading,
            alignment=ft.alignment.center
        ),
        ft.Container(height=20),
        upload_container,
        ft.Container(height=20),
        cartoonized_result,
        ft.Container(height=20),
        visualization_buttons,
        ft.Container(height=10),
        histogram_container,
        pie_chart_container,
        bar_graph_container,
        ft.Container(height=40),
        sample_section,
        footer
    )

# Run the app
if __name__ == "__main__":
    ft.app(target=main)