_sysclean_completions() {
  local commands

  commands="clean analyze doctor report queue rollback"

  COMPREPLY=( $(compgen -W "$commands" -- "${COMP_WORDS[1]}") )
}

complete -F _sysclean_completions sysclean