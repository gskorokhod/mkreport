#!/bin/bash

if [ ! -d "./venv" ]; then
  python3 -m venv venv
  ./venv/bin/pip3 install -r ./requirements.txt
fi

CURRENT_DIR=$(pwd)

# Create the mkreport file with dynamic content
cat << EOF > mkreport
#!/bin/bash

PROJECT_DIR=$CURRENT_DIR

\$PROJECT_DIR/venv/bin/python3 \$PROJECT_DIR/main.py
EOF

# Move the mkreport file to the user's local bin
mkdir -p ~/.local/bin
mv mkreport ~/.local/bin/

# Make mkreport executable
chmod +x ~/.local/bin/mkreport

echo "mkreport installed successfully to ~/.local/bin/mkreport."
