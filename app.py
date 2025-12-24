import gradio as gr
import pandas as pd
from trading_system import run_scan

def run_trading_system():
    try:
        output_path = run_scan()
        df = pd.read_csv(output_path)
        return df, f"✅ Scan completed successfully.\nRows: {len(df)}"
    except Exception as e:
        return None, f"❌ Error: {str(e)}"

with gr.Blocks(title="NSE500 Quant Swing Trading System") as demo:
    gr.Markdown(
        """
        # 📈 NSE500 Quantitative Swing Trading System
        Rule-based offline quantitative strategy using RSI, MA & Volume.
        """
    )

    run_btn = gr.Button("▶ Run Daily Scan")

    status = gr.Textbox(label="Status", lines=3)
    output_table = gr.Dataframe(label="Scan Results")

    run_btn.click(
        fn=run_trading_system,
        inputs=[],
        outputs=[output_table, status]
    )

if __name__ == "__main__":
    demo.launch()
