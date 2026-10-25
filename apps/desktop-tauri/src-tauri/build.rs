fn main() {
    if std::env::var("CARGO_CFG_TARGET_OS").as_deref() == Ok("windows") {
        let root = std::path::PathBuf::from(std::env::var("CARGO_MANIFEST_DIR").unwrap());
        let audit = root.join("../../../tools/stage_windows_sidecars.py");
        println!("cargo:rerun-if-changed={}", audit.display());
        println!("cargo:rerun-if-changed=binaries");
        assert_eq!(
            std::env::var("TARGET").as_deref(),
            Ok("x86_64-pc-windows-msvc"),
            "No reviewed sidecars for this Windows target"
        );
        let result = std::process::Command::new("python")
            .arg(audit)
            .arg("--destination")
            .arg(root.join("binaries"))
            .status()
            .expect("Python is required for sidecar digest review");
        assert!(result.success(), "Unreviewed or missing Windows sidecars");
    }
    tauri_build::build()
}
