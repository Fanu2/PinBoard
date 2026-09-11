# 📌 PinBoard

### Your Personal Visual Library

> **Collect. Organize. Remember.**
>
> A simple, private, local-first Pinterest-style image organizer built with **Python, PySide6 and SQLite**.

PinBoard is designed for one purpose: **making your own collection of images easy to browse and useful later**.

It is not a social network, not a cloud service, and not another complicated productivity system.

It is simply your **personal visual reference shelf**.

---

## ✨ What PinBoard Does

PinBoard lets you point the application at folders containing your images and turn them into an easy-to-explore visual library.

Instead of repeatedly searching through Windows folders, you can:

- 🖼️ Browse images visually
- 📁 Import entire folders recursively
- 🔎 Search your collection
- ⭐ Mark important images as favorites
- 📚 Organize images into collections
- 🏷️ Add tags
- 📝 Add notes and descriptions
- 🔍 Open images in a larger viewer
- 🧱 Browse using a Pinterest-inspired masonry layout

And importantly:

### 🔒 Your original images stay where they are.

PinBoard stores a **catalogue of your images**, rather than creating another copy of your entire collection.

---

# 🎯 Why PinBoard?

A normal file browser is excellent for managing files.

But it is not always ideal for remembering **visual ideas**.

You may have folders containing:

- UI ideas
- screenshots
- software references
- diagrams
- wallpapers
- photographs
- travel ideas
- design inspiration
- interesting images
- technical references
- things you simply want to remember

PinBoard gives these images a visual home.

Think of it as:

```text
Windows folders
      │
      ▼
   PinBoard
      │
      ├── Visual browsing
      ├── Search
      ├── Collections
      ├── Tags
      ├── Favorites
      └── Notes
```

---

# 🖼️ Visual Gallery

PinBoard uses a Pinterest-inspired **masonry layout** so images can be viewed as a visual collection rather than a conventional file list.

```text
┌────────────┐   ┌───────┐   ┌─────────────┐
│            │   │       │   │             │
│            │   │ Image │   │             │
│   Image    │   │       │   │    Image    │
│            │   └───────┘   │             │
│            │   ┌────────┐  │             │
└────────────┘   │        │  └─────────────┘
                 │ Image  │  ┌────────────┐
                 │        │  │            │
                 └────────┘  │   Image    │
                             │            │
                             └────────────┘
```

The goal is to make browsing feel more like exploring a visual board.

---

# ⭐ Favorites

Important images can be marked as favorites.

For example:

```text
⭐ Useful PySide6 UI
⭐ Interesting software
⭐ Great dashboard design
⭐ Reference diagram
```

Favorites provide a quick way to create a personal shortlist without moving or copying files.

---

# 📚 Collections

Create collections that match the way you think about your images.

Examples:

```text
📚 Collections

💻 Software
🎨 Design Ideas
🐍 Python
🖥️ PySide6
📖 Reference
✈️ Travel
🏠 Home
💡 Ideas
```

An image can then be associated with a collection.

---

# 🏷️ Tags

Tags provide another layer of organization.

Example:

```text
Image: PySide6 Dashboard

Collection:
Software

Tags:
#python
#pyside6
#qt
#ui
#dashboard
```

Search can use these tags as well as filenames.

---

# 📝 Notes

Sometimes an image is useful because of an idea associated with it.

PinBoard allows you to keep a small note with the image.

For example:

> "Good idea for a future desktop application."

The image remains untouched; the note lives in PinBoard's catalogue.

---

# 🔎 Search

Search is designed to search beyond filenames.

You can search through:

- Image names
- Tags
- Notes
- Descriptions

For example:

```text
python
dashboard
travel
reference
pyside6
```

This turns the visual library into something you can actually retrieve later.

---

# 🔐 Local First

PinBoard is intentionally local.

There is:

- ❌ No account
- ❌ No cloud upload
- ❌ No subscription
- ❌ No advertising
- ❌ No required Internet connection

Your catalogue is stored locally using SQLite.

```text
%USERPROFILE%\.pinboard\pinboard.db
```

