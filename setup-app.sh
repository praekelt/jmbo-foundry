#!/bin/bash

# Add new sites or upgrade them if they already exist. This script is idempotent.
#
# There are levels of operation. Level 1 is quickest since it just updates the
# code and restarts. Level 3 is slowest since it cleans out existing code and
# does a buildout and restart.
#
# 1: Update source code. No buildout.
# 2: Update source code. Buildout.
# 3: Remove existing source code and update. Buildout.

# Default values
USER=www-data
LEVEL=1

# Parse arguments
while getopts "p:d:r:b:u:l:" opt; do
    case $opt in
        p)
            PREFIX=$OPTARG;;
        d)
            DEPLOY_TYPE=$OPTARG;;
        r)
            REPO=$OPTARG;;
        b)
            BRANCH=$OPTARG;;
        u)
            USER=$OPTARG;;
        l)
            LEVEL=$OPTARG;;
    esac    
done

if [[ -z "$PREFIX" || -z "$DEPLOY_TYPE" || -z "$REPO" || -z "$BRANCH" ]];
then
    echo "Usage: upgrade.sh -p (prefix) -d (deploy_type) -r (repo) -b (branch) [-u (user) -l (level)]"
    exit 1
fi

# Checkout / update repo to /tmp
cd /tmp
if [ -d $REPO ]; then
    cd $REPO
    git checkout $BRANCH
    git pull
else
    git clone -b $BRANCH https://praekeltdeploy:g55trw7th@github.com/praekelt/$REPO.git
fi

# Stop processes
for f in `ls /tmp/${REPO}/${DEPLOY_TYPE}_*.cfg`
do
    FILENAME=$(basename $f)
    if [ $FILENAME != "${DEPLOY_TYPE}_base.cfg" ]; then
        # Calculate directory name. Also name of script.
        FTMP=${FILENAME%.*}
        THEDIR=$PREFIX-${FTMP//_/-}

        sudo supervisorctl stop ${THEDIR}.gunicorn
    fi    
done

# Create database. Safe to run even if database already exists.
DB_NAME=${PREFIX}_${DEPLOYTYPE}
echo "CREATE USER $DB_NAME WITH PASSWORD '$DB_NAME'" | sudo -u postgres psql
echo "CREATE DATABASE $DB_NAME WITH OWNER $DB_NAME ENCODING 'UTF8'" | sudo -u postgres psql

# Checkouts
INDEX=0
for f in `ls /tmp/${REPO}/${DEPLOY_TYPE}_*.cfg`
do
    FILENAME=$(basename $f)
    if [ $FILENAME != "${DEPLOY_TYPE}_base.cfg" ]; then
        # Calculate directory name. Also name of script.
        FTMP=${FILENAME%.*}
        THEDIR=$PREFIX-${FTMP//_/-}

        # Clone, bootstrap, buildout
        cd /var/praekelt/
        IS_NEW=0
        if [ -d $THEDIR ]; then
            cd $THEDIR
            if [ $LEVEL == 3 ]; then
                sudo -u $USER rm -rf src
                sudo -u $USER rm -rf $PREFIX
            fi
            sudo -u $USER git checkout $BRANCH
            sudo -u $USER git pull
        else
            IS_NEW=1
            sudo -u $USER git clone -b $BRANCH https://praekeltdeploy:g55trw7th@github.com/praekelt/$REPO.git $THEDIR
            cd $THEDIR
            sudo chown -R $USER:$USER .git/
        fi

        # Always re-bootstrap in case of a new version of distribute
        sudo -u $USER ../python/bin/python bootstrap.py

        if [[ $IS_NEW == 1 || $LEVEL -ge 2 ]]; then
            sudo -u $USER ./bin/buildout -Nv -c $FILENAME
        fi

        # Database setup on first loop
        if [ $INDEX == 0 ]; then
            read -p "Create a superuser if prompted. Do not generate default content. [enter]" y
            sudo -u $USER ./bin/$THEDIR syncdb
            sudo -u $USER ./bin/$THEDIR migrate
            sudo -u $USER ./bin/$THEDIR loaddata src/jmbo-foundry/foundry/fixtures/photosizes.json
            sudo -u $USER ./bin/$THEDIR loaddata src/jmbo-post/post/fixtures/photosizes.json
            sudo -u $USER ./bin/$THEDIR loaddata src/jmbo-gallery/gallery/fixtures/photosizes.json
            sudo -u $USER ./bin/$THEDIR loaddata src/jmbo/jmbo/fixtures/photosizes.json
        fi

        sudo -u $USER rm -rf static
        sudo -u $USER ./bin/$THEDIR collectstatic --noinput

        # Create nginx symlink if required
        sudo ln -s /var/praekelt/${THEDIR}/nginx/gunicorn-${THEDIR}.conf /etc/nginx/sites-enabled/

        # Create supervisor symlink if required
        sudo ln -s /var/praekelt/${THEDIR}/supervisor/gunicorn-${THEDIR}.conf /etc/supervisor/conf.d/

        let INDEX++
    fi
done

# Update supervisor
sudo supervisorctl update

# Start processes
for f in `ls /tmp/${REPO}/${DEPLOY_TYPE}_*.cfg`
do
    FILENAME=$(basename $f)
    if [ $FILENAME != "${DEPLOY_TYPE}_base.cfg" ]; then
        # Calculate directory name. Also name of script.
        FTMP=${FILENAME%.*}
        THEDIR=$PREFIX-${FTMP//_/-}

        sudo supervisorctl start ${THEDIR}.gunicorn
    fi    
done

# Restart memcached
sudo /etc/init.d/memcached restart

# Reload nginx
sudo /etc/init.d/nginx reload
