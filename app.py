import gradio as gr
from video_engine import generate_ad

TITLE = "Umer Video AI - Local Ad Generator"

def run(prompt, duration, aspect, quality, reference, product_demo, seed):
    return generate_ad(
        prompt=prompt,
        duration=int(duration),
        aspect=aspect,
        quality=quality,
        reference_image=reference,
        product_demo=product_demo,
        seed=int(seed),
    )

with gr.Blocks(title=TITLE) as demo:
    gr.Markdown("# Umer Video AI\nLocal/open-source ad video generation. No per-video API fee when you run it on your own hardware.")
    with gr.Row():
        with gr.Column():
            prompt = gr.Textbox(
                label="Ad prompt",
                lines=12,
                value="Create a photorealistic vertical UGC ad for an AI assistant. One adult creator in a realistic home office, natural smartphone camera movement, believable lighting, accurate product branding, no fake UI text, no unrelated logos."
            )
            duration = gr.Slider(4, 30, value=12, step=1, label="Total duration (seconds)")
            aspect = gr.Dropdown(["9:16", "16:9", "1:1"], value="9:16", label="Aspect ratio")
            quality = gr.Dropdown(["fast", "quality", "ultra"], value="quality", label="Quality preset")
            reference = gr.Image(type="filepath", label="Creator / product reference image (optional)")
            product_demo = gr.Video(label="Real product screen recording (optional)")
            seed = gr.Number(value=42, precision=0, label="Seed")
            generate = gr.Button("Generate ad", variant="primary")
        with gr.Column():
            output = gr.Video(label="Generated ad")
            status = gr.Textbox(label="Status", interactive=False)

    generate.click(
        fn=run,
        inputs=[prompt, duration, aspect, quality, reference, product_demo, seed],
        outputs=[output, status],
    )

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860)
