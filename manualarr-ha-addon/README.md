# Manualarr Home Assistant Add-on Repository

Product manual library with AI search for Home Assistant.

## Installation

1. **Copy the URL** of this repository.
2. Login to your **Home Assistant** instance.
3. Go to **Settings** > **Add-ons** > **Add-on Store**.
4. Click the **three dots** (menu) in the top right corner and select **Repositories**.
5. Paste the repository URL into the "Add" field and click **Add**.
6. Close the dialog.
7. Scroll down or search for **Manualarr**.
8. Click on the add-on card and click **Install**.
9. Once installed, start the add-on.
10. Enable **Show in sidebar** to easily access the interface.

## AI Assistant Integration

To allow Home Assistant's conversation agents (like OpenAI, Google Gemini, or local LLMs) to search your manuals:

1. Go to the `assistant-configs` directory in this repository.
2. Select the configuration template that matches your assistant setup.
3. Follow the instructions in the template to register the `search_manuals` tool.

## Features

- **Store Manuals**: Upload PDF manuals via the web interface.
- **Search**: Full-text search through your manual library.
- **AI Context**: Provides relevant manual snippets to LLMs to answer questions like "How do I change the filter?".
- **Ingress Support**: Securely integrated into the Home Assistant sidebar.

## Support

For issues, please open a ticket in the repository issue tracker.