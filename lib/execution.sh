run_pipeline() {
  local module="$1"

  info "Scanning module: $module"
  "${module}_scan"

  info "Planning module: $module"
  "${module}_plan"

  confirm_destructive "$module execution"

  info "Executing module: $module via daemon"
  python3 "$ROOT_DIR/python/executor/client.py" "{\"command\": [\"echo\", \"Executing module: $module via daemon\"]}"

  info "Verifying module: $module"
  "${module}_verify"

  info "Recording execution metadata"
}