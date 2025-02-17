#/bin/bash


echo "deleting https://id.acdh.oeaw.ac.at/pez-briefe/vol-01-2010 from ${ARCHE}"
docker run --rm \
  --network="host" \
  --entrypoint arche-delete-resource \
  acdhch/arche-ingest \
  "https://id.acdh.oeaw.ac.at/pez-briefe/vol-01-2010" ${ARCHE} ${ARCHE_USER} ${ARCHE_PASSWORD} --references
  
echo "deleting https://id.acdh.oeaw.ac.at/pez-briefe/vol-02-2015 from ${ARCHE}"
docker run --rm \
  --network="host" \
  --entrypoint arche-delete-resource \
  acdhch/arche-ingest \
  "https://id.acdh.oeaw.ac.at/pez-briefe/vol-02-2015" ${ARCHE} ${ARCHE_USER} ${ARCHE_PASSWORD} --references
  
echo "deleting https://id.acdh.oeaw.ac.at/pez-briefe/pez-letters.rng from ${ARCHE}"
docker run --rm \
  --network="host" \
  --entrypoint arche-delete-resource \
  acdhch/arche-ingest \
  "https://id.acdh.oeaw.ac.at/pez-briefe/pez-letters.rng" ${ARCHE} ${ARCHE_USER} ${ARCHE_PASSWORD} --references

if [ "${TITLEIMAGE}" != "" ] ; then
  echo "deleting ${TITLEIMAGE} from ${ARCHE}"
  docker run --rm \
    --network="host" \
    --entrypoint arche-delete-resource \
    acdhch/arche-ingest \
    ${TITLEIMAGE} ${ARCHE} ${ARCHE_USER} ${ARCHE_PASSWORD}
fi

if [ "${PROJECTID}" != "" ] ; then
  echo "deleting ${PROJECTID} from ${ARCHE}"
  docker run --rm \
    --network="host" \
    --entrypoint arche-delete-resource \
    acdhch/arche-ingest \
    ${PROJECTID} ${ARCHE} ${ARCHE_USER} ${ARCHE_PASSWORD}  --references
fi

echo ""
echo "delete ${TOPCOLID} from ${ARCHE}"
docker run --rm \
  --network="host" \
  --entrypoint arche-delete-resource \
  acdhch/arche-ingest \
  ${TOPCOLID} ${ARCHE} ${ARCHE_USER} ${ARCHE_PASSWORD} --recursively