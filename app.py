import gradio as gr
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

initial_params = pd.read_csv("data/params.csv", index_col=0)
population = pd.read_csv("data/population.csv", index_col=0).divide(1e9)


def update_graphs(*slider_values):
    params = pd.DataFrame(np.array(slider_values).reshape(
        2, -1), columns=initial_params.columns, index=initial_params.index)

    fig1, ax1 = plt.subplots()
    population.plot(ax=ax1)
    ax1.set_title("Populations Over Time")
    ax1.set_ylabel("Population (Billions)")

    capacity = population.apply(
        lambda x: x*params.loc['range'], axis=1)
    fig2, ax2 = plt.subplots()
    capacity.plot(ax=ax2)
    ax2.set_title("Welfare Capacities Over Time")
    ax2.set_ylabel("Welfare Capacity (Arbitrary Units)")

    welfare = capacity.apply(lambda x: x*params.loc['value'], axis=1)
    fig3, ax3 = plt.subplots()
    welfare.plot(ax=ax3)
    ax3.set_title("Total Welfare Over Time")
    ax3.set_ylabel("Total Welfare (Arbitrary Units)")

    return fig1, fig2, fig3


with gr.Blocks() as demo:
    gr.Markdown("# Net Global Welfare")

    sliders = []

    with gr.Row():
        with gr.Column():
            gr.Markdown("### Welfare Range (0 to 1)")
            for col in initial_params.columns:
                sliders.append(gr.Slider(
                    minimum=0, maximum=1, value=initial_params.loc['range', col], label=col))

        with gr.Column():
            gr.Markdown("### Welfare Value (-1 to 1)")
            for col in initial_params.columns:
                sliders.append(gr.Slider(
                    minimum=-1, maximum=1, value=initial_params.loc['value', col], label=col))

    with gr.Row():
        graph1 = gr.Plot()
        graph2 = gr.Plot()
        graph3 = gr.Plot()

    graphs = [graph1, graph2, graph3]

    for slider in sliders:
        slider.release(update_graphs, inputs=sliders, outputs=graphs)

    demo.load(update_graphs, inputs=sliders, outputs=graphs)

demo.launch(share=True)
