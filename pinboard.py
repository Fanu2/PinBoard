import sys, sqlite3, hashlib, json, urllib.request, urllib.error
from pathlib import Path
from datetime import datetime

from PySide6.QtCore import Qt, QSize, Signal, QRect, QPoint
from PySide6.QtGui import QPixmap, QImage, QPainter, QFont, QColor
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QPushButton, QFileDialog, QLineEdit, QMessageBox, QScrollArea,
    QFrame, QDialog, QDialogButtonBox, QInputDialog, QTextEdit, QComboBox,
    QSplitter, QListWidget, QListWidgetItem, QFormLayout, QCheckBox
)

try:
    from PIL import Image, ImageStat
except ImportError:
    Image = None

APP_DIR = Path.home() / ".pinboard"
DB_PATH = APP_DIR / "pinboard.db"
THUMB_DIR = APP_DIR / "thumbnails"
SUPPORTED = {".jpg", ".jpeg", ".png", ".webp", ".bmp", ".gif", ".tif", ".tiff"}

STYLE = """
QMainWindow, QWidget { background:#f4f5f7; color:#202124; }
QLineEdit, QTextEdit, QComboBox { background:white; border:1px solid #d7d9de; border-radius:10px; padding:9px; }
QPushButton { background:white; border:1px solid #d7d9de; border-radius:9px; padding:8px 13px; }
QPushButton:hover { background:#eceff3; }
QFrame#Sidebar, QFrame#Card, QFrame#Panel { background:white; border:1px solid #e0e2e6; border-radius:12px; }
QLabel#Title { font-size:21px; font-weight:700; }
QLabel#Muted { color:#6d737c; }
QLabel#CardTitle { font-weight:600; }
"""

def db():
    APP_DIR.mkdir(exist_ok=True)
    THUMB_DIR.mkdir(exist_ok=True)
    con = sqlite3.connect(DB_PATH)
    # Create the current schema for a fresh installation.
    con.execute("""CREATE TABLE IF NOT EXISTS images(
        id INTEGER PRIMARY KEY, path TEXT UNIQUE NOT NULL, name TEXT NOT NULL,
        favorite INTEGER NOT NULL DEFAULT 0, collection TEXT DEFAULT '',
        tags TEXT DEFAULT '', note TEXT DEFAULT '', description TEXT DEFAULT '',
        sha256 TEXT DEFAULT '', phash TEXT DEFAULT '', added TEXT DEFAULT CURRENT_TIMESTAMP
    )""")

    # V0.1 compatibility: an existing PinBoard database may only contain
    # id/path/name/favorite/added. Add newer columns without destroying data.
    existing = {row[1] for row in con.execute("PRAGMA table_info(images)").fetchall()}
    migrations = {
        "collection": "ALTER TABLE images ADD COLUMN collection TEXT DEFAULT ''",
        "tags": "ALTER TABLE images ADD COLUMN tags TEXT DEFAULT ''",
        "note": "ALTER TABLE images ADD COLUMN note TEXT DEFAULT ''",
        "description": "ALTER TABLE images ADD COLUMN description TEXT DEFAULT ''",
        "sha256": "ALTER TABLE images ADD COLUMN sha256 TEXT DEFAULT ''",
        "phash": "ALTER TABLE images ADD COLUMN phash TEXT DEFAULT ''",
    }
    for column, statement in migrations.items():
        if column not in existing:
            con.execute(statement)

    con.execute("""CREATE TABLE IF NOT EXISTS collections(
        id INTEGER PRIMARY KEY, name TEXT UNIQUE NOT NULL
    )""")
    con.commit()
    return con

def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024*1024), b""):
            h.update(chunk)
    return h.hexdigest()

def image_phash(path):
    if Image is None:
        return ""
    try:
        im = Image.open(path).convert("L").resize((16,16))
        pixels = list(im.getdata())
        avg = sum(pixels) / len(pixels)
        return "".join("1" if p >= avg else "0" for p in pixels)
    except Exception:
        return ""

def thumb_path(path):
    key = hashlib.sha1(str(Path(path).resolve()).encode()).hexdigest()
    return THUMB_DIR / f"{key}.jpg"

def make_thumbnail(path, size=420):
    out = thumb_path(path)
    try:
        if out.exists() and out.stat().st_mtime >= Path(path).stat().st_mtime:
            return str(out)
        if Image:
            im = Image.open(path).convert("RGB")
            im.thumbnail((size, size))
            im.save(out, "JPEG", quality=88)
            return str(out)
    except Exception:
        pass
    return path

def dominant_color(path):
    if not Image:
        return ""
    try:
        im = Image.open(path).convert("RGB").resize((1,1))
        r,g,b = im.getpixel((0,0))
        return f"#{r:02x}{g:02x}{b:02x}"
    except Exception:
        return ""

def image_metadata(path):
    result = {}
    try:
        if Image:
            im = Image.open(path)
            result["Format"] = im.format or "Unknown"
            result["Dimensions"] = f"{im.width} × {im.height}"
            result["Mode"] = im.mode
            result["File size"] = f"{Path(path).stat().st_size/1024:.1f} KB"
            result["Modified"] = datetime.fromtimestamp(Path(path).stat().st_mtime).strftime("%Y-%m-%d %H:%M")
            exif = im.getexif()
            if exif:
                result["EXIF fields"] = str(len(exif))
    except Exception:
        pass
    return result

