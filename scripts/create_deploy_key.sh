#!/usr/bin/env bash

# Set the default key name and passphrase


KEY_NAME="id_ed25519"


PASSPHRASE="my passphrase"

# Check if the SSH directory exists, if not create it
if [ ! -d "$HOME/.ssh" ]; then
  mkdir "$HOME/.ssh"
  chmod 700 "$HOME/.ssh"
fi

# Generate the key and save it to the specified file
ssh-keygen -t ed25519 -C "charlskenno@gmail.com" -f "$HOME/.ssh/$KEY_NAME" -N ""

# Set the permissions on the key file
chmod 600 "$HOME/.ssh/$KEY_NAME"

# Output the public key for easy copying and pasting
echo "Your public key is:"
cat "$HOME/.ssh/$KEY_NAME.pub"