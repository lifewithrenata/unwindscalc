from flask import Flask, render_template_string, request
from datetime import datetime

app = Flask(__name__)

# HTML template (mimics Tkinter style: labels, boxes, result box)
template = """
<!DOCTYPE html>
<html>
<head>
    <title>Unwind Fee Calculator</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background: #fafafa; }
        h2 { margin-bottom: 20px; }
        label { display: inline-block; width: 220px; margin-bottom: 8px; }
        input { width: 200px; padding: 5px; margin-bottom: 12px; }
        .button { margin-top: 10px; padding: 8px 14px; }
        .result-box {
            margin-top: 20px;
            padding: 12px;
            border: 1px solid #ccc;
            background: #fff;
            width: 500px;
            white-space: pre-wrap;
            font-family: monospace;
        }
    </style>
</head>
<body>
    <h2>Unwind Fee Calculator</h2>
    <form method="post">
        <label>DV01:</label>
        <input type="text" name="dv01" value="{{ request.form.dv01 }}"><br>

        <label>Client's Original Direction (pays/receives):</label>
            <select name="direction">
            <option value="pays" {% if request.form.direction == 'pays' %}selected{% endif %}>pays</option>
            <option value="receives" {% if request.form.direction == 'receives' %}selected{% endif %}>receives</option>
            </select><br>

        <label>Original Fixed Rate (%):</label>
        <input type="text" name="old_rate" value="{{ request.form.old_rate }}"><br>

        <label>Today's Fixed Rate (%):</label>
        <input type="text" name="new_rate" value="{{ request.form.new_rate }}"><br>

        <input type="submit" value="Calculate" class="button">
    </form>

    {% if result %}
    <div class="result-box">
        {{ result }}
    </div>
    <button onclick="copyResult()">Copy to Clipboard</button>
    <script>
    function copyResult() {
      var text = document.querySelector('.result-box').innerText;
      navigator.clipboard.writeText(text);
    }
    </script>
    {% endif %}
</body>
</html>
"""

@app.route("/", methods=["GET", "POST"])
def unwind():
    result = None
    if request.method == "POST":
        try:
            dv01 = float(request.form["dv01"].replace(",", ""))
            direction = request.form["direction"].lower().strip()
            old_rate = float(request.form["old_rate"]) / 100
            new_rate = float(request.form["new_rate"]) / 100
        except:
            result = "❌ Invalid input. Please check your entries."
        else:
            if direction not in {"pays", "receives"}:
                result = "❌ Direction must be 'pays' or 'receives'."
            else:
                delta_bps = (new_rate - old_rate) * 10000
                s = 1 if direction == "pays" else -1
                fee = s * dv01 * delta_bps

                if fee > 0:
                    label = f"Client receives {fee:,.2f}"
                elif fee < 0:
                    label = f"Client pays {abs(fee):,.2f}"
                else:
                    label = "No unwind fee (flat)"

                today_phrase = "today client receives at" if direction == "pays" else "today client pays at"

                result = (
                    f"Unwind Fee:\n"
                    f"Client {direction} fixed at {old_rate*100:.4f}% → {today_phrase} {new_rate*100:.4f}%\n"
                    f"{label}\n\n"
                    f"Details:\nDV01: {dv01:,.2f}\nMove: {delta_bps:,.2f} bps\n"
                    f"Timestamp: {datetime.now().strftime('%d %b %Y %H:%M:%S')}"
                )

    return render_template_string(template, result=result, request=request)


if __name__ == "__main__":
    app.run(debug=True)