class MasonryWidget(QWidget):
    card_width = 245
    gap = 12
    def __init__(self):
        super().__init__()
        self.cards = []
        self.setMinimumWidth(700)

    def set_cards(self, cards):
        for c in self.cards:
            c.setParent(None)
            c.deleteLater()
        self.cards = cards
        for c in cards:
            c.setParent(self)
            c.show()
        self.relayout()

    def resizeEvent(self, event):
        self.relayout()
        super().resizeEvent(event)

    def relayout(self):
        if not self.cards:
            self.setMinimumHeight(300)
            return
        cols = max(1, self.width() // (self.card_width + self.gap))
        heights = [8] * cols
        for card in self.cards:
            col = min(range(cols), key=lambda i: heights[i])
            x = 8 + col * (self.card_width + self.gap)
            y = heights[col]
            card.setGeometry(QRect(x, y, self.card_width, card.sizeHint().height()))
            heights[col] += card.sizeHint().height() + self.gap
        self.setMinimumHeight(max(400, max(heights) + 10))

class Viewer(QDialog):
    def __init__(self, path, parent=None):
        super().__init__(parent)
        self.setWindowTitle(Path(path).name)
        self.resize(1100, 800)
        layout = QVBoxLayout(self)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        label = QLabel(alignment=Qt.AlignmentFlag.AlignCenter)
        pix = QPixmap(path)
        if pix.isNull():
            label.setText("Unable to load image.")
        else:
            label.setPixmap(pix.scaled(1020, 700, Qt.AspectRatioMode.KeepAspectRatio,
                                       Qt.TransformationMode.SmoothTransformation))
        scroll.setWidget(label)
        layout.addWidget(scroll)
        b = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        b.rejected.connect(self.reject)
        layout.addWidget(b)

class Editor(QDialog):
    saved = Signal()
    def __init__(self, row, collections, parent=None):
        super().__init__(parent)
        self.row = row
        self.setWindowTitle("Pin details")
        self.resize(560, 480)
        layout = QVBoxLayout(self)
        form = QFormLayout()
        self.collection = QComboBox()
        self.collection.addItem("")
        self.collection.addItems(collections)
        if row[4]: self.collection.setCurrentText(row[4])
        self.tags = QLineEdit(row[5] or "")
        self.note = QTextEdit(row[6] or "")
        self.description = QTextEdit(row[7] or "")
        form.addRow("Collection:", self.collection)
        form.addRow("Tags:", self.tags)
        form.addRow("Note:", self.note)
        form.addRow("Description:", self.description)
        layout.addLayout(form)
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Save |
                                   QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.save)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def save(self):
        self.parent().con.execute("""UPDATE images SET collection=?,tags=?,note=?,description=? WHERE id=?""",
            (self.collection.currentText(), self.tags.text(), self.note.toPlainText(),
             self.description.toPlainText(), self.row[0]))
        self.parent().con.commit()
        self.saved.emit()
        self.accept()

