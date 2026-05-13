use std::io::{BufRead, BufReader};
use std::process::{Child, Command, Stdio};
use std::sync::Mutex;
use tauri::{Manager, State};

struct Sidecar {
    port: u16,
    child: Child,
}

struct SidecarState(Mutex<Option<Sidecar>>);

#[tauri::command]
fn get_backend_port(state: State<'_, SidecarState>) -> u16 {
    state
        .0
        .lock()
        .unwrap()
        .as_ref()
        .map(|s| s.port)
        .unwrap_or(0)
}

fn spawn_sidecar() -> Result<Sidecar, String> {
    let backend_dir = std::path::PathBuf::from(env!("CARGO_MANIFEST_DIR"))
        .parent()
        .ok_or("no parent dir")?
        .join("backend");

    let calibre_library =
        std::env::var("NIGHTSTAND_CALIBRE_LIBRARY").unwrap_or_else(|_| {
            let home = std::env::var("HOME").unwrap_or_default();
            format!("{home}/Calibre Library")
        });

    let mut child = Command::new("uv")
        .args(["run", "python", "-m", "nightstand.main", "--port", "0"])
        .current_dir(&backend_dir)
        .env("NIGHTSTAND_CALIBRE_LIBRARY", calibre_library)
        .stdout(Stdio::piped())
        .stderr(Stdio::inherit())
        .spawn()
        .map_err(|e| format!("failed to spawn sidecar: {e}"))?;

    let stdout = child.stdout.take().ok_or("no stdout on child")?;
    let mut reader = BufReader::new(stdout);
    let mut port: u16 = 0;

    loop {
        let mut line = String::new();
        match reader.read_line(&mut line) {
            Ok(0) => break, // EOF before port was announced
            Ok(_) => {
                if let Some(p) = line.trim().strip_prefix("NIGHTSTAND_PORT=") {
                    port = p.parse().map_err(|e| format!("bad port value: {e}"))?;
                    break;
                }
            }
            Err(e) => return Err(format!("reading sidecar stdout: {e}")),
        }
    }

    // Drain remaining stdout in background to prevent SIGPIPE on the child.
    std::thread::spawn(move || {
        let mut buf = String::new();
        while reader.read_line(&mut buf).unwrap_or(0) > 0 {
            buf.clear();
        }
    });

    if port == 0 {
        return Err("sidecar did not report a port".into());
    }

    Ok(Sidecar { port, child })
}

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .manage(SidecarState(Mutex::new(None)))
        .setup(|app| {
            let handle = app.handle().clone();
            match spawn_sidecar() {
                Ok(sidecar) => {
                    *handle.state::<SidecarState>().0.lock().unwrap() = Some(sidecar);
                }
                Err(e) => eprintln!("Sidecar spawn failed: {e}"),
            }
            Ok(())
        })
        .on_window_event(|window, event| {
            if let tauri::WindowEvent::Destroyed = event {
                let killed = {
                    let state = window.state::<SidecarState>();
                    let mut guard = state.0.lock().unwrap();
                    guard.take()
                };
                if let Some(mut sidecar) = killed {
                    let _ = sidecar.child.kill();
                }
            }
        })
        .invoke_handler(tauri::generate_handler![get_backend_port])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
