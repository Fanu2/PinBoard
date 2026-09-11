from pathlib import Path
import sqlite3, json, urllib.request

DB = Path.home()/".pinboard"/"pinboard.db"

def duplicate_groups():
    con=sqlite3.connect(DB)
    return con.execute("""SELECT sha256, GROUP_CONCAT(path,'\n') FROM images
                          WHERE sha256<>'' GROUP BY sha256 HAVING COUNT(*)>1""").fetchall()

def ollama_describe(image_path, model="llava"):
    """Optional helper. Requires an Ollama vision model and local Ollama service."""
    import base64
    data=base64.b64encode(Path(image_path).read_bytes()).decode()
    payload=json.dumps({"model":model,"prompt":"Describe this image briefly for a personal visual library.","images":[data],"stream":False}).encode()
    req=urllib.request.Request("http://127.0.0.1:11434/api/generate",data=payload,
                               headers={"Content-Type":"application/json"})
    with urllib.request.urlopen(req, timeout=120) as r:
        return json.loads(r.read())["response"]

if __name__=="__main__":
    groups=duplicate_groups()
    print(f"Exact duplicate groups: {len(groups)}")
    for _,paths in groups:
        print("\n---\n"+paths)
