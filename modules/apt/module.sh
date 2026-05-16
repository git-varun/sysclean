module_name() {
  echo "apt"
}

module_description() {
  echo "APT package cleanup module"
}

module_risk() {
  echo "medium"
}

module_scan() {
  apt list --installed 2>/dev/null
}

module_plan() {
  sudo apt autoremove --dry-run
}

module_execute() {
  sudo apt autoremove --purge -y
}

module_verify() {
  dpkg -l
}

module_rollback() {
  echo "APT rollback not yet implemented"
}