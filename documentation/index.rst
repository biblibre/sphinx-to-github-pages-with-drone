How to build and publish a Sphinx documentation on GitHub Pages using Drone CI
==============================================================================

To follow this tutorial you must have:

* a GitHub repository containing a Sphinx documentation located in
  ``documentation`` directory at the root of the repository,
* a ``documentation/requirements.txt`` file containing Python dependencies,
* a ``documentation/conf.py`` file containing Sphinx configuration.

Initialize ``gh-pages`` branch
------------------------------

The ``gh-pages`` will contain the generated documentation. We need to create it
and add a few files in it::

    cd /path/to/repo

    # Create an orphan branch (no parent commit) and remove all files
    git checkout --orphan gh-pages
    git rm -rf .

    # Tell Github to not try to build our documentation
    touch .nojekyll

    # Optional, but can be useful to have links to different versions of the
    # documentation (different languages for instances)
    touch index.html

    git add .nojekyll index.html
    git commit -m "Initial commit"
    git push origin gh-pages

As an example, you can put the following content in ``index.html``::

    <!DOCTYPE html>
    <html>
        <head>
            <title>MyRepo user manual</title>
        </head>
        <body>
            <h1>MyRepo user manual</h1>

            <ul>
                <li><a href="en/">English</a></li>
                <li><a href="fr/">French</a></li>
            </ul>
        </body>
    </html>

Create a mirror on git.biblibre.com
-----------------------------------

Since our Drone instance only works on git.biblibre.com, we need to create a
mirror repository there.

#. Go to https://git.biblibre.com
#. Click on the ``+`` sign in the top right corner and then ``New migration``
#. Choose ``GitHub``
#. Enter your repository URL and check ``This repository will be a mirror``
#. Choose the right owner and repository name
#. Click the ``Migrate repository`` button

Create a GitHub deploy key
--------------------------

Drone will need to push to the GitHub repository. We need a deploy key for
that. It's an SSH key that will be granted write access only for this
repository.

#. Generate an SSH keys pair::

    ssh-keygen -f /tmp/github_deploy_key -t ed25519 -C drone+myrepo@biblibre.com

#. Go to github repository's settings page and click on ``Deploy keys`` (or go
   directly to ``https://github.com/<USER>/<REPO>/settings/keys``)
#. Click on ``Add a deploy key``
#. Enter a title
#. Copy the **public** key into the text area
#. Check ``Allow write access``

Configure Drone
---------------

#. Go to https://drone.biblibre.com
#. Click on ``SYNC``
#. Once the synchronisation is done, search your module and click on ``Activate``
#. In the settings, check ``Disable pull requests`` and ``Disable forks``
#. Click on ``Save``
#. In the ``Secrets`` section, enter ``GH_DEPLOY_KEY`` in the ``Secret Name``
   input, and copy the **private** key into the ``Secret Value`` input.
#. Leave the ``Allow pull requests`` checkbox **unchecked**.
#. Click on ``Add a secret``.

Add Drone configuration to your repository
------------------------------------------

In your repository's main branch, add the following files:

.. code-block:: yaml
    :caption: ``.drone.yml``

    ---
    kind: 'pipeline'
    type: 'docker'
    name: 'documentation'
    steps:
      - name: 'build'
        image: 'python:3'
        commands:
          - 'sh .drone/documentation-build.sh'
      - name: 'push'
        image: 'alpine'
        commands:
          - 'apk add git openssh'
          - 'sh .drone/documentation-push.sh'
        environment:
          GH_DEPLOY_KEY:
            from_secret: 'GH_DEPLOY_KEY'
    trigger:
      branch:
        - 'master'
      event:
        - 'push'


.. code-block:: sh
    :caption: ``.drone/documentation-build.sh``

    #!/bin/sh

    cd "$(dirname -- "$(dirname -- "$(readlink -f -- "$0")")")/documentation"
    pip install -r requirements.txt
    languages="en fr"
    for language in $languages; do
        make -e BUILDDIR=_build/$language SPHINXOPTS="-D language=$language" clean html
    done

.. code-block:: sh
    :caption: .drone/documentation-push.sh

    #!/bin/sh

    unset GIT_AUTHOR_NAME
    unset GIT_AUTHOR_EMAIL
    unset GIT_AUTHOR_DATE
    unset GIT_COMMITTER_NAME
    unset GIT_COMMITTER_EMAIL
    unset GIT_COMMITTER_DATE

    git config --global user.email "drone@biblibre.com"
    git config --global user.name "Drone CI"

    mkdir -p ~/.ssh
    printenv GH_DEPLOY_KEY > ~/.ssh/deploy_key
    chmod 600 ~/.ssh/deploy_key
    cat > ~/.ssh/config << 'CONFIG'
    Host github.com
    User git
    IdentityFile ~/.ssh/deploy_key
    StrictHostKeyChecking accept-new
    CONFIG

    cd "$(mktemp -d)"
    git clone --branch gh-pages git@github.com:<USER>/<REPO>.git .

    languages="en fr"
    for language in $languages; do
        rm -rf $language
        cp -r "$DRONE_WORKSPACE/documentation/_build/$language/html" $language
        git add $language
    done
    git commit -m "Drone build: $DRONE_BUILD_NUMBER" -m "Triggered-by: $DRONE_COMMIT_SHA"

    git push origin gh-pages

.. warning:: Do not forget to replace <USER> and <REPO> by the correct values

Set the execution flag for shell scripts::

    chmod +x .drone/*.sh

Then commit and push::

    git add .drone.yml .drone/*.sh
    git commit -m 'Add Drone files to automatically build documentation'
    git push origin master

Test it!
--------

Everything is ready and the documentation should be automatically built when
the mirror on git.biblibre.com get synchronized (once every 8 hours by
default).

But you can test right now by manually triggering the synchronization. This
option can be found in the mirror repository's settings.
