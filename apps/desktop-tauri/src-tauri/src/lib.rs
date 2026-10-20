mod engine;
use std::sync::{Arc, Mutex};
use tauri::Manager;
type Shared = Arc<Mutex<Option<engine::Engine>>>;
#[tauri::command]
async fn desktop(
    state: tauri::State<'_, Shared>,
    action: String,
    params: Option<serde_json::Value>,
) -> Result<serde_json::Value, String> {
    let state = state.inner().clone();
    tauri::async_runtime::spawn_blocking(move || {
        state
            .lock()
            .map_err(|_| "Application state is unavailable.")?
            .as_mut()
            .ok_or("Application is closing.")?
            .action(&action, params.unwrap_or(serde_json::json!({})))
    })
    .await
    .map_err(|_| "Background operation failed.".to_string())?
}
#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .setup(|app| {
            let dir = app.path().app_local_data_dir()?;
            #[cfg(debug_assertions)]
            let dir = std::env::var_os("FORGE_DESKTOP_TEST_DIR")
                .map(std::path::PathBuf::from)
                .unwrap_or(dir);
            let engine = engine::Engine::new(dir).map_err(std::io::Error::other)?;
            app.manage(Arc::new(Mutex::new(Some(engine))) as Shared);
            Ok(())
        })
        .invoke_handler(tauri::generate_handler![desktop])
        .build(tauri::generate_context!())
        .expect("Unable to initialize ForgeCoin Desktop")
        .run(|app, event| {
            if let tauri::RunEvent::Exit = event {
                if let Ok(mut state) = app.state::<Shared>().lock() {
                    state.take();
                }
            }
        });
}
