import gradio as gr
from trading_system import run_scan

def run_trading_system():
    try:
        buys, sells, full = run_scan()
        status = f"✅ Scan completed | BUY: {len(buys)} | SELL: {len(sells)}"
        return buys, sells, full, status
    except Exception as e:
        return None, None, None, f"❌ Error: {e}"

with gr.Blocks(title="NSE500 Quant Swing Trading System") as demo:
    gr.Markdown("# 📈 NSE500 Quantitative Swing Trading System")

    run_btn = gr.Button("▶ Run Daily Scan")

    status = gr.Textbox(label="Status", lines=2)

    with gr.Tab("🟢 Buy Matrix"):
        buy_table = gr.Dataframe(label="New BUY Signals")

    with gr.Tab("🔴 Sell / Exit Alerts"):
        sell_table = gr.Dataframe(label="Exit Signals")

    with gr.Tab("🔍 Full Market Context"):
        full_table = gr.Dataframe(label="Complete NSE500 Scan")

    run_btn.click(
        fn=run_trading_system,
        inputs=[],
        outputs=[buy_table, sell_table, full_table, status]
    )

demo.launch()
