#!/bin/bash

if [ "$0" != "-bash" ]; then
    echo "ERROR: run with source not sh"
    echo "usage: source setup.sh"
exit
fi

python3 -m venv env/dev


devdir=$( dirname $( dirname $VIRTUAL_ENV ) )

post_activate_path=env/dev/bin/postactivate

echo '#!/bin/bash' >> $post_activate_path
echo 'PYTHONPATH=${PYTHONPATH}:'"$devdir" >> $post_activate_path

. env/dev/bin/activate

pip install -r requirements.txt