Thumbnail cache:

```text
%USERPROFILE%\.pinboard\thumbnails\
```

---

# 🛡️ Original Files Are Not Modified

PinBoard does **not** reorganize your folders.

It does not move your images.

It does not rename your images.

It does not replace your images.

Instead, it maintains a lightweight catalogue:

```text
Original image
      │
      └──────► PinBoard catalogue
                   │
                   ├── path
                   ├── favorite
                   ├── collection
                   ├── tags
                   ├── note
                   └── description
```

This makes PinBoard suitable for an existing image collection.

---

# 🧰 Technology

| Component | Technology |
|---|---|
| Language | Python |
| GUI | PySide6 |
| Database | SQLite |
| Image processing | Pillow |
| Platform | Windows / Python desktop |
| Architecture | Local-first |

The application intentionally avoids a large framework stack.

---

# 🚀 Installation

## 1. Install Python

Python 3.10 or newer is recommended.

## 2. Install dependencies

Open PowerShell:

```powershell
py -m pip install -r requirements.txt
```

## 3. Start PinBoard

```powershell
python pinboard.py
```

That's it.

---

# 📂 Importing Your Images

Start PinBoard and select:

```text
＋ Add Folder
```

Choose a folder.

PinBoard scans that folder recursively and adds supported images to its catalogue.

Supported formats include:

```text
.jpg
.jpeg
.png
.webp
.bmp
.gif
.tif
.tiff
```

You can import another folder later. Existing images are not duplicated in the catalogue.

---

# 🧠 Optional Advanced Tools

PinBoard also includes a small optional utility module:

```text
pinboard_tools.py
```

It provides groundwork for:

- SHA-256 exact duplicate detection
- Perceptual image hashing
- Optional local AI image descriptions through Ollama

These features are **optional** and are not required for normal PinBoard use.

The application remains useful without AI.

---

# 🗃️ Data Model

The catalogue contains information such as:

```text
Image
 ├── Path
 ├── Name
 ├── Favorite
 ├── Collection
 ├── Tags
 ├── Note
 ├── Description
 ├── SHA-256
 ├── Perceptual Hash
 └── Added Date
```

This gives PinBoard room to grow without requiring a complicated backend.

---

# 🛣️ Project Philosophy

PinBoard should remain **small and useful**.

The goal is not to reproduce every feature of Pinterest.

The goal is to create a personal tool that answers one simple question:

> **"Where was that image or idea I wanted to remember?"**

Features should therefore be added only when they provide genuine value.

---

# 🔮 Possible Future Ideas

The following are possibilities rather than commitments:

- Drag-and-drop importing
- Better variable-height masonry cards
- Image metadata / EXIF browser
- Clipboard image capture
- Duplicate cleanup workflow
- Similar-image search
- Image rotation and cropping
- Local AI auto-tagging
- Local AI image descriptions
- Obsidian export
- Markdown export
- Integration with other personal knowledge tools

The project can remain perfectly useful without implementing all of these.

---

# 📌 Project Status

**PinBoard V0.5 — Stable Personal Edition**

The application has reached a practical feature level suitable for everyday personal use.

The current priority is **stability and usefulness rather than feature accumulation**.

---

# 🗂️ Project Structure

```text
PinBoard_V0.5/
│
├── pinboard.py
├── pinboard_tools.py
├── requirements.txt
└── README.md
```

Runtime data is kept outside the project:

```text
%USERPROFILE%\.pinboard\
│
├── pinboard.db
└── thumbnails\
```

This keeps the source directory clean.

---

# 💡 The Idea Behind PinBoard

There are many powerful applications for managing files, notes and knowledge.

PinBoard occupies a smaller space:

**visual memory.**

It is a place for the images that are useful because you saw them.

```text
See something interesting
          ↓
       Pin it
          ↓
      Organize it
          ↓
      Find it later
          ↓
       Use the idea
```

Simple.

Private.

Local.

Useful.

---

## 📜 License

Choose a license when publishing the repository.

---

### 📌 PinBoard

**A personal visual library — not another social network.**
