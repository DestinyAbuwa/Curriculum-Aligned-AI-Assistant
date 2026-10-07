# UICOMP Curriculum AI Assistant

A chat-style web page for the UICOMP medical-education assistant. It runs on your own computer in a browser. There is no backend yet, so nothing replies to messages.

## What you need

- **Node.js 20.19 or newer** (22.12+ also works). It was built and tested with Node 24.
  Download it from https://nodejs.org, then check with `node --version`.
- An internet connection the first time, to download the packages (and later for the Google font).

## Run it

1. Open a terminal in this folder (the one that contains `package.json`).
2. Install the packages. You only need to do this once:

   ```
   npm install
   ```

3. Start the app:

   ```
   npm run dev
   ```

4. Open **http://localhost:5173** in your browser.
5. Press `Ctrl + C` in the terminal to stop it.

While it is running, saving a change to `src/App.jsx` updates the page automatically.

## Other commands

| Command | What it does |
| --- | --- |
| `npm run build` | Checks everything compiles and writes a finished copy to a `dist` folder |
| `npm run preview` | Serves that `dist` copy so you can look at it (run `npm run build` first) |

## If something goes wrong

- **PowerShell says "running scripts is disabled":** use Command Prompt (`cmd`) instead, or type `npm.cmd install` and `npm.cmd run dev`.
- **Port 5173 is busy:** Vite picks the next free port and prints the address in the terminal. Use that one.


## Good to know

- Chats are kept in memory only. Refreshing the page clears them.
- It is a desktop-width layout. There is no phone or small-window layout for now.

