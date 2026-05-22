run_pipeline() {
  local module_name="$1"
  local module_script="$ROOT_DIR/modules/$module_name/module.sh"

  if [[ ! -f "$module_script" ]]; then
    error "Module $module_name not found at $module_script"
    return 1
  fi

  info "Planning module: $module_name"
  local plan_json
  plan_json=$("$module_script" --plan)

  if [[ -z "$plan_json" ]]; then
    error "Failed to generate plan for $module_name"
    return 1
  fi

  # Basic validation: check if it's JSON and has command
  if ! echo "$plan_json" | grep -q "\"command\""; then
    error "Invalid plan from $module_name: missing command"
    return 1
  fi

  info "Module $module_name plan generated."
  # Optional: show estimated bytes
  local size
  size=$(echo "$plan_json" | grep -oP '"estimated_bytes":\s*\K[0-9]+' || echo 0)
  info "Estimated reclaimable space: $size bytes"

  confirm_destructive "$module_name execution"

  info "Enqueuing $module_name via daemon..."
  if python3 "$ROOT_DIR/python/core/client.py" "$plan_json"; then
    info "Module $module_name enqueued successfully"
  else
    error "Failed to enqueue $module_name"
    return 1
  fi
}