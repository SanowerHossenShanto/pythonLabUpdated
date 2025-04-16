# QR Code Generator

## Overview
This **QR Code Generator** is a simple Python application built using the **Tkinter** library, allowing users to generate QR codes from text or URLs. It provides customization options, such as adjusting QR code colors, adding logos, saving history, and much more.

### Key Features:
- **Generate QR Codes**: Create QR codes from URLs or text input.
- **Customizable Appearance**: Choose the foreground (QR color) and background colors for your QR code.
- **Logo Insertion**: Add logos to your QR codes.
- **History Tracking**: Save and view the last 10 generated QR codes.
- **Search History**: Search QR code history by file name.
- **Clipboard Support**: Copy generated QR codes to the clipboard for easy sharing.
- **Dark Mode**: Toggle between light and dark themes.
- **Reset Function**: Reset the application to its initial state.
- **History Export**: Save your QR code generation history to a CSV file for future reference.

## Technologies Used:
- **Tkinter**: For building the graphical user interface (GUI).
- **qrcode**: Python library for generating QR codes.
- **Pillow (PIL)**: For handling images (QR code generation, logo insertion).
- **pyperclip**: For clipboard functionality (copy QR codes to clipboard).
- **cryptography**: For encryption (Fernet).
- **csv**: For saving QR code history.

## Installation

To run this project, you need to install the following libraries:

```bash
pip install qrcode[pil]
pip install pyperclip
pip install pillow
pip install cryptography
