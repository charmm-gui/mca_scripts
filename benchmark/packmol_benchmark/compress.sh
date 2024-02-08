#!/bin/bash
# compresses the full packmol output and leaves only the tail uncompressed

for dir in test_*/; do
    pushd "$dir" >/dev/null

    if [[ ! -e pack.full.tgz && -e pack.out ]]; then
        echo compressing $1

        tail pack.out > pack.tail
        tar czf pack.full.tgz pack.out
        mv pack.tail pack.out
    fi

    popd >/dev/null
done
