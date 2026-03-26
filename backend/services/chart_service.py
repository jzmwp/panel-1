"""Chart generation service using matplotlib."""

import base64
import io
import logging

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

logger = logging.getLogger(__name__)

# Mine-appropriate color palette
COLORS = ["#2563eb", "#dc2626", "#16a34a", "#ea580c", "#9333ea", "#0891b2", "#4f46e5", "#c026d3"]


def generate_chart(config: dict) -> dict:
    """Generate a chart and return base64-encoded PNG."""
    try:
        chart_type = config["chart_type"]
        title = config.get("title", "")
        x_label = config.get("x_label", "")
        y_label = config.get("y_label", "")
        data = config["data"]
        labels = data["labels"]
        datasets = data["datasets"]

        fig, ax = plt.subplots(figsize=(10, 6))
        fig.patch.set_facecolor("#1e1e2e")
        ax.set_facecolor("#1e1e2e")

        ax.tick_params(colors="#cdd6f4")
        ax.xaxis.label.set_color("#cdd6f4")
        ax.yaxis.label.set_color("#cdd6f4")
        ax.title.set_color("#cdd6f4")
        for spine in ax.spines.values():
            spine.set_color("#45475a")

        if chart_type == "line":
            for i, ds in enumerate(datasets):
                ax.plot(labels, ds["values"], label=ds["label"],
                        color=COLORS[i % len(COLORS)], linewidth=2, marker="o", markersize=4)

        elif chart_type == "bar":
            import numpy as np
            x = np.arange(len(labels))
            width = 0.8 / len(datasets)
            for i, ds in enumerate(datasets):
                offset = (i - len(datasets) / 2 + 0.5) * width
                ax.bar(x + offset, ds["values"], width, label=ds["label"],
                       color=COLORS[i % len(COLORS)])
            ax.set_xticks(x)
            ax.set_xticklabels(labels, rotation=45, ha="right")

        elif chart_type == "scatter":
            for i, ds in enumerate(datasets):
                ax.scatter(labels, ds["values"], label=ds["label"],
                          color=COLORS[i % len(COLORS)], s=50)

        elif chart_type == "pie":
            if datasets:
                ax.pie(datasets[0]["values"], labels=labels, autopct="%1.1f%%",
                       colors=COLORS[:len(labels)])

        ax.set_title(title, fontsize=14, fontweight="bold", pad=15)
        if x_label:
            ax.set_xlabel(x_label)
        if y_label:
            ax.set_ylabel(y_label)
        if chart_type != "pie" and datasets:
            ax.legend(facecolor="#313244", edgecolor="#45475a", labelcolor="#cdd6f4")

        plt.xticks(rotation=45, ha="right")
        plt.tight_layout()

        buf = io.BytesIO()
        fig.savefig(buf, format="png", dpi=150, bbox_inches="tight",
                    facecolor=fig.get_facecolor())
        plt.close(fig)
        buf.seek(0)

        image_b64 = base64.b64encode(buf.read()).decode("utf-8")
        return {"image": image_b64}

    except Exception as e:
        logger.exception("Chart generation error")
        return {"error": str(e)}
