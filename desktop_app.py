import threading
import time
import webbrowser

import uvicorn


def run_server() -> None:
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=False)


def main() -> None:
    thread = threading.Thread(target=run_server, daemon=True)
    thread.start()
    time.sleep(1.2)
    webbrowser.open("http://127.0.0.1:8000")
    print("Desktop-like mode started. Close with Ctrl+C.")
    thread.join()


if __name__ == "__main__":
    main()
