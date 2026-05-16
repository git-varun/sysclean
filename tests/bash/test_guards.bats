#!/usr/bin/env bats

load "../../lib/guards.sh"

@test "is_protected_path detects .ssh" {
  run is_protected_path "$HOME/.ssh/id_rsa"
  [ "$status" -eq 0 ]
}

@test "is_protected_path detects .gnupg" {
  run is_protected_path "$HOME/.gnupg/pubring.kbx"
  [ "$status" -eq 0 ]
}

@test "is_protected_path allows normal paths" {
  run is_protected_path "$HOME/Downloads/test.txt"
  [ "$status" -eq 1 ]
}

@test "validate_environment does not exit if not root and python3 exists" {
  run validate_environment
  [ "$status" -eq 0 ]
}
