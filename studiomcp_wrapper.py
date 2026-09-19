import os
import sys
import json
import subprocess
import threading


def find_studio_mcp():
    # 1. Check command line arguments if provided
    if len(sys.argv) > 1 and os.path.isfile(sys.argv[1]):
        return sys.argv[1]

    is_windows = sys.platform == "win32"
    is_mac = sys.platform == "darwin"
    
    # dynamic define StudioMCP
    exe_name = "StudioMCP.exe" if is_windows else "StudioMCP"

    if is_windows:
        # 2. Check Windows Registry
        try:
            import winreg

            with winreg.OpenKey(
                winreg.HKEY_CURRENT_USER, r"Software\Roblox\RobloxStudio"
            ) as key:
                content_folder, _ = winreg.QueryValueEx(key, "ContentFolder")
                parent_dir = os.path.dirname(os.path.normpath(content_folder))
                exe_path = os.path.join(parent_dir, exe_name)
                if os.path.isfile(exe_path):
                    return exe_path
        except Exception:
            pass

        # 3. Check AppData Local Roblox Versions folder (pick latest modified)
        local_app_data = os.environ.get("LOCALAPPDATA", "")
        if local_app_data:
            versions_dir = os.path.join(local_app_data, "Roblox", "Versions")
            if os.path.isdir(versions_dir):
                candidates = []
                for entry in os.listdir(versions_dir):
                    full_entry = os.path.join(versions_dir, entry)
                    if os.path.isdir(full_entry):
                        exe_path = os.path.join(full_entry, exe_name)
                        if os.path.isfile(exe_path):
                            candidates.append((os.path.getmtime(exe_path), exe_path))
                if candidates:
                    candidates.sort(key=lambda x: x[0], reverse=True)
                    return candidates[0][1]

    elif is_mac:
        # check normal Application directory of macOS
        mac_paths = [
            "/Applications/RobloxStudio.app/Contents/MacOS/StudioMCP",
            os.path.expanduser("~/Applications/RobloxStudio.app/Contents/MacOS/StudioMCP")
        ]
        
        for path in mac_paths:
            if os.path.isfile(path):
                return path

        # check Library directory if a Roblox app store "Versions"
        versions_dir = os.path.expanduser("~/Library/Roblox/Versions")
        if os.path.isdir(versions_dir):
            candidates = []
            for entry in os.listdir(versions_dir):
                full_entry = os.path.join(versions_dir, entry)
                if os.path.isdir(full_entry):
                    exe_path = os.path.join(full_entry, exe_name)
                    if os.path.isfile(exe_path):
                        candidates.append((os.path.getmtime(exe_path), exe_path))
            if candidates:
                candidates.sort(key=lambda x: x[0], reverse=True)
                return candidates[0][1]

    return None


def pump(src, dst):
    try:
        for line in iter(src.readline, ""):
            if not line:
                break
            dst.write(line)
            dst.flush()
    except Exception:
        pass


def main():
    studio_path = find_studio_mcp()
    if not studio_path or not os.path.isfile(studio_path):
        sys.stderr.write("Error: Could not locate StudioMCP on this system.\n")
        sys.stderr.flush()
        sys.exit(1)

    # Reconfigure stdin/stdout to utf-8 if possible
    if hasattr(sys.stdin, "reconfigure"):
        sys.stdin.reconfigure(encoding="utf-8")
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    proc = subprocess.Popen(
        [studio_path],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        bufsize=1,
    )

    threading.Thread(target=pump, args=(proc.stdout, sys.stdout), daemon=True).start()
    threading.Thread(target=pump, args=(proc.stderr, sys.stderr), daemon=True).start()

    try:
        for line in sys.stdin:
            line_str = line.strip()
            if not line_str:
                continue

            try:
                msg = json.loads(line_str)
                # Intercept non-standard discovery probes sent before MCP initialize
                if isinstance(msg, dict) and msg.get("method") == "server/discover":
                    resp = {
                        "jsonrpc": "2.0",
                        "id": msg.get("id"),
                        "error": {
                            "code": -32601,
                            "message": "Method not found",
                        },
                    }
                    sys.stdout.write(json.dumps(resp) + "\n")
                    sys.stdout.flush()
                    continue
            except Exception:
                pass

            if proc.poll() is not None:
                break

            proc.stdin.write(line_str + "\n")
            proc.stdin.flush()

    except (KeyboardInterrupt, BrokenPipeError):
        pass
    finally:
        try:
            if proc.stdin:
                proc.stdin.close()
        except Exception:
            pass
        try:
            proc.wait(timeout=3)
        except Exception:
            try:
                proc.terminate()
            except Exception:
                pass


if __name__ == "__main__":
    main()
