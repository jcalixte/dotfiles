FROM couchdb:3.5.3

# Baked in, not bind-mounted: Coolify does not copy repo files to the host, so a
# bind mount of ./config/local.ini would mount an empty directory instead.
COPY --chown=couchdb:couchdb config/local.ini /opt/couchdb/etc/local.d/10-local.ini
