"""
    starfish-provenance contract

"""
from convex_contracts.convex_contract import ConvexContract


class ProvenanceContract(ConvexContract):

    def __init__(self, convex, name=None):
        ConvexContract.__init__(self, convex, name or 'starfish.provenance', '0.0.1')

        self._source = f'''
            (def provenance-asset {{}})
            (def provenance-owner {{}})
            (defn version [] "{self.version}")
            (defn assert-asset-id [value]
                (when-not (and (blob? value) (== 32 (count (blob value)))) (fail "INVALID" "invalid asset-id"))
            )
            (defn assert-address [value]
                (when-not (address? (address value)) (fail "INVALID" "invalid address"))
            )
            (defn register [asset-id]
                (assert-asset-id asset-id)
                (let [record {{:owner *caller* :timestamp *timestamp*}}]
                    (def provenance-asset
                        (assoc provenance-asset (blob asset-id)
                            (conj (get provenance-asset (blob asset-id))
                            record)
                        )
                    )
                    (def provenance-owner
                        (assoc provenance-owner *caller*
                            (conj (get provenance-owner *caller*)
                            (blob asset-id))
                        )
                    )
                    record
                )
            )
            (defn event-list [asset-id]
                (assert-asset-id asset-id)
                (get provenance-asset (blob asset-id))
            )
            (defn asset-list []
               (keys provenance-asset)
            )
            (defn owner-list [owner-id]
                (assert-address owner-id)
                (get provenance-owner (address owner-id))
            )
            (export asset-list event-list owner-list register version)

'''
