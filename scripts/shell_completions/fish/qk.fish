# Completions for quikey
# https://github.com/bostrt/quikey/
# Copy this file to /usr/share/fish/vendor_completions.d/

complete -c qk -f -n __fish_is_first_token -a 'start' -d 'Start the quikey daemon'
complete -c qk -f -n __fish_is_first_token -a 'stop' -d 'Stop the quikey daemon'
complete -c qk -f -n __fish_is_first_token -a 'status' -d 'Show a status report'
complete -c qk -f -n __fish_is_first_token -a 'add' -d 'Add a new entry'
complete -c qk -f -n __fish_is_first_token -a 'edit' -d 'Edit an existing entry'
complete -c qk -f -n __fish_is_first_token -a 'ls' -d 'List (all) entries'
complete -c qk -f -n __fish_is_first_token -a 'rm' -d 'Remove an entry'

complete -c qk -f        -l 'help'     -d 'Show a help message and exit'

complete -c qk -f -s 'n' -l 'name'     -d 'Name of quikey phrase' -a "(qk ls | grep '^| ' | cut --d ' ' -f 2 | tail -n '+2')" -n "__fish_seen_subcommand_from add edit rm"
complete -c qk -f -s 't' -l 'tag'      -d 'Optional tag for the phrase'  -n "__fish_seen_subcommand_from add"
complete -c qk -f -s 'p' -l 'phrase'   -d 'The full phrase to add'       -n "__fish_seen_subcommand_from add"
complete -c qk -f        -l 'show-all' -d 'Show all entries'             -n "__fish_seen_subcommand_from ls"
