#!/usr/bin/env bash
set -euo pipefail

SERVICE_NAME="camera_app"
SERVICE_FILE="/etc/systemd/system/${SERVICE_NAME}.service"

# ---------- Detect paths ----------

# Directory of this script (repo root)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

APP_FILE="${SCRIPT_DIR}/camera_app.py"

# Check that camera_app.py exists
if [[ ! -f "${APP_FILE}" ]]; then
  echo "ERROR: ${APP_FILE} not found."
  echo "Make sure camera_app.py is in the same directory as this script."
  exit 1
fi

# Python binary
PYTHON_BIN="$(command -v python3 || true)"
if [[ -z "${PYTHON_BIN}" ]]; then
  echo "ERROR: python3 not found in PATH."
  exit 1
fi

# Must be run as root (e.g. sudo ./setup_camera_service.sh)
if [[ "${EUID}" -ne 0 ]]; then
  echo "Please run this script with sudo:"
  echo "  sudo $0"
  exit 1
fi

# Figure out which user should run the service:
# - If run via sudo, prefer SUDO_USER
# - Otherwise, fallback to current user
if [[ -n "${SUDO_USER-}" && "${SUDO_USER}" != "root" ]]; then
  RUN_USER="${SUDO_USER}"
  RUN_HOME="/home/${SUDO_USER}"
else
  RUN_USER="$(whoami)"
  RUN_HOME="${HOME}"
fi

# X display + Xauthority (for QTGL preview)
DISPLAY_ENV=":0"
XAUTHORITY_FILE="${RUN_HOME}/.Xauthority"

echo "Setting up systemd service:"
echo "  Service name : ${SERVICE_NAME}"
echo "  Service file : ${SERVICE_FILE}"
echo "  Run user     : ${RUN_USER}"
echo "  App path     : ${APP_FILE}"
echo "  Python       : ${PYTHON_BIN}"
echo "  DISPLAY      : ${DISPLAY_ENV}"
echo "  XAUTHORITY   : ${XAUTHORITY_FILE}"
echo

# ---------- Write systemd service unit ----------

cat > "${SERVICE_FILE}" <<EOF
[Unit]
Description=Raspberry Pi Camera App
After=graphical.target

[Service]
Type=simple
User=${RUN_USER}
WorkingDirectory=${SCRIPT_DIR}
ExecStart=${PYTHON_BIN} ${APP_FILE}
Restart=on-failure
Environment=DISPLAY=${DISPLAY_ENV}
Environment=XAUTHORITY=${XAUTHORITY_FILE}

[Install]
WantedBy=graphical.target
EOF

echo "Service file written to ${SERVICE_FILE}"

# ---------- Enable + start service ----------

systemctl daemon-reload
systemctl enable "${SERVICE_NAME}.service"
systemctl restart "${SERVICE_NAME}.service"

echo
echo "Done!"
echo "Service status:"
systemctl --no-pager status "${SERVICE_NAME}.service" || true
