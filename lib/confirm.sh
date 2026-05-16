#!/usr/bin/env bash

confirm_destructive() {
  local action="$1"

  echo
  echo "Destructive action detected: $action"
  read -rp "Type DELETE to continue: " response

  [[ "$response" == "DELETE" ]]
}