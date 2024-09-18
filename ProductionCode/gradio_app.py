import gradio as gr
import numpy as np
import matplotlib.pyplot as plt
from scipy import integrate
import threading
import time

def plot_function(expression, x_range):
    x = np.linspace(-x_range, x_range, 200)
    try:
        y = eval(expression)
        fig, ax = plt.subplots()
        ax.plot(x, y)
        ax.set_xlabel('x')
        ax.set_ylabel('y')
        ax.set_title(f'y = {expression}')
        ax.grid(True)
        return fig
    except:
        return None

def calculate_area(expression, x_range):
    try:
        func = lambda x: eval(expression)
        area, _ = integrate.quad(func, -x_range, x_range)
        return f"The area under the curve from -{x_range} to {x_range} is approximately {area:.4f}"
    except:
        return "Unable to calculate the area. Please check your expression."

def update_graph_and_area(expression, x_range):
    graph = plot_function(expression, x_range)
    area = calculate_area(expression, x_range)
    return graph, area

def background_task(interval=3):
    count = 0
    while True:
        time.sleep(interval)
        count += 1
        yield f"Background task update: {count}"

def update_status(status):
    return status

with gr.Blocks() as demo:
    gr.Markdown("# Function Plotter and Area Calculator")
    
    with gr.Row():
        with gr.Column():
            expression_input = gr.Textbox(label="Enter a math expression (use 'x' as the variable)", value="x**2")
            x_range_slider = gr.Slider(minimum=1, maximum=10, step=0.5, label="X-axis range", value=5)
            calculate_button = gr.Button("Calculate Area")
        
        with gr.Column():
            plot_output = gr.Plot(label="Function Plot")
            area_output = gr.Textbox(label="Area Calculation Result")
    
    status_output = gr.Textbox(label="Background Task Status")
    status_state = gr.State()
    
    expression_input.change(update_graph_and_area, inputs=[expression_input, x_range_slider], outputs=[plot_output, area_output])
    x_range_slider.change(update_graph_and_area, inputs=[expression_input, x_range_slider], outputs=[plot_output, area_output])
    calculate_button.click(calculate_area, inputs=[expression_input, x_range_slider], outputs=area_output)

    demo.load(background_task, None, status_state, every=3)
    status_state.change(update_status, inputs=[status_state], outputs=[status_output])
demo.queue().launch()
