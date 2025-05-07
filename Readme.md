# BitTorrent-Based File Sharing System

This project simulates a basic BitTorrent system using Python for peer-to-peer (P2P) file sharing across devices on the same Wi-Fi network.

> 🚧 Project is still under development.

## 📂 Folder Structure

- `Internet/`: Internet server – stores `.torrent` files to distribute
- `tracker.py`: Central tracker – manages peers and their file info
- `node.py`: Peer program – uploads/downloads files
- `node1` to `node6/`: Example peer folders containing shared files
- `gen_file.py`: (optional) Generates file/torrent for testing

## 🔧 How It Works

- `Internet` server: Saves `.torrent` files that are shared with peers.
- `tracker`: Keeps track of which peers are seeding or leeching files.
- Each peer (node) runs its own `node.py` and points to a shared folder with the file they want to offer.

## 🚀 How to Run

> ⚠️ Make sure all devices are on the **same Wi-Fi network**.

### Step-by-step

1. On the **main server machine**:
    - Run the internet server first:
      ```bash
      cd Internet
      python internet.py
      ```
    - Then run the tracker:
      ```bash
      python tracker.py
      ```

2. On **each peer machine**:
    - Create a folder (e.g., `node1`, `node2`, ...) and place your file or folder inside.
    - Copy `node.py` into that folder.
    - Run the peer node:
      ```bash
      python node.py
      ```

## ✅ Features

- Upload and download files via `.torrent` protocol
- Peer discovery via tracker
- Simple file sharing with multiple nodes

## 📌 Notes

- Use folders `node1` to `node6` as examples for different peers.
- Files `read.py`, `tr.py`, `t.py` are test or legacy versions (optional).

## 🧑 Author

- Developed by [hungyle123](https://github.com/hungyle123)

---

More features and improvements are being added soon.
