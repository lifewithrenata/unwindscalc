from flask import Flask, render_template_string, request
from datetime import datetime

app = Flask(__name__)

template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Unwind Fee Calculator</title>
    <style>
        :root {
            --bg:#0f172a;         /* slate-900 */
            --card:#111827;       /* gray-900 */
            --ink:#e5e7eb;        /* gray-200 */
            --muted:#9ca3af;      /* gray-400 */
            --accent:#22d3ee;     /* cyan-400 */
            --accent-2:#38bdf8;   /* sky-400 */
            --ok:#22c55e;         /* green-500 */
            --bad:#ef4444;        /* red-500 */
            --border:#1f2937;     /* gray-800 */
            --chip:#0b1220;       /* dark chip */
        }
        * { box-sizing: border-box; }
        html, body { height: 100%; }
        body {
            margin: 0;
            font-family: ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial, "Apple Color Emoji", "Segoe UI Emoji";
            background: radial-gradient(1200px 800px at 10% 10%, #0b1220 0%, var(--bg) 40%),
                        radial-gradient(900px 700px at 100% 0%, #0b1220 0%, var(--bg) 40%),
                        var(--bg);
            color: var(--ink);
            -webkit-font-smoothing: antialiased;
        }
        .wrap {
            max-width: 840px;
            margin: 40px auto;
            padding: 24px;
        }
        .card {
            background: linear-gradient(180deg, rgba(255,255,255,0.02), rgba(255,255,255,0.0));
            border: 1px solid var(--border);
            border-radius: 16px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.25);
            backdrop-filter: blur(6px);
            padding: 24px;
        }
        h1 {
            font-size: 26px; margin: 0 0 4px 0; letter-spacing: 0.3px;
        }
        .sub {
            color: var(--muted); margin-bottom: 18px; font-size: 14px;
        }
        form { display: grid; grid-template-columns: repeat(12, 1fr); gap: 14px; }
        .field { grid-column: span 12; }
        @media (min-width: 720px) {
            .field.half { grid-column: span 6; }
            .field.third { grid-column: span 4; }
        }
        label { display:block; font-size: 12px; color: var(--muted); margin-bottom: 6px; }
        input[type="number"], select, input[type="text"] {
            width: 100%;
            background: var(--chip);
            color: var(--ink);
            border: 1px solid var(--border);
            border-radius: 10px;
            padding: 10px 12px;
            outline: none;
        }
        input::placeholder { color: #6b7280; }
        input:focus, select:focus { border-color: var(--accent-2); box-shadow: 0 0 0 3px rgba(56,189,248,0.15); }
        .row { display:flex; gap: 10px; align-items:center; }
        .btn {
            appearance: none; border: 0; cursor: pointer; border-radius: 12px; padding: 12px 16px; font-weight: 600;
            background: linear-gradient(90deg, var(--accent), var(--accent-2)); color: #0b1220;
        }
        .btn:active { transform: translateY(1px); }
        .ghost { background: transparent; color: var(--ink); border: 1px solid var(--border); }
        .result { margin-top: 18px; padding: 16px; border: 1px dashed var(--accent-2); border-radius: 12px; background: rgba(2,132,199,0.08); }
        .kvs { display:grid; grid-template-columns: repeat(2, minmax(0,1fr)); gap:10px; margin-top:10px; }
        .kv { background: var(--chip); border:1px solid var(--border); border-radius: 10px; padding: 10px; font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace; }
        .pill { display:inline-block; padding:2px 8px; border-radius:999px; font-size:12px; margin-left:8px; border:1px solid var(--border); background: var(--chip); color: var(--muted); }
        .footer { margin-top: 18px; color: var(--muted); font-size: 12px; }
        .spacer { height: 6px; }
    </style>
</head>
<body>
  <div class="wrap">
    <div class="card">
      <h1>Unwind Fee Calculator</h1>
      <div class="sub">Enter DV01, direction, and rates; we’ll handle the rest.</div>
      <form method="post">
        <div class="field third">
          <label for="dv01">DV01</label>
          <input id="dv01" name="dv01" type="text" inputmode="decimal" placeholder="e.g. 12,345" value="{{ request.form.dv01 }}">
        </div>
        <div class="field third">
          <label for="direction">Client's original direction</label>
          <select id="direction" name="direction">
            <option value="pays" {% if request.form.direction == 'pays' %}selected{% endif %}>Pays fixed</option>
            <option value="receives" {% if request.form.direction == 'receives' %}selected{% endif %}>Receives fixed</option>
          </select>
        </div>
        <div class="field third">
          <label for="old_rate">Original fixed rate (%)</label>
          <input id="old_rate" name="old_rate" type="number" step="0.0001" placeholder="e.g. 2.3750" value="{{ request.form.old_rate }}">
        </div>
        <div class="field third">
          <label for="new_rate">Today's fixed rate (%)</label>
          <input id="new_rate" name="new_rate" type="number" step="0.0001" placeholder="e.g. 3.1450" value="{{ request.form.new_rate }}">
        </div>
        <div class="field" style="grid-column: span 12; display:flex; gap:10px;">
          <button type="submit" class="btn">Calculate</button>
          {% if result %}
          <button type="button" class="btn" onclick="copyResult()">Copy to Clipboard</button>
          {% endif %}
        </div>
      </form>

      {% if result %}
      <div class="result" id="resultBox">
        <div style="display:flex; justify-content:space-between; align-items:center;">
          <strong>Result</strong>
          <small class="pill">formatted</small>
        </div>
        <div class="spacer"></div>
        <pre style="margin:0; white-space:pre-wrap;">{{ result }}</pre>
      </div>
      {% endif %}

      <div class="footer">Pro tip: comma separators in DV01 are okay. We’ll handle it. • No pop-ups when copying — it just works.</div>
    </div>
  </div>

  <script>
    function copyResult() {
      var box = document.getElementById('resultBox');
      if (!box) return;
      var text = box.innerText;
      navigator.clipboard.writeText(text);
    }
  </script>
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