class Card(QFrame):
    def __init__(self, row, owner):
        super().__init__()
        self.row, self.owner = row, owner
        self.setObjectName("Card")
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setMinimumHeight(250)
        layout = QVBoxLayout(self); layout.setContentsMargins(8,8,8,8)
        self.preview = QLabel(alignment=Qt.AlignmentFlag.AlignCenter)
        self.preview.setMinimumHeight(175)
        source = make_thumbnail(row[1])
        pix = QPixmap(source)
        if not pix.isNull():
            self.preview.setPixmap(pix.scaled(225, 260, Qt.AspectRatioMode.KeepAspectRatio,
                                              Qt.TransformationMode.SmoothTransformation))
        layout.addWidget(self.preview)
        title = QLabel(row[2]); title.setObjectName("CardTitle"); title.setWordWrap(True)
        layout.addWidget(title)
        info = QLabel((row[4] or "") + (("  #" + " #".join(t.strip() for t in row[5].split(",") if t.strip())) if row[5] else ""))
        info.setObjectName("Muted"); info.setWordWrap(True); layout.addWidget(info)
        bar = QHBoxLayout()
        fav = QPushButton("★" if row[3] else "☆"); fav.setFixedWidth(40)
        fav.clicked.connect(lambda: owner.toggle_favorite(row[0]))
        bar.addWidget(fav)
        edit = QPushButton("Edit"); edit.clicked.connect(lambda: owner.edit_pin(row))
        bar.addWidget(edit)
        bar.addStretch()
        layout.addLayout(bar)

    def mousePressEvent(self, e):
        if e.button() == Qt.MouseButton.LeftButton:
            Viewer(self.row[1], self.window()).exec()
        super().mousePressEvent(e)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.con = db()
        self.favorite_only = False
        self.collection_filter = ""
        self.setWindowTitle("PinBoard — Personal Visual Library")
        self.resize(1400, 900)
        self.build_ui()
        self.refresh()

    def build_ui(self):
        root = QWidget(); outer = QHBoxLayout(root); outer.setContentsMargins(12,12,12,12)
        side = QFrame(); side.setObjectName("Sidebar"); side.setFixedWidth(235)
        sl = QVBoxLayout(side)
        t=QLabel("📌 PinBoard"); t.setObjectName("Title"); sl.addWidget(t)
        m=QLabel("Personal Visual Library"); m.setObjectName("Muted"); sl.addWidget(m); sl.addSpacing(15)
        b=QPushButton("＋ Add Folder"); b.clicked.connect(self.add_folder); sl.addWidget(b)
        b=QPushButton("🖼 All Images"); b.clicked.connect(self.show_all); sl.addWidget(b)
        b=QPushButton("★ Favorites"); b.clicked.connect(self.show_favorites); sl.addWidget(b)
        b=QPushButton("＋ Collection"); b.clicked.connect(self.new_collection); sl.addWidget(b)
        sl.addSpacing(12); sl.addWidget(QLabel("COLLECTIONS"))
        self.collections_list = QListWidget(); self.collections_list.itemClicked.connect(self.collection_clicked)
        sl.addWidget(self.collections_list)
        sl.addStretch()
        self.stats=QLabel(); self.stats.setObjectName("Muted"); sl.addWidget(self.stats)
        outer.addWidget(side)

        content=QWidget(); cl=QVBoxLayout(content)
        header=QHBoxLayout(); h=QLabel("My Visual Library"); h.setObjectName("Title"); header.addWidget(h); header.addStretch()
        self.search=QLineEdit(); self.search.setPlaceholderText("Search names, tags, notes, descriptions…"); self.search.setMaximumWidth(470)
        self.search.textChanged.connect(self.refresh); header.addWidget(self.search)
        cl.addLayout(header)
        self.gallery=MasonryWidget()
        scroll=QScrollArea(); scroll.setWidgetResizable(True); scroll.setWidget(self.gallery)
        cl.addWidget(scroll)
        outer.addWidget(content,1)
        self.setCentralWidget(root)

    def load_collections(self):
        self.collections_list.clear()
        for (name,) in self.con.execute("SELECT name FROM collections ORDER BY name"):
            self.collections_list.addItem(name)

    def show_all(self):
        self.favorite_only=False; self.collection_filter=""; self.refresh()
    def show_favorites(self):
        self.favorite_only=True; self.collection_filter=""; self.refresh()
    def collection_clicked(self, item):
        self.favorite_only=False; self.collection_filter=item.text(); self.refresh()

    def new_collection(self):
        name, ok=QInputDialog.getText(self,"New collection","Collection name:")
        if ok and name.strip():
            try:
                self.con.execute("INSERT OR IGNORE INTO collections(name) VALUES(?)",(name.strip(),)); self.con.commit()
            except sqlite3.Error: pass
            self.load_collections()

    def add_folder(self):
        folder=QFileDialog.getExistingDirectory(self,"Select image folder")
        if not folder: return
        added=0
        for p in Path(folder).rglob("*"):
            if p.is_file() and p.suffix.lower() in SUPPORTED:
                try:
                    before=self.con.total_changes
                    self.con.execute("""INSERT OR IGNORE INTO images(path,name,sha256,phash) VALUES(?,?,?,?)""",
                                     (str(p.resolve()),p.name,sha256_file(p),image_phash(p)))
                    added += self.con.total_changes-before
                except Exception: pass
        self.con.commit(); self.load_collections(); self.refresh()
        QMessageBox.information(self,"Import complete",f"Folder scanned.\nNew images added: {added}")

    def toggle_favorite(self, image_id):
        self.con.execute("UPDATE images SET favorite=1-favorite WHERE id=?",(image_id,)); self.con.commit(); self.refresh()

    def edit_pin(self,row):
        collections=[x[0] for x in self.con.execute("SELECT name FROM collections ORDER BY name")]
        d=Editor(row,collections,self); d.saved.connect(self.refresh); d.exec()

    def refresh(self):
        term=self.search.text().strip().lower()
        q="""SELECT id,path,name,favorite,collection,tags,note,description FROM images WHERE 1=1"""
        args=[]
        if self.favorite_only: q+=" AND favorite=1"
        if self.collection_filter: q+=" AND collection=?"; args.append(self.collection_filter)
        if term:
            q+=" AND lower(name||' '||coalesce(tags,'')||' '||coalesce(note,'')||' '||coalesce(description,'')) LIKE ?"
            args.append("%"+term+"%")
        q+=" ORDER BY id DESC"
        rows=self.con.execute(q,args).fetchall()
        self.gallery.set_cards([Card(r,self) for r in rows])
        total=self.con.execute("SELECT COUNT(*) FROM images").fetchone()[0]
        self.stats.setText(f"{len(rows)} shown\n{total} total images")
        self.load_collections()

def main():
    app=QApplication(sys.argv); app.setStyleSheet(STYLE)
    win=MainWindow(); win.show(); sys.exit(app.exec())

if __name__=="__main__":
    main()
