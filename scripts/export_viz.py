# scripts/export_viz.py
import json
from db import get_connection

def export_html(output_path="data/bloodline_viz.html"):
    conn = get_connection()
    albums = conn.execute("SELECT id, artist, title FROM albums").fetchall()
    artists = conn.execute("SELECT id, name, depth FROM artists").fetchall()
    edges = conn.execute("""
        SELECT source_album_id, source_artist_id, target_artist_id FROM edges
    """).fetchall()
    conn.close()

    nodes = []
    for row in albums:
        nodes.append({
            "id": f"a_{row['id']}",
            "label": f"{row['artist']}\n{row['title']}",
            "shape": "box",
            "color": {"background": "#ffffff", "border": "#000000"},
            "font": {"size": 11, "color": "#000000"}
        })
    for row in artists:
        bg = "#333333" if row["depth"] == 1 else "#666666"
        nodes.append({
            "id": f"ar_{row['id']}",
            "label": row["name"],
            "shape": "ellipse",
            "color": {"background": bg, "border": "#000000"},
            "font": {"size": 10, "color": "#ffffff"}
        })

    links = []
    for row in edges:
        source = f"a_{row['source_album_id']}" if row["source_album_id"] else f"ar_{row['source_artist_id']}"
        target = f"ar_{row['target_artist_id']}"
        links.append({"from": source, "to": target})

    html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>Bloodline — influence graph</title>
<script src="https://unpkg.com/vis-network/standalone/umd/vis-network.min.js"></script>
<style>
  body {{ margin: 0; background: #111; }}
  #graph {{ width: 100vw; height: 100vh; }}
</style>
</head>
<body>
<div id="graph"></div>
<script>
  const nodes = new vis.DataSet({json.dumps(nodes, ensure_ascii=False)});
  const edges = new vis.DataSet({json.dumps(links, ensure_ascii=False)});
  const container = document.getElementById("graph");
  const network = new vis.Network(container, {{ nodes, edges }}, {{
    physics: {{
      solver: "forceAtlas2Based",
      forceAtlas2Based: {{ gravitationalConstant: -80, springLength: 120 }},
      stabilization: {{ iterations: 200 }}
    }},
    edges: {{
      arrows: "to",
      color: {{ color: "#444", highlight: "#fff" }},
      smooth: {{ type: "continuous" }}
    }},
    interaction: {{ hover: true, tooltipDelay: 100 }}
  }});
</script>
</body>
</html>"""

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"Exported to {output_path}")
    print(f"  Nodes: {len(nodes)}, Edges: {len(links)}")

if __name__ == "__main__":
    export_html